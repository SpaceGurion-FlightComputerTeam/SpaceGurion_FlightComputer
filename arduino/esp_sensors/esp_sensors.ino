/****************************************************************
 * Fused Telemetry Example
 * Combines IMU (ICM-20948 with DMP Quat9 over SPI), BMP280, and
 * u‑blox GNSS.
 *
 * IMU: Uses SPI. Unnecessary I2C defines (WIRE_PORT, AD0_VAL) removed.
 * BMP280 & GNSS: Use I2C via Wire.
 *
 * Libraries required:
 *   - SparkFun_ICM-20948_ArduinoLibrary
 *   - Adafruit_BMP280
 *   - SparkFun_u-blox_GNSS_Arduino_Library
 *
 * Adapted from:
 *   Example6_DMP_Quat9_Orientation.ino (ICM-20948)
 *   BMP280 and GNSS example code.
 *
 * No warranty is given.
 ***************************************************************/

#include "ICM_20948.h" // SparkFun ICM-20948 library (SPI version will be used)
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include "SparkFun_u-blox_GNSS_Arduino_Library.h"

// ----- IMU (ICM-20948) Setup -----
// Using SPI
#define SERIAL_PORT Serial
#define SPI_PORT SPI           // SPI port to use
#define CS_PIN 5               // Chip select pin for the IMU

ICM_20948_SPI myICM;           // Using SPI for the IMU

// ----- BMP280 Setup -----
Adafruit_BMP280 bmp;           // I2C BMP280 sensor
#define SEA_LEVEL_PRESSURE_HPA 1013.25

// ----- GNSS Setup -----
SFE_UBLOX_GNSS myGNSS;

void setup() {
  SERIAL_PORT.begin(115200);
  while (!SERIAL_PORT); // Wait for Serial connection
  SERIAL_PORT.println(F("Initializing sensors..."));

  // ----------- IMU (ICM-20948) Initialization -----------
  SPI_PORT.begin();
  
  bool imuInitialized = false;
  while (!imuInitialized) {
    // Initialize the IMU using SPI
    myICM.begin(CS_PIN, SPI_PORT);
    SERIAL_PORT.print(F("IMU Initialization returned: "));
    SERIAL_PORT.println(myICM.statusString());
    if (myICM.status != ICM_20948_Stat_Ok) {
      SERIAL_PORT.println(F("Trying IMU initialization again..."));
      delay(500);
    }
    else {
      imuInitialized = true;
    }
  }
  SERIAL_PORT.println(F("IMU connected!"));

  bool success = true; // Track DMP configuration success

  // Initialize DMP (requires enabling DMP in ICM_20948_C.h)
  success &= (myICM.initializeDMP() == ICM_20948_Stat_Ok);

  // Enable the DMP orientation sensor (Quat9 output)
  success &= (myICM.enableDMPSensor(INV_ICM20948_SENSOR_ORIENTATION) == ICM_20948_Stat_Ok);

  // Set the DMP ODR for Quat9 to the maximum (value = 0)
  success &= (myICM.setDMPODRrate(DMP_ODR_Reg_Quat9, 0) == ICM_20948_Stat_Ok);

  // Enable FIFO and DMP, then reset DMP and FIFO
  success &= (myICM.enableFIFO() == ICM_20948_Stat_Ok);
  success &= (myICM.enableDMP() == ICM_20948_Stat_Ok);
  success &= (myICM.resetDMP() == ICM_20948_Stat_Ok);
  success &= (myICM.resetFIFO() == ICM_20948_Stat_Ok);

  if (success) {
    SERIAL_PORT.println(F("IMU DMP enabled!"));
  } else {
    SERIAL_PORT.println(F("Failed to enable IMU DMP! Check your DMP configuration in ICM_20948_C.h"));
    while (1); // Halt if IMU configuration fails
  }
  
  // ----------- BMP280 & GNSS Initialization -----------
  Wire.begin();  // Begin I2C for BMP280 and GNSS

  // GNSS initialization
  if (!myGNSS.begin()) {
    SERIAL_PORT.println(F("GNSS module not detected at default I2C address. Check wiring."));
    while (1);
  }
  myGNSS.setAutoPVT(true);  // Enable automatic position updates
  myGNSS.setNavigationFrequency(5); // Set GNSS update rate to 5 Hz

  // BMP280 initialization
  if (!bmp.begin()) {
    SERIAL_PORT.println(F("Could not find a valid BMP280 sensor. Check wiring or I2C address."));
    while (1);
  }
  bmp.setSampling(Adafruit_BMP280::MODE_FORCED,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);

  SERIAL_PORT.println(F("Setup complete.\n"));
}

