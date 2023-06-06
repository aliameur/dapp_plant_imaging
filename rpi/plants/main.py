import pika
from rabbitplant import RabbitPlant
from controller import Controller

rmq = RabbitPlant()
controller = Controller()


def handle_message(message: str):
    command, plant_id, value = message.split(",", maxsplit=2)
    if command == 'get':
        response = controller.get_current_conditions(plant_id)
    elif command == 'temperature':
        response = controller.set_temp(plant_id, value)
    elif command == 'wavelength':
        response = controller.set_wavelength(plant_id, value)
    elif command == 'brightness':
        response = controller.set_brightness(plant_id, value)
    else:
        response = 'Unexpected request'
    return response


def on_request(ch, method, props, body: bytes):
    message = body.decode()
    response = handle_message(message)
    response = message
    print(f" [.] Received {message}")
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)


rmq.start_consuming(on_request)
