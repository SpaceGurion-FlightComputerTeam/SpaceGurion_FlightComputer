#include <SD.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include "SparkFun_u-blox_GNSS_Arduino_Library.h"

// ----- SD Card Setup -----
// The onboard µSD slot on the ESP32 Thing Plus uses GPIO 5 for CS.
#define SD_CS_PIN 5
const char *filename = "/telemetry.txt";

// ----- BMP280 Setup -----
Adafruit_BMP280 bmp; // I2C BMP280 sensor
#define SEA_LEVEL_PRESSURE_HPA 1013.25

// ----- GNSS Setup -----
SFE_UBLOX_GNSS myGNSS;

// ----- (Optional) IMU Setup (I2C / Qwiic) -----
// Uncomment the following if you plan to use the IMU via I2C (Qwiic)
// #include "ICM_20948.h"
// ICM_20948_I2C myIMU;

// Global variables to hold the last known valid GNSS fix:
double lastLat = 0.0;
double lastLon = 0.0;

// Logging control variables:
bool loggingEnabled = true;      // Default: logging is enabled
unsigned long baseTime = 0;        // Base time for relative timestamps

////////////////////////////////////////////////////////////
// Helper function: Append a line to the SD card file
////////////////////////////////////////////////////////////
void writeToSD(String dataLine) {
  File file = SD.open(filename, FILE_WRITE);
  if (file) {
    // Move file pointer to the end of file to ensure appending.
    file.seek(file.size());
    file.println(dataLine);
    file.close();
    Serial.println("Log line written to SD.");
  } else {
    Serial.println("❌ Error opening telemetry file for writing.");
  }
}

////////////////////////////////////////////////////////////
// Helper function: Read and print the entire telemetry file
////////////////////////////////////////////////////////////
void readSDFile() {
  File file = SD.open(filename, FILE_READ);
  if (file) {
    Serial.println("----- Contents of telemetry.txt -----");
    while (file.available()) {
      Serial.print((char)file.read());
    }
    file.close();
    Serial.println("\n----- End of file -----");
  } else {
    Serial.println("❌ Error opening telemetry file for reading.");
  }
}

////////////////////////////////////////////////////////////
// Helper function: Convert decimal degrees to DMS and print it
////////////////////////////////////////////////////////////
void printDMS(double lat, double lon) {
  char latHem = (lat >= 0) ? 'N' : 'S';
  char lonHem = (lon >= 0) ? 'E' : 'W';
  lat = fabs(lat);
  lon = fabs(lon);
  
  int latDeg = (int)lat;
  int lonDeg = (int)lon;
  double latMinFull = (lat - latDeg) * 60;
  double lonMinFull = (lon - lonDeg) * 60;
  int latMin = (int)latMinFull;
  int lonMin = (int)lonMinFull;
  double latSec = (latMinFull - latMin) * 60;
  double lonSec = (lonMinFull - lonMin) * 60;
  
  Serial.print("DMS format: ");
  Serial.print(latDeg); Serial.print("°");
  Serial.print(latMin); Serial.print("'");
  Serial.print(latSec, 1); Serial.print("\"");
  Serial.print(latHem); Serial.print(", ");
  Serial.print(lonDeg); Serial.print("°");
  Serial.print(lonMin); Serial.print("'");
  Serial.print(lonSec, 1); Serial.print("\"");
  Serial.println(lonHem);
}

////////////////////////////////////////////////////////////
// Process Serial Commands: "stop", "start", "continue", "read"
////////////////////////////////////////////////////////////
void processSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.equalsIgnoreCase("stop")) {
      loggingEnabled = false;
      Serial.println("Logging stopped.");
    }
    else if (command.equalsIgnoreCase("start")) {
      // Remove the current file to start fresh and reset timestamp.
      if (SD.exists(filename)) {
        SD.remove(filename);
      }
      File file = SD.open(filename, FILE_WRITE);
      if (file) {
        file.println("Timestamp,GNSS_Lat,GNSS_Lon,Temperature,Pressure,Altitude");
        file.close();
        Serial.println("New logging started. File cleared. Timestamp reset to 0.");
      } else {
        Serial.println("❌ Error creating new telemetry file.");
      }
      baseTime = millis();
      loggingEnabled = true;
    }
    else if (command.equalsIgnoreCase("continue")) {
      loggingEnabled = true;
      Serial.println("Logging continued.");
    }
    else if (command.equalsIgnoreCase("read")) {
      Serial.println("Reading telemetry file:");
      readSDFile();
    }
    else {
      Serial.println("Unknown command. Use 'stop', 'start', 'continue' or 'read'.");
    }
  }
}

