# Space Gurion - Flight Computer Sensors

## Introduction
Welcome to the Space Gurion's Flight Computer Sensors repository. This repository contains the code for the sensors used in our student-led rocketry program's flight computer. Our mission is to launch a rocket and gather crucial data during its flight.

## Hardware Requirements
- GPS Module (e.g., Adafruit Ultimate GPS Module)
- IMU Sensor (e.g., MPU-6050 or similar)
- Raspberry Pi or any compatible microcontroller board
- Serial-to-USB converter (for IMU sensor)

## Software Requirements
- Python 3.x
- `adafruit_gps` library for GPS Module
- `serial` library for UART communication
- `numpy` for numerical operations

## Installation
1. Clone the repository:
git clone [[repository URL]](https://github.com/Flight-Computer-space-gurion/Sensors.git)
2. Install required Python libraries:
  pip install pyserial numpy

## Usage

### GPS Sensor
1. Connect the GPS module to your Raspberry Pi or microcontroller.
2. Run the GPS sensor script:
  python gps_sensor.py

### IMU Sensor
1. Connect the IMU sensor to your Raspberry Pi or microcontroller using the Serial-to-USB converter.
2. Run the IMU sensor script:
  python imu_sensor.py


