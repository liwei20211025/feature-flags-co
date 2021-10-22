import logging

from config.config_handling import get_config_value
from opencensus.ext.azure.log_exporter import AzureLogHandler

from azure_service_bus.send_consume import AzureReceiver

p1_logger = logging.getLogger('p1_azure_service_bus_get_expt_recoding_info')
p1_logger.addHandler(AzureLogHandler(
    connection_string=get_config_value('azure', 'insignt_conn_str')))
p1_logger.setLevel(logging.INFO)


class P1AzureGetExptRecordingInfoReceiver(AzureReceiver):
    def handle_body(self, topic, body):
        if type(body) is dict:
            key, end, value = body.get('ExptId', None), body.get(
                'EndExptTime', None), body
            if key:
                p1_logger.info('p1########p1 gets %r#########' % body)
                self.redis_set(key, value)
                if not end:
                    # set up link between ff and his active expts
                    ff_env_id = 'dict_ff_act_expts_%s_%s' % (
                        body['EnvId'], body['FlagId'])
                    self.__setup_relation_between_obj_expt(
                        ff_env_id, body['FlagId'], key)
                    # set up link between event and his active expts
                    event_env_id = 'dict_event_act_expts_%s_%s' % (
                        body['EnvId'], body['EventName'])
                    self.__setup_relation_between_obj_expt(
                        event_env_id, body['EventName'], key)
                    topic = get_config_value('p2', 'topic_Q2')
                    subscription = get_config_value('p2', 'subscription_Q2')
                    self.send(self._bus, topic, subscription, key)
                    p1_logger.info('########p1 send %r to Q2########' % key)

    def __setup_relation_between_obj_expt(self, dict_expt_id, key, expt_id):
        dict_acitveExpts = dict_from_redis if (
            dict_from_redis := self.redis_get(dict_expt_id)) else {}
        list_act_Expts = dict_acitveExpts.get(key, [])
        list_act_Expts.append(expt_id)
        dict_acitveExpts[key] = list_act_Expts
        self.redis_set(dict_expt_id, dict_acitveExpts)
