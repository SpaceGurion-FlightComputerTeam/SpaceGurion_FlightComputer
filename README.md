# SpaceGurion Flight Computer

## Project Overview
This project is developed by the **Flight Computer** team as part of the SpaceGurion initiative. Its purpose is to handle, stream, analyze, and visualize telemetry data collected during rocket flight. The system integrates data from multiple onboard sensors including:
- **IMU** (Inertial Measurement Unit)
- **GPS**
- **Barometer**

The telemetry data is streamed in real time to a local server, processed using Python, and visualized via a web dashboard that includes:
- A **3D model** of the rocket reflecting its live orientation (via Three.js)
- **Live graphs** showing altitude and vertical velocity (via Chart.js)

The entire system is modular, cross-platform, and integrates both hardware (ESP32 + sensors) and software (Arduino, Python, JavaScript).

---

## Features
- Real-Time Telemetry Streaming via WebSocket
- Dynamic Charts for altitude and velocity
- 3D Rocket Visualization based on IMU orientation
- Python Backend for data handling and analysis
- Arduino scripts for sensor integration
- Simple startup using `start.bat`

---

## Project Structure
```
SPACEGURION_FLIGHTCOMPUTER/
│
├── arduino/
│   ├── esp_sensors/
│   │   └── esp_sensors.ino
│   ├── IMU_Data/
│   │   └── IMU_Data.ino  ** to be removed
│   └── libraries/
│       * specified below *
│
├── backend/
│   └── rocket_data_analysis/
│       ├── data_analysis.py
│       └── rocket_data.csv
│   └── main.py
│
├── dashboard/
|   └── public/
│       ├── 3d_models/
│       │   ├── rocket.glb
│       │   └── Saturn V.glb
│       ├── css/
│       │   └── styles.css
│       ├── js/
│       │   ├── charts.js
│       │   └── model.js
│       └── dashboard.html
│
├── schematics/
│   ├── hardware_diagram.png
│   └── ground_control.png
|
├── start.bat
└── README.md
```

---

## Setup & Running the Project

### Prerequisites
- Python 3.x
- Arduino IDE
- A modern browser (for dashboard)

### Install Required Python Libraries
```bash
pip install websockets numpy pandas
```

### Required Arduino Libraries
Install the following via the Arduino Library Manager:
- SparkFun_ICM-20948_ArduinoLibrary
- Adafruit_BMP280
- SparkFun_u-blox_GNSS_Arduino_Library

### Running the System
Start the system:
  - Double-click `start.bat`  
  or
  - Manually run:
     ```bash
     python backend/main.py
     ```
---

## Notes & TODO
- [ ] Add diagrams illustrating system flow
- [ ] Refactor backend for modularity
- [ ] Add logging and error handling
- [ ] Improve UI controls (e.g., pause/resume)

---

## Credits
This project is maintained by the Flight Computer team @ SpaceGurion.
---