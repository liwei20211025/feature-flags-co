import logging

from azure_service_bus.constants import (P3_FF_EVENT_NECESSAIRE_KEYS,
                                         P3_USER_EVENT_NECESSAIRE_KEYS)
from azure_service_bus.insight_utils import (get_custom_properties,
                                             get_insight_logger)
from azure_service_bus.send_consume import AzureReceiver

p3_logger = get_insight_logger('p3_azure_service_bus_get_expt_events')
p3_logger.setLevel(logging.INFO)


class P3AzureGetExptFFEventsReceiver(AzureReceiver):
    def handle_body(self, topic, body):
        if type(body) is dict:
            missing_keys = [k for k in P3_FF_EVENT_NECESSAIRE_KEYS if k not in body.keys()]
            if not missing_keys:
                dict_flag_acitveExpts = self.redis_get('dict_ff_act_expts_%s_%s' % (body['EnvId'], body['FeatureFlagId']))
                if dict_flag_acitveExpts and dict_flag_acitveExpts.get(body['FeatureFlagId'], None):
                    id = '%s_%s' % (body['EnvId'], body['FeatureFlagId'])
                    value = self.redis_get(id)
                    list_ff_events = value if value else []
                    dict_to_add = {
                        'UserKeyId': body['UserKeyId'],
                        'VariationLocalId': body['VariationLocalId'],
                        'TimeStamp': body['TimeStamp']
                    }
                    list_ff_events = list_ff_events + [dict_to_add]
                    self.redis_set(id, list_ff_events)
                    p3_logger.info('ADD FF EVENT', extra=get_custom_properties(**dict_to_add))
                else:
                    body['reason'] = 'EVENT NOT FOUND'
                    p3_logger.warning('EVENT IGNOR', extra=get_custom_properties(**body))
            else:
                body['reason'] = 'UNVALID FORMAT'
                body['missing_keys'] = missing_keys
                p3_logger.warning('EVENT IGNOR', extra=get_custom_properties(**body))
        else:
            p3_logger.warning('EVENT IGNOR', extra=get_custom_properties(reason='FORBIDDEN INPUT'))


class P3AzureGetExptUserEventsReceiver(AzureReceiver):
    def handle_body(self, topic, body):
        if type(body) is dict:
            missing_keys = [k for k in P3_USER_EVENT_NECESSAIRE_KEYS if k not in body.keys()]
            if not missing_keys:
                dict_customEvent_acitveExpts = self.redis_get(
                    'dict_event_act_expts_%s_%s' % (body['EnvironmentId'], body['EventName']))
                if dict_customEvent_acitveExpts and dict_customEvent_acitveExpts.get(body['EventName'], None):
                    id = '%s_%s' % (body['EnvironmentId'], body['EventName'])
                    value = self.redis_get(id)
                    list_user_events = value if value else []
                    dict_to_add = {
                        'UserKeyId': body['User']['FFUserKeyId'],
                        'NumericValue': body['NumericValue'],
                        'TimeStamp': body['TimeStamp']
                    }
                    list_user_events = list_user_events + [dict_to_add]
                    self.redis_set(id, list_user_events)
                    p3_logger.info('ADD USER EVENT', extra=get_custom_properties(**dict_to_add))
                else:
                    body['reason'] = 'EVENT NOT FOUND'
                    p3_logger.warning('EVENT IGNOR', extra=get_custom_properties(**body))
            else:
                body['reason'] = 'UNVALID FORMAT'
                body['missing_keys'] = missing_keys
                p3_logger.warning('EVENT IGNOR', extra=get_custom_properties(**body))
        else:
            p3_logger.warning('EVENT IGNOR', extra=get_custom_properties(reason='FORBIDDEN INPUT'))
