import os
import pika
import uuid
from dotenv import load_dotenv

load_dotenv()
MAX_TIMEOUT = os.environ.get("MAX_TIMEOUT", 10)


class RabbitMQ:

    def __init__(self):
        self.credentials = self.parameters = None
        self.connection = self.channel = None
        self.callback_queue = self.response = self.corr_id = None

    def init_app(self, current_app):
        self.credentials = pika.PlainCredentials(current_app.config.get("RABBIT_USER"),
                                                 current_app.config.get("RABBIT_PASS"))
        self.parameters = pika.ConnectionParameters(current_app.config.get("RABBIT_HOST"),
                                                    current_app.config.get("RABBIT_PORT"),
                                                    "/",
                                                    credentials=self.credentials,
                                                    heartbeat=0)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response: bytes | None = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, queue: str, message: str) -> bytes | None:
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=message)
        self.connection.process_data_events(time_limit=10)
        return self.response
