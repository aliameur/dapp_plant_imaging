import pika
from rabbitplant import RabbitPlant
from controller import Controller

rmq = RabbitPlant()
controller = Controller()


def handle_message(message: str):
    try:
        command, plant_id, value = message.split(",", maxsplit=2)
        if command == 'get':
            response = controller.get_current_conditions(plant_id)
        elif command == 'temperature':
            response = controller.set_temperature(plant_id, value)
        elif command == 'wavelength':
            response = controller.set_wavelength(plant_id, value)
        elif command == 'brightness':
            response = controller.set_brightness(plant_id, value)
        elif command == 'new':
            response = controller.new_plant(plant_id, value)
        elif command == "delete":
            response = controller.delete_plant(plant_id)
        elif command == "init":
            response = controller.init_plants(value)
        else:
            response = 'Unexpected request'
        return response
    except Exception as e:
        return e.__str__()


def on_request(ch, method, props, body: bytes):
    message = body.decode()
    # response = handle_message(message)
    response = message + " response"
    print(f" [.] Received {message}")
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)


rmq.start_consuming(on_request)
