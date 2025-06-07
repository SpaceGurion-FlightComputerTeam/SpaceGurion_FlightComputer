

#include "imu.h"
#include "coumunication.h"
#include "barometer.h"
#include "helper.h"
#include "sd_logger.h"

// ----- GNSS Setup ----- (gps)
const char *filename = "/telemetry.txt";
SFE_UBLOX_GNSS myGNSS;


// Global variables to hold the last known valid GNSS fix:
double lastLat = 0.0;
double lastLon = 0.0;

// Logging control variables:
bool loggingEnabled = true;      // Default: logging is enabled
unsigned long baseTime = 0;        // Base time for relative timestamps


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
// Setup
////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(I2C_DATA);
  start_socket(RadioRate,  XBEE_RX, XBEE_TX);
  initSDCard();
  baseTime = millis();
  
  // ----- I2C Initialization -----
  Wire.begin();
  
  // ----- GNSS Initialization -----
  if (!myGNSS.begin()) {
    Serial.println("❌ u-blox GNSS module not detected. Check wiring.");
  }
  // Comment this out to avoid flooding Serial with raw NMEA messages:
  // myGNSS.setNMEAOutputPort(Serial);
  myGNSS.setAutoPVT(true);         // Enable automatic position updates
  myGNSS.setNavigationFrequency(10);  // Set GNSS update rate to 5 Hz

  BARSetup();
  ImuSetup();
  delay(LOG_TIME); // Delay between log entries; adjust as needed.
  
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
    } else
     {
     
      gnssData = String(lastLat, 7) + "," + String(lastLon, 7);
      Serial.println("GNSS data not available. Using last known fix.");
    }
    
    String bmpData=getFormattedData();
 
 
    String logLine =  bmpData+";"+ readIMU()+ ";" +gnssData+"\n" ;
    
    Serial.println("Log line: " + logLine);
    writeToSD(logLine);
    send(logLine);
  }
  
  Serial.println("----------------------\n");
 
}
