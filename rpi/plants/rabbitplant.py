import pika


class RabbitPlant:

    def __init__(self):
        self.username = "rabbitmq"
        self.password = "rabbitmq"
        self.host = "localhost"
        self.port = 5672

        self._init_rmq()

    def _init_rmq(self):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.parameters = pika.ConnectionParameters(self.host,
                                                    self.port,
                                                    "/",
                                                    credentials=self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='plant')

    def start_consuming(self, on_message_callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='plant', on_message_callback=on_message_callback)
        print(" [x] Plants Board Awaiting RPC requests")
        self.channel.start_consuming()
