#include "sd_logger.h"

const char *filename = "/telemetry.txt";
bool loggingEnabled = true;
unsigned long baseTime = 0;

void initSDCard() {
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("❌ SD card initialization failed!");
    while (true);
  }
  Serial.println("✅ SD card initialized.");

  File file = SD.open(filename, FILE_WRITE);
  if (file) {
    file.println("Timestamp,GNSS_Lat,GNSS_Lon,Temperature,Pressure,Altitude");
    file.close();
    Serial.println("Telemetry file created.");
  } else {
    Serial.println("❌ Error creating telemetry file.");
  }

  baseTime = millis();
}

void startLogging() {
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

void stopLogging() {
  loggingEnabled = false;
  Serial.println("Logging stopped.");
}

void continueLogging() {
  loggingEnabled = true;
  Serial.println("Logging continued.");
}

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

void writeToSD(String dataLine) {
  File file = SD.open(filename, FILE_WRITE);
  if (file) {
    file.seek(file.size());
    file.println(dataLine);
    file.close();
    Serial.println("Log line written to SD.");
  } else {
    Serial.println("❌ Error opening telemetry file for writing.");
  }
}

void processSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.equalsIgnoreCase("stop")) {
      stopLogging();
    }
    else if (command.equalsIgnoreCase("start")) {
      startLogging();
    }
    else if (command.equalsIgnoreCase("continue")) {
      continueLogging();
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
