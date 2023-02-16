import socket
import RPi.GPIO as GPIO


def handle_message(message: str):
    command, value, plant_id = message.split(",")
    if command == 'brightness':
        response = set_led(plant_id, value)
    elif command == 'temperature':
        response = set_temp(plant_id, value)
    else:
        response = 'Unexpected request'
    return response


def set_led(plant_id: int, brightness: int) -> str:
    global plants
    led_pin = plants.get(plant_id, default=-1)["led_pin"]
    if led_pin == -1:
        return "Invalid plant ID"

    # Convert brightness percentage to a duty cycle value between 0 and 100
    duty_cycle = brightness / 100.0 * 100

    # Create a PWM object with a frequency of 100 Hz
    p = GPIO.PWM(led_pin, 100)

    # Start the PWM with the duty cycle value
    p.start(duty_cycle)

    # # TODO test with raspberry pi ASAP
    # # Clean up the PWM object and GPIO pin when finished
    # p.stop()
    # GPIO.cleanup(led_pin)

    return f"Brightness set to: {brightness}%"


# TODO write set temp function
def set_temp(plant_id: int, temperature: float) -> str:
    global plants
    heating_pin = plants.get(plant_id, default=-1)["heating_pin"]
    if heating_pin == -1:
        return "Invalid plant ID"

    return f"Temperature set to: {temperature}°C"


GPIO.setmode(GPIO.BCM)
plants = {
    1: {
        'heating_pin': 18,
        'led_pin': 17,
        'heating_status': False,
        'led_brightness': 0
    },
    2: {
        'heating_pin': 23,
        'led_pin': 24,
        'heating_status': False,
        'led_brightness': 0
    }
}
# set pins mode
for plant_id, plant_info in plants.items():
    GPIO.setup(plant_info['heating_pin'], GPIO.OUT)
    GPIO.setup(plant_info['led_pin'], GPIO.OUT)

HOST = '0.0.0.0'
PORT = 8888

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Listening on {HOST}:{PORT}...")

    # Wait for command from computer
    while True:
        try:
            # Accept incoming connection
            conn, addr = s.accept()
            with conn:
                # Receive incoming message
                data = conn.recv(1024).decode()
                if not data:
                    continue
                # Handle incoming message
                response = handle_message(data)
                conn.send(response.encode())
                # TODO make sure return response to computer
        except Exception as e:
            print(f"Error: {e}")
