import logging

from azure_service_bus.send_consume import AzureReceiver

logger = logging.getLogger('p3_azure_service_bus_get_expt_events')
logger.setLevel(logging.INFO)


class P3AzureGetExptFFEventsReceiver(AzureReceiver):
    def handle_body(self, topic, body):
        if type(body) is dict:
            dict_flag_acitveExpts = self.redis_get(
                'dict_ff_act_expts_%s_%s' % (body['EnvId'], body['FeatureFlagId']))
            if dict_flag_acitveExpts and dict_flag_acitveExpts.get(body['FeatureFlagId'], None):
                id = '%s_%s' % (body['EnvId'], body['FeatureFlagId'])
                value = self.redis_get(id)
                list_ff_events = value if value else []
                dict_to_add = {
                    # 'FeatureFlagId': body['FeatureFlagId'],
                    'UserKeyId': body['UserKeyId'],
                    'VariationLocalId': body['VariationLocalId'],
                    'TimeStamp': body['TimeStamp']
                }
                list_ff_events = list_ff_events + [dict_to_add]
                self.redis_set(id, list_ff_events)
                logger.info('Added ff event: %r' % dict_to_add)


class P3AzureGetExptUserEventsReceiver(AzureReceiver):
    def handle_body(self, topic, body):
        if type(body) is dict:
            dict_customEvent_acitveExpts = self.redis_get(
                'dict_event_act_expts_%s_%s' % (body['EnvironmentId'], body['EventName']))
            if dict_customEvent_acitveExpts and dict_customEvent_acitveExpts.get(body['EventName'], None):
                id = '%s_%s' % (body['EnvironmentId'], body['EventName'])
                value = self.redis_get(id)
                list_user_events = value if value else []
                dict_to_add = {
                    # 'EventName': body['EventName'],
                    'UserKeyId': body['User']['FFUserKeyId'],
                    'TimeStamp': body['TimeStamp']
                }
                list_user_events = list_user_events + [dict_to_add]
                self.redis_set(id, list_user_events)
                logger.info('Added user event: %r' % dict_to_add)
