import logging

from config.config_handling import get_config_value
from opencensus.ext.azure.log_exporter import AzureLogHandler

from azure_service_bus.send_consume import AzureReceiver

foo_logger = logging.getLogger('service_bus_foo_receiver')
foo_logger.addHandler(AzureLogHandler(
    connection_string=get_config_value('azure', 'insignt_conn_str')))
foo_logger.setLevel(logging.INFO)


class FooReceiver(AzureReceiver):
    def handle_body(self, topic, body):
        foo_logger.info("topic: %s" % topic)
        foo_logger.info("received: %s" % body)
