import pika


class RabbitImaging:

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
        self.channel.queue_declare(queue='imaging')

    def start_consuming(self, on_message_callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='imaging', on_message_callback=on_message_callback)
        print(" [x] Imaging Board Awaiting RPC requests")
        self.channel.start_consuming()
