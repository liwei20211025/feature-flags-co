import uuid

P1_NECESSAIRE_KEYS = ['ExptId',
                      'IterationId',
                      'EnvId',
                      'FlagId',
                      'BaselineVariation',
                      'Variations',
                      'EventName',
                      'StartExptTime',
                      'EndExptTime']

P1_OPTIONAL_KEYS = ['EventType',
                    'CustomEventTrackOption',
                    'CustomEventSuccessCriteria',
                    'CustomEventUnit']


P3_FF_EVENT_NECESSAIRE_KEYS = ['EnvId',
                               'FeatureFlagId',
                               'UserKeyId',
                               'VariationLocalId',
                               'TimeStamp']

P3_USER_EVENT_NECESSAIRE_KEYS = ['EnvironmentId',
                                 'User',
                                 'EventName',
                                 'NumericValue',
                                 'TimeStamp']

FMT = '%Y-%m-%dT%H:%M:%S.%f'


def get_azure_instance_id():
    return str(uuid.getnode())


# unit = s
HEALTH_CHECK_TIMEOUT = 210
