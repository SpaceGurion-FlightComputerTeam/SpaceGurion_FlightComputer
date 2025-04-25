#include "sd_logger.h"

const char *filename = "/telemetry.txt";
bool loggingEnabled = true;
unsigned long baseTime = 0;

//update
void initSDCard() {
  SPI.begin(sck, miso, mosi, cs);
  if (!SD.begin(cs)) {
    if (!SD.begin()) {
      Serial.println("Card Mount Failed");
      return;
    }
    uint8_t cardType = SD.cardType();

    if (cardType == CARD_NONE) {
      Serial.println("No SD card attached");
      return;
    }
  }
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
//update
void writeToSD(String message) {


  File file = fs.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println("Failed to open file for writing");
    return;
  }
  if (file.print(message)) {
    Serial.println("File written");
  } else {
    Serial.println("Write failed");
  }
  file.close();
}

void processSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.equalsIgnoreCase("stop")) {
      stopLogging();
    } else if (command.equalsIgnoreCase("start")) {
      startLogging();
    } else if (command.equalsIgnoreCase("continue")) {
      continueLogging();
    } else if (command.equalsIgnoreCase("read")) {
      Serial.println("Reading telemetry file:");
      readSDFile();
    } else {
      Serial.println("Unknown command. Use 'stop', 'start', 'continue' or 'read'.");
    }
  }
}
