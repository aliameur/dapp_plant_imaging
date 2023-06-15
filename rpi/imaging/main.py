import pika
from rabbitimaging import RabbitImaging
from controller import Controller

rmq = RabbitImaging()
controller = Controller()


def handle_message(message: str):
    response = None
    return response


def on_request(ch, method, props, body):
    body = str(body)
    print(f" [.] Received {body, type(body)}")
    response = "hello from imaging"

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


rmq.start_consuming(on_request)
