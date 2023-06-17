# DAPP Plant Imaging: Arabidopsis Imaging and Plant Growth API

This project provides a RESTful API for controlling and interacting with the imaging and plant growth system designed
using two Raspberry Pi boards. This system includes a camera, which utilizes stepper motors and a linear actuator to
create focus stacked images of the plant Arabidopsis, as well as a modular plant growth chamber that controls light
wavelength, brightness, and temperature as environmental factors. The API aims to simplify plant research and make it
less costly by providing a standardized interface for controlling the devices and accessing the data they generate.

The authentication is done via Firebase, RabbitMQ is used as a messaging broker to the Raspberry Pi boards. The plant
board uses a series of PID controllers in a multithreaded fashion. The imaging board uses gphoto2 to control the camera.
The project stores images and data on Google Cloud Storage and Firestore. The project is deployed using Docker-compose,
building two images, one for the Flask app, and one for the RabbitMQ server.

## Tech Stack

- Python 3.10
- Flask
- RabbitMQ
- Raspberry Pi boards
- Firebase for Auth
- Google Cloud Storage and Firestore for data storage
- Docker-compose for deployment

## Installation and Deployment with Docker

To install the API, follow these steps:

1. Clone the project repository from GitHub: `git clone https://github.com/aliameur/dapp_plant_imaging`
2. Navigate into the project directory: `cd dapp_plant_imaging`
3. Build and run the Docker images: `docker-compose up --build -d`

## Structure

webapp/  
├── __init__.py  
├── main/  
├── api/  
│ &nbsp; &nbsp; &nbsp; &nbsp;├── plants/  
│ &nbsp; &nbsp; &nbsp; &nbsp;├── imaging/  
│ &nbsp; &nbsp; &nbsp; &nbsp;├── data/
└── dashboard/

.  
├── flask_app  
│   ├── main.py  
│   ├── config.py  
│   ├── requirements.txt  
│   ├── Dockerfile  
│   ├── firebase-config.json  
│   ├── .env  
│   └── api  
│       ├── __init__.py  
│       ├── controllers.py  
│       ├── models.py  
│       ├── rabbitmq.py  
│       ├── data/  
│       ├── auth/  
│       ├── plants/  
│       └── imaging/  
├── rabbitmq  
│   └── Dockerfile  
├── rpi  
│   ├── imaging/  
│   └── plants/  
└── docker-compose.yml  


## Dashboard

A separate dashboard has been implemented using React to provide a user interface for interacting with the system. The source code for the dashboard can be found [here](https://github.com/aliameur/plant-imaging-dashboard).

## Limitations 

The project is actively being developed. If you encounter any problems or have any suggestions, please open an issue.

## License

This project is licensed under the MIT License.

