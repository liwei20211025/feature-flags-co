import logging
from azure_service_bus.service_bus_foo_receiver import FooReceiver

CONNECTION_STR = 'Endpoint=sb://ffc-ce2-dev.servicebus.chinacloudapi.cn/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=zd326D36R1rvT50CcFQ51wAu9+2vH0MlUA67rezo5G0='
TOPIC_NAME = 'ds'
SUBSCRIPTION_NAME = 'py'

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%m-%d %H:%M')
    FooReceiver(CONNECTION_STR).consume(
        (TOPIC_NAME, SUBSCRIPTION_NAME), is_dlq=True)
