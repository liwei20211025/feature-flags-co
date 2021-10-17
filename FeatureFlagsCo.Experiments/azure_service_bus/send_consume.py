
from abc import ABC
import abc
import json
import logging
import os
import sys
import time
from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusSender, ServiceBusReceiver
from azure.servicebus._common.constants import ServiceBusSubQueue

from azure.servicebus.exceptions import MessageAlreadySettled, MessageLockLostError, MessageNotFoundError, MessageSizeExceededError, OperationTimeoutError, ServiceBusAuthenticationError, ServiceBusAuthorizationError, ServiceBusCommunicationError, ServiceBusConnectionError, ServiceBusError
import redis

TO_DO_NUM = '500'

logger = logging.getLogger('send_consume')
logger.setLevel(logging.INFO)

# The logging levels below may need to be changed based on the logging that you want to suppress.
uamqp_logger = logging.getLogger('uamqp')
uamqp_logger.setLevel(logging.ERROR)

# or even further fine-grained control, suppressing the warnings in uamqp.connection module
uamqp_connection_logger = logging.getLogger('uamqp.connection')
uamqp_connection_logger.setLevel(logging.ERROR)


class AzureServiceBus:
    def __init__(self,
                 conn_str,
                 redis_host='localhost',
                 redis_port=6379,
                 redis_passwd=''):
        self._conn_str = conn_str
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._redis_passwd = redis_passwd
        self._init__redis_connection(
            redis_host, redis_port, redis_passwd)

    def _init__redis_connection(self, host, port, password):
        try:
            ssl = True if int(port) == 6380 else False
        except:
            ssl = False
        self._redis = redis.Redis(
            host=host,
            port=port,
            password=password,
            ssl=ssl)

    @property
    def redis(self) -> redis.Redis:
        return self._redis

    def redis_get(self, id):
        value = self.redis.get(id)
        return json.loads(value.decode()) if value else None

    def redis_set(self, id, value):
        self.redis.set(id, str.encode(json.dumps(value)))

    def redis_del(self, *id):
        self.redis.delete(*id)


class AzureSender(AzureServiceBus):

    def send(self, bus: ServiceBusClient, topic: str, origin: str, *messages):

        def send_batch_messages(sender: ServiceBusSender, topic, origin, *msgs):
            batch_message = sender.create_message_batch()
            for msg in msgs:
                try:
                    message = ServiceBusMessage(json.dumps(
                        msg), subject=topic, application_properties={'origin': origin})
                except TypeError:
                    # Message body is of an inappropriate type, must be string, bytes or None.
                    continue
                try:
                    batch_message.add_message(message)
                except MessageSizeExceededError:
                    # ServiceBusMessageBatch object reaches max_size.
                    # New ServiceBusMessageBatch object can be created here to send more data.
                    # This must be handled at the application layer, by breaking up or condensing.
                    continue
            last_error = None
            for _ in range(3):  # Send retries
                try:
                    sender.send_messages(batch_message)
                    last_error = None
                    return
                except MessageSizeExceededError:
                    # The body provided in the message to be sent is too large.
                    # This must be handled at the application layer, by breaking up or condensing.
                    logger.exception(
                        "The body provided in the message to be sent is too large")
                    break
                except ServiceBusError as e:
                    # Other types of service bus errors that can be handled at the higher level, such as connection/auth errors
                    # If it happens persistently, should bubble up, and should be logged/alerted if high volume.
                    last_error = e
                    continue
            if last_error:
                raise last_error
        if not bus:
            bus = ServiceBusClient.from_connection_string(
                conn_str=self._conn_str, logging_enable=True)
            with bus:
                sender = bus.get_topic_sender(topic_name=topic)
                with sender:
                    send_batch_messages(sender, topic, origin, *messages)
        else:
            sender = bus.get_topic_sender(topic_name=topic)
            with sender:
                send_batch_messages(sender, topic, origin, *messages)
        logger.info(
            f'send to topic: {topic}, origin: {origin}, num of message: {len(messages)}')


