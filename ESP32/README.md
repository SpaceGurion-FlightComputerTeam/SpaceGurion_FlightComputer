# **ESP32 Flight Computer System**

This project implements a flight computer system using an **ESP32-WROOM-32E**. The system reads data from an IMU, controls a servo motor based on the IMU readings, and sends the data to a Raspberry Pi via UART. The architecture is designed with abstraction layers to ensure modularity, scalability, and maintainability.

---

## **Project Overview**

The system is organized into the following abstraction layers:

### **1. Board Support Package (BSP)**
The **BSP** is responsible for configuring board-specific hardware such as pin mappings, clock settings, and peripheral initialization.

- **Responsibilities**:
  - Mapping pins for IMU, servo, and UART communication.
  - Initializing board peripherals.

---

### **2. Hardware Abstraction Layer (HAL)**
The **HAL** provides low-level drivers to interface with hardware peripherals. It abstracts the complexity of hardware registers and protocols.

- **Responsibilities**:
  - Drivers for:
    - IMU (e.g., I2C/SPI communication).
    - Servo motor (e.g., PWM control).
    - Serial communication (e.g., UART transmission).
  - Provides hardware-specific functions to upper layers.

---

### **3. Application Programming Interface (API)**
The **API** offers high-level operations built on top of the HAL, making the system hardware-independent for the application layer.

- **Responsibilities**:
  - Simplify hardware operations by exposing functions like:
    - Fetching IMU data.
    - Controlling the servo motor.
    - Sending data to the Raspberry Pi.

---

### **4. Main Application**
The **Main Application** implements the system logic, initializes components, and manages real-time tasks.

- **Responsibilities**:
  - Initialize all layers (BSP, HAL, API).
  - Create and manage tasks for:
    - Reading IMU data.
    - Controlling the servo motor.
    - Sending IMU data to the Raspberry Pi.

---

## **Project Folder Structure**

The folder structure reflects the layered architecture of the project:

```plaintext
/project_root
  ├── ESP32/
  │   ├── bsp/                      # Board Support Package
  │   │   ├── bsp.cpp
  │   │   ├── bsp.h
  │   ├── hal/                      # Hardware Abstraction Layer
  │   │   ├── imu_hal.cpp
  │   │   ├── imu_hal.h
  │   │   ├── servo_hal.cpp
  │   │   ├── servo_hal.h
  │   │   ├── serial_hal.cpp
  │   │   ├── serial_hal.h
  │   ├── api/                      # Application Programming Interface
  │   │   ├── imu_api.cpp
  │   │   ├── imu_api.h
  │   │   ├── servo_api.cpp
  │   │   ├── servo_api.h
  │   │   ├── serial_api.cpp
  │   │   ├── serial_api.h
  │   ├── main/                     # Main Application
  │   │   ├── main.cpp
  ├── include/                      # Shared headers (common typedefs, macros)
  │   ├── common.h
  ├── CMakeLists.txt                # Build system configuration
```
---

## **Setup Instructions**

### **1. Prerequisites**
- ESP32-WROOM-32E (SparkFun RedBoard or equivalent).
- Raspberry Pi (for serial data logging).
- SparkFun 9DoF IMU - ICM-20948 or similar IMU.
- Servo motor.
- ESP-IDF (for FreeRTOS and ESP32 development).

## **How It Works**

The ESP32 flight computer system is designed to handle both **hard real-time tasks** and **soft real-time tasks**, ensuring precise control and reliable communication in a flight environment. Here's an overview of the system's operation:

---

### **Real-Time Tasks**

#### **Hard Real-Time Tasks**
1. **IMU Reading Task**:
   - Continuously reads data (e.g., roll, pitch, yaw) from the IMU at a fixed frequency.
   - Ensures consistent data acquisition to avoid missing critical flight dynamics.

2. **Servo Control Task**:
   - Uses the IMU readings to adjust the servo motor's position in real time.
   - Implements precise timing and deterministic behavior to maintain system stability during flight.

   **Key Characteristics**:
   - Both tasks are time-critical and must execute within strict deadlines.
   - Managed using **FreeRTOS** to guarantee timely execution.

#### **Soft Real-Time Task**
1. **Data Transfer to Raspberry Pi**:
   - Periodically encodes the IMU data and sends it to the Raspberry Pi via UART.
   - While timing is important for data consistency, occasional delays do not compromise system safety or performance.

   **Key Characteristics**:
   - Less time-sensitive compared to hard real-time tasks.
   - Runs as a background task with lower priority in the FreeRTOS scheduler.

---

### **Inter-Layer Communication**

The system follows a layered architecture for modularity and clear separation of concerns:

1. **Board Support Package (BSP)**:
   - Initializes hardware configurations (e.g., pins for IMU, servo, and UART).
   - Provides board-specific functions to the HAL.

2. **Hardware Abstraction Layer (HAL)**:
   - Interfaces directly with hardware peripherals.
   - Provides low-level functions for reading IMU data, controlling the servo, and managing UART communication.

3. **Application Programming Interface (API)**:
   - Encapsulates HAL functionality into high-level operations.
   - Offers a simple and reusable interface for tasks like fetching IMU data or controlling the servo motor.

4. **Main Application**:
   - Coordinates tasks and ensures smooth execution of the system.
   - Interacts with the API to fetch data, control hardware, and manage task priorities.

---

### **Task Priorities**

- **IMU Reading and Servo Control (Hard Real-Time)**:
  - Assigned the **highest priority** to ensure deterministic execution.
  - Typically scheduled at fixed intervals (e.g., 50ms or 20Hz).

- **Data Transfer to Raspberry Pi (Soft Real-Time)**:
  - Runs at a **lower priority**, allowing the system to focus on critical tasks first.
  - Executes periodically (e.g., 100ms or 10Hz) when CPU resources are available.

---

This design ensures that critical control tasks are always executed on time while less critical communication tasks are handled without interfering with system stability.
