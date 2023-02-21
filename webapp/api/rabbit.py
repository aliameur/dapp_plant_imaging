import pika


class RabbitMQ:

    def __init__(self, username: str, password: str, host: str, port: int, exchange: str, routing_key: str):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.exchange = exchange
        self.routing_key = routing_key
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            self.host, self.port, '/', credentials, heartbeat=0
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange=self.exchange, exchange_type='direct', durable=True
        )

    def send_message(self, message):
        if not self.connection or self.connection.is_closed:
            self.connect()

        self.channel.basic_publish(
            exchange=self.exchange, routing_key=self.routing_key, body=message
        )

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
