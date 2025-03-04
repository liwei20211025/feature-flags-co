import logging
import os
import sys

from azure_service_bus.p2_azure_service_bus_get_expt_result import \
    P2AzureGetExptResultReceiver
from config.config_handling import get_config_value

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%m-%d %H:%M')
    sb_host = get_config_value('azure', 'fully_qualified_namespace')
    sb_sas_policy = get_config_value('azure', 'sas_policy')
    sb_sas_key = get_config_value('azure', 'servicebus_sas_key')
    redis_host = get_config_value('redis', 'redis_host')
    redis_port = get_config_value('redis', 'redis_port')
    redis_passwd = get_config_value('redis', 'redis_passwd')
    topic = get_config_value('p2', 'topic_Q2')
    subscription = get_config_value('p2', 'subscription_Q2')
    try:
        wait_timeout = float(get_config_value('p2', 'wait_timeout'))
        prefetch_count = int(get_config_value('p2', 'prefetch_count'))
    except:
        wait_timeout = 30.0
        prefetch_count = 2
    process_name = ''
    if len(sys.argv) > 1:
        process_name = sys.argv[1]
    else:
        process_name = os.path.basename(__file__)
    P2AzureGetExptResultReceiver(sb_host, sb_sas_policy, sb_sas_key, redis_host, redis_port, redis_passwd, wait_timeout) \
        .consume(process_name=process_name,
                 topic=(topic, subscription),
                 prefetch_count=prefetch_count,
                 is_dlq=False)
