import pika
from rabbitplant import RabbitPlant
from controller import Controller

rmq = RabbitPlant()
controller = Controller()


def handle_message(message: str):
    global controller
    command, plant_id, value = message.split(",")
    if command == 'get':
        response = controller.get_current_conditions(plant_id)
    elif command == 'temp':
        response = controller.set_temp(plant_id, value)
    elif command == 'wavelength':
        response = controller.set_wavelength(plant_id, value)
    elif command == 'brightness':
        response = controller.set_brightness(plant_id, value)
    else:
        response = 'Unexpected request'
    return response


def on_request(ch, method, props, body):
    body = str(body)
    print(f" [.] Received {body}")
    response = "Hello from plant"

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


rmq.start_consuming(on_request)
