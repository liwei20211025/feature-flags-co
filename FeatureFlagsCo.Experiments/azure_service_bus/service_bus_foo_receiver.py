from azure_service_bus.send_consume import AzureReceiver


class FooReceiver(AzureReceiver):
    def handle_body(self, topic, body):
        print("topic: %s" % topic)
        print("received: %s" % body)
