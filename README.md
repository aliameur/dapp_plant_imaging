# DAPP Plant Imaging: Arabidopsis Imaging and Plant Growth API

This project provides a RESTful API for controlling and interacting with the imaging and plant growth system designed
using two Raspberry Pi boards. The devices consist of a camera system that utilizes stepper motors and a linear
actuator to create focus stacked images of the plant Arabidopsis, as well as a modular plant growth chamber that allows
for control of light wavelength, brightness, and temperature as environmental factors. The API is designed to
make plant research more accessible and less costly, by providing a simple and standardized interface for controlling
the devices and accessing the data they generate.

## Stack

- Python 3.10
- Flask
- RabbitMQ
- Raspberry Pi boards
- JavaScript [not yet]
- HTML/CSS
- Canon EDSDK

## Installation

To install the API, follow these steps:

- Clone the project repository from GitHub: `git clone https://github.com/aliameur/dapp_plant_imaging`
- Install the required Python packages: `pip install -r requirements.txt`
- Set up Flask app [instructions to be added here]
- Set up RabbitMQ messaging: [instructions to be added here]

## Structure

webapp/  
├── __init__.py  
├── main/  
├── api/  
│ &nbsp; &nbsp; &nbsp; &nbsp;├── plants/  
│ &nbsp; &nbsp; &nbsp; &nbsp;├── imaging/  
│ &nbsp; &nbsp; &nbsp; &nbsp;├── data/
└── dashboard/

## Current TODOs

- Test rabbitmq with raspberry pi board
- Write imaging endpoints
- Write data endpoints
- Get requirements for dashboard
- Integrate Canon EDSDK

## Limitations and Known Issues

As with any software project, there may be limitations or known issues with the API. Here are some known limitations and
issues:

- [insert limitation/issue here]

