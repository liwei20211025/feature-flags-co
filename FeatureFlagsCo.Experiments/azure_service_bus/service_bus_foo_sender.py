import logging
from azure_service_bus.send_consume import AzureSender

CONNECTION_STR = 'Endpoint=sb://ffc-ce2-dev.servicebus.chinacloudapi.cn/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=zd326D36R1rvT50CcFQ51wAu9+2vH0MlUA67rezo5G0='
TOPIC_NAME = 'ds'
ORIGIN = 'py'
Q1_START = {
    "ExptId": 'FF__38__48__103__PayButton_exp1',
    "IterationId": "2",
    "EnvId": "103",
    "FlagId": "FF__38__48__103__PayButton",
    "BaselineVariation": "1",
    "Variations": ["1", "2", "3"],
    "EventName": "ButtonPayTrack",
    "StartExptTime": "2021-09-20T21:00:00.123456",
    "EndExptTime": ""
}

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%m-%d %H:%M')
    AzureSender(CONNECTION_STR).send(None, TOPIC_NAME, ORIGIN, Q1_START)