class AzureReceiver(ABC, AzureSender):

    @abc.abstractmethod
    def handle_body(self, topic, body):
        pass

    def consume(self, topic=(), connection_retries=3, settlement_retries=3, is_dlq=False):

        def receive_message(receiver: ServiceBusReceiver, settlement_retries=3, is_dlq=False):
            if is_dlq:
                logger.info("#######dlq receiver#######")
            else:
                logger.info("#######normal receiver#######")
            should_retry = True
            while should_retry:
                try:
                    for msg in receiver:
                        last_error = None
                        try:
                            # Do your application-specific data processing here
                            # self.handle_body(msg.subject, json.loads(str(msg)))
                            self.handle_body(msg.subject, json.loads(str(msg)))
                            should_complete = True
                        except ServiceBusError:
                            logger.exception(
                                "Maybe error in send message, retrying to connect...")
                            raise
                        except redis.RedisError as e:
                            logger.exception('redis error')
                            last_error = e
                            should_complete = False
                        except Exception as e:
                            logger.exception(
                                f'Application level error in {msg.subject}')
                            last_error = e
                            should_complete = False

                        for _ in range(settlement_retries):  # Settlement retry
                            try:
                                if should_complete:
                                    receiver.complete_message(msg)
                                else:
                                    # Depending on the desired behavior, one could dead letter on failure instead; failure modes are comparable.
                                    # Abandon returns the message to the queue for another consumer to receive, dead letter moves to the dead letter subqueue.
                                    # maybe put the message into dead_letter_queue
                                    if isinstance(last_error, redis.RedisError):
                                        if not self.redis.ping():
                                            self._init__redis_connection(self._redis_host,
                                                                         self._redis_port,
                                                                         self._redis_passwd)
                                        receiver.abandon_message(msg)
                                    elif is_dlq:
                                        # messages will be handled later
                                        # save them in redis
                                        id = f'{msg.subject}_py_deferred_sequenced_numbers'
                                        if not (deferred_sequenced_numbers := self.redis_get(id)):
                                            deferred_sequenced_numbers = []
                                        deferred_sequenced_numbers.append(
                                            msg.sequence_number)
                                        self.redis_set(
                                            id, deferred_sequenced_numbers)
                                        receiver.defer_message(msg)
                                    else:
                                        receiver.dead_letter_message(
                                            msg, reason=TO_DO_NUM, error_description='Application level failure')

                                break
                            except (MessageAlreadySettled, MessageLockLostError, MessageNotFoundError):
                                # Message was already settled, either somewhere earlier in this processing or by another node.  Continue.
                                # Message lock was lost before settlement.  Handle as necessary in the app layer for idempotency then continue on.
                                # Message has an improper sequence number, was dead lettered, or otherwise does not exist.  Handle at app layer, continue on.
                                logger.exception(
                                    'message settled or lost or not found')
                                break
                            except ServiceBusError:
                                # Any other undefined service errors during settlement.  Can be transient, and can retry, but should be logged, and alerted on high volume.
                                logger.exception(
                                    'undefined service errors during settlement, retrying...')
                                continue
                    return
                except ServiceBusError:
                    # some service bus error in connection that can be handled at the higher level, such as connection/auth errors
                    raise
                except BaseException as e:
                    # Although miscellaneous service errors and interruptions can occasionally occur during receiving,
                    # In most pragmatic cases one can try to continue receiving unless the failure mode seens persistent.
                    # Logging the associated failure and alerting on high volume is often prudent.
                    if isinstance(e, KeyboardInterrupt):
                        raise
                    logger.exception(
                        'service errors and interruptions occasionally occur during receiving, trying to fetch next message...')
                    continue

        self._bus = ServiceBusClient.from_connection_string(
            conn_str=self._conn_str, logging_enable=True)
        for _ in range(connection_retries):  # Connection retries.
            try:
                logger.info('################opening...################')
                with self._bus:
                    if topic:
                        topic_name, subscription = topic
                        receiver = self._bus.get_subscription_receiver(topic_name=topic_name, subscription_name=subscription) if not is_dlq else self._bus.get_subscription_receiver(
                            topic_name=topic_name, subscription_name=subscription, sub_queue=ServiceBusSubQueue.DEAD_LETTER)
                    else:
                        try:
                            sys.exit(0)
                        except SystemExit:
                            os._exit(0)
                    with receiver:
                        logger.info(
                            f'########topic: {topic_name}, subscription: {subscription}########')
                        receive_message(
                            receiver, settlement_retries=settlement_retries, is_dlq=is_dlq)
            except ServiceBusError:
                logger.exception(
                    'An error occurred in service bus level, retrying to connect...')
                time.sleep(10)
                continue
            except KeyboardInterrupt:
                logger.info('#######Interrupted#########')
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
            except:
                logger.exception('#######unexpected#########')

        try:
            logger.warning('application quits...')
            sys.exit(1)
        except SystemExit:
            os._exit(1)
