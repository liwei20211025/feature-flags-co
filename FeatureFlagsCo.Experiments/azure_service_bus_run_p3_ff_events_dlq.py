import logging
import os
import sys

from azure_service_bus.p3_azure_service_bus_get_expt_events import \
    P3AzureGetExptFFEventsReceiver
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
    topic = get_config_value('p3', 'topic_Q4')
    subscription = get_config_value('p3', 'subscription_Q4')
    try:
        prefetch_count = int(get_config_value('p3', 'prefetch_count'))
    except:
        prefetch_count = 10
    process_name = ''
    if len(sys.argv) > 1:
        process_name = sys.argv[1]
    else:
        process_name = os.path.basename(__file__)
    P3AzureGetExptFFEventsReceiver(sb_host, sb_sas_policy, sb_sas_key, redis_host, redis_port, redis_passwd) \
        .consume(process_name=process_name,
                 topic=(topic, subscription),
                 prefetch_count=prefetch_count,
                 is_dlq=False)
