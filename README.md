# Rocket IMU Data Visualization

## Overview
This project reads real-time data from the **ICM-20948 IMU sensor** using an Arduino microcontroller and displays it graphically in a web interface. The system runs on a **local Node.js server** and serves the visualization dashboard through a browser.

## Installation & Setup
### Prerequisites
Before setting up, ensure you have the following installed:
- **Node.js** (Download from [nodejs.org](https://nodejs.org/))
- **Arduino IDE** (For uploading code to the microcontroller)
- **Serial communication drivers** (if required for your Arduino board)

### Setup Steps
#### 1. Upload the Arduino Code
1. Open **Arduino IDE**.
2. Install required libraries (if any).
3. Open the Arduino script from this repository.
4. Select the correct board and port.
5. Upload the code to your microcontroller.

#### 2. Install & Run the Web Server
1. Open a terminal inside the `server` directory:
   
2. Install Node.js dependencies:
   ```sh
   npm install
   ```
3. Run the local server by double-click the `start.bat` file in the root directory
   
   - This will launch the server and open `http://127.0.0.1:8080/index.html` in your browser.
   - If the batch file doesn’t work, manually start the server. enter the followind command in the terminal inside the `server` directory:
     
     ```sh
     node server.js
     ```
     then copy `http://127.0.0.1:8080/index.html` to your browser


## File Structure
- **`arduino/`** → Contains the Arduino IMU sensor code.
- **`server/`** → Contains the web interface and backend.
  - **`server.js`** → Node.js server using Express.js.
  - **`public/`** → HTML, CSS, and JavaScript files for visualization.
  - **`package.json`** → Lists dependencies.
  - **`start.bat`** → Starts the server and opens the web app.


## Troubleshooting
- **Missing Packages?** Run `npm install` in the `server/` folder.
- **Port Already in Use?** Change the port in `server.js` if 8080 is taken.
- **Arduino Not Sending Data?** Check serial connections and baud rate.