////////////////////////////////////////////////////////////
// Setup
////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Initializing sensors and SD card...");
  
  // ----- SD Card Initialization -----
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("❌ SD card initialization failed!");
    while (true); // Halt if SD card isn't working.
  }
  Serial.println("✅ SD card initialized.");
  
  // Create or clear the telemetry file with a CSV header.
  File file = SD.open(filename, FILE_WRITE);
  if (file) {
    file.println("Timestamp,GNSS_Lat,GNSS_Lon,Temperature,Pressure,Altitude");
    file.close();
    Serial.println("Telemetry file created.");
  } else {
    Serial.println("❌ Error creating telemetry file.");
  }
  
  // Set the base timestamp for logging.
  baseTime = millis();
  
  // ----- I2C Initialization -----
  Wire.begin();
  
  // ----- GNSS Initialization -----
  if (!myGNSS.begin()) {
    Serial.println("❌ u-blox GNSS module not detected. Check wiring.");
    while (true);
  }
  // Comment this out to avoid flooding Serial with raw NMEA messages:
  // myGNSS.setNMEAOutputPort(Serial);
  myGNSS.setAutoPVT(true);         // Enable automatic position updates
  myGNSS.setNavigationFrequency(5);  // Set GNSS update rate to 5 Hz
  
  // ----- BMP280 Initialization -----
  if (!bmp.begin()) {
    Serial.println("❌ Could not find BMP280 sensor. Check wiring or address.");
    while (true);
  }
  bmp.setSampling(Adafruit_BMP280::MODE_FORCED,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);
  
  // ----- (Optional) IMU Initialization (I2C / Qwiic) -----
  // Uncomment the following block when you want to use an IMU via I2C/Qwiic.
  /*
  if (!myIMU.begin(Wire)) {
    Serial.println("❌ IMU not detected. Check Qwiic wiring.");
    while (true);
  }
  Serial.println("✅ IMU (I2C) connected!");
  // Configure the IMU as needed...
  */
  
  Serial.println("Setup complete.\n");
}

////////////////////////////////////////////////////////////
// Main Loop
////////////////////////////////////////////////////////////
void loop() {
  // Process any serial commands first.
  processSerialCommands();

  // Only log sensor data if logging is enabled.
  if (loggingEnabled) {
    // Compute relative timestamp (in milliseconds) from when logging started.
    unsigned long relTimestamp = millis() - baseTime;
    
    // --- GNSS Data Processing ---
    String gnssData;
    if (myGNSS.getPVT()) {
      double lat = myGNSS.getLatitude() / 10000000.0;
      double lon = myGNSS.getLongitude() / 10000000.0;
      lastLat = lat;
      lastLon = lon;
      gnssData = String(lat, 7) + "," + String(lon, 7);
      Serial.print("Decimal degrees: ");
      Serial.print(lat, 7);
      Serial.print(", ");
      Serial.println(lon, 7);
      printDMS(lat, lon);
    } else {
      // Use last known fix if no new data is available.
      gnssData = String(lastLat, 7) + "," + String(lastLon, 7);
      Serial.println("GNSS data not available. Using last known fix.");
    }
    
    // --- BMP280 Data Processing ---
    String bmpData;
    if (bmp.takeForcedMeasurement()) {
      float temp = bmp.readTemperature();
      float press = bmp.readPressure();
      float alt = bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA);
      bmpData = String(temp, 2) + "," + String(press, 0) + "," + String(alt, 2);
      Serial.print("Temperature = ");
      Serial.print(temp);
      Serial.println(" *C");
      Serial.print("Pressure = ");
      Serial.print(press);
      Serial.println(" Pa");
      Serial.print("Approx altitude = ");
      Serial.print(alt);
      Serial.println(" m");
    } else {
      bmpData = "N/A,N/A,N/A";
      Serial.println("BMP280 measurement failed!");
    }
    
    // --- (Optional) IMU Data Processing ---
    // Uncomment and complete this block if using an I2C/Qwiic IMU in the future.
    /*
    String imuData;
    if (/* valid IMU data available * /) {
      // Example:
      // imuData = String(q0,3) + "," + String(q1,3) + "," + String(q2,3) + "," + String(q3,3);
    } else {
      imuData = "N/A,N/A,N/A,N/A";
    }
    */
    
    // --- Combine sensor data into one CSV log line ---
    // Format: RelativeTimestamp,GNSS_Lat,GNSS_Lon,Temperature,Pressure,Altitude
    String logLine = String(relTimestamp) + "," + gnssData + "," + bmpData;
    // Append IMU data if available:
    // logLine += "," + imuData;
    
    Serial.println("Log line: " + logLine);
    writeToSD(logLine);
  }
  
  Serial.println("----------------------\n");
  delay(1000); // Delay between log entries; adjust as needed.
}
