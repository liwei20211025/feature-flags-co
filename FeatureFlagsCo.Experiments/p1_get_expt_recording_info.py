import json
import os
import sys
import logging

from rabbitmq.rabbitmq import RabbitMQConsumer, RabbitMQSender


class P1GetExptRecordingInfoConsumer(RabbitMQConsumer):

    def __setup_relation_between_obj_expt(self, dict_expt_id, key, expt_id):
        dict_from_redis = self.redis_get(dict_expt_id)
        dict_acitveExpts = dict_from_redis if dict_from_redis else {}
        list_act_Expts = dict_acitveExpts.get(key, [])
        list_act_Expts.append(expt_id)
        dict_acitveExpts[key] = list
        self.redis_set(dict_expt_id, dict_acitveExpts)

    def handle_body(self, body, **properties):
        if type(body) is dict:
            key, end, value = body.get('ExptID', None), body.get(
                'EndExptTime', None), body
            if key:
                if not end:
                    # set up link between ff and his active expts
                    ff_env_id = 'dict_ff_act_expts_%s_%s' % (
                        body['EnvId'], body['Flag']['Id'])
                    self.__setup_relation_between_obj_expt(
                        ff_env_id, body['Flag']['Id'], key)
                    # set up link between event and his active expts
                    event_env_id = 'dict_event_act_expts_%s_%s' % (
                        body['EnvId'], body['EventName'])
                    self.__setup_relation_between_obj_expt(
                        event_env_id, body['EventName'], key)
                    jsons = [key]
                    RabbitMQSender() \
                        .send(topic='Q2', routing_key='py.experiments.experiment', *jsons)

                self.redis_set(key, value)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%m-%d %H:%M')
    while True:
        try:
            P1GetExptRecordingInfoConsumer().consumer(
                'py.experiments.recordinginfo', ('Q1', []))
            break
        except KeyboardInterrupt:
            logging.info('#######Interrupted#########')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception as e:
            logging.exception('#######unexpected#########')