void loop() {
  // ----------- IMU Data Processing -----------
  icm_20948_DMP_data_t data;
  myICM.readDMPdataFromFIFO(&data);
  if ((myICM.status == ICM_20948_Stat_Ok) || (myICM.status == ICM_20948_Stat_FIFOMoreDataAvail)) {
    // Check for Quat9 header
    if ((data.header & DMP_header_bitmap_Quat9) > 0) {
      // Convert Q1, Q2, Q3 from fixed-point (scaled by 2^30) to double precision
      double q1 = ((double)data.Quat9.Data.Q1) / 1073741824.0;
      double q2 = ((double)data.Quat9.Data.Q2) / 1073741824.0;
      double q3 = ((double)data.Quat9.Data.Q3) / 1073741824.0;
      // Reconstruct Q0 using the unit quaternion constraint
      double q0 = sqrt(1.0 - (q1*q1 + q2*q2 + q3*q3));

      SERIAL_PORT.print(F("IMU -> Q1:"));
      SERIAL_PORT.print(q1, 3);
      SERIAL_PORT.print(F(" Q2:"));
      SERIAL_PORT.print(q2, 3);
      SERIAL_PORT.print(F(" Q3:"));
      SERIAL_PORT.print(q3, 3);
      SERIAL_PORT.print(F(" Accuracy:"));
      SERIAL_PORT.println(data.Quat9.Data.Accuracy);
    }
  }
  if (myICM.status != ICM_20948_Stat_FIFOMoreDataAvail) {
    delay(10);
  }
  
  // ----------- GNSS Data Processing -----------
  if (myGNSS.getPVT()) {
    double lat = myGNSS.getLatitude() / 10000000.0;
    double lon = myGNSS.getLongitude() / 10000000.0;
    
    SERIAL_PORT.print(F("GNSS -> Decimal degrees: "));
    SERIAL_PORT.print(lat, 7);
    SERIAL_PORT.print(F(", "));
    SERIAL_PORT.println(lon, 7);
    
    printDMS(lat, lon);
  }
  
  // ----------- BMP280 Data Processing -----------
  if (bmp.takeForcedMeasurement()) {
    SERIAL_PORT.print(F("BMP280 -> Temperature = "));
    SERIAL_PORT.print(bmp.readTemperature());
    SERIAL_PORT.println(" *C");
    
    SERIAL_PORT.print(F("BMP280 -> Pressure = "));
    SERIAL_PORT.print(bmp.readPressure());
    SERIAL_PORT.println(" Pa");
    
    SERIAL_PORT.print(F("BMP280 -> Approx altitude = "));
    SERIAL_PORT.print(bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA));
    SERIAL_PORT.println(" m");
  } else {
    SERIAL_PORT.println(F("BMP280 measurement failed!"));
  }

  SERIAL_PORT.println("----------------------\n");
  delay(200);
}

// Convert decimal degrees to DMS format
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

  SERIAL_PORT.print(F("GNSS -> DMS format: "));
  SERIAL_PORT.print(latDeg); SERIAL_PORT.print("°");
  SERIAL_PORT.print(latMin); SERIAL_PORT.print("'");
  SERIAL_PORT.print(latSec, 1); SERIAL_PORT.print("\"");
  SERIAL_PORT.print(latHem); SERIAL_PORT.print(", ");

  SERIAL_PORT.print(lonDeg); SERIAL_PORT.print("°");
  SERIAL_PORT.print(lonMin); SERIAL_PORT.print("'");
  SERIAL_PORT.print(lonSec, 1); SERIAL_PORT.print("\"");
  SERIAL_PORT.println(lonHem);
}
