
#include "sd_logger.h"

String Filepath ="/log.txt";
File logFile;
bool isLogging = false;

// ------------------ SD Functions ------------------ //

void initSDCard() {
    Serial.println("Initializing SD card...");
    if (!SD.begin(SD_CS)) {
        Serial.println("SD card initialization failed!");
        return;
    }
    Serial.println("SD card initialized.");
}

void startLogging() {
    if (!isLogging) {
        logFile = SD.open(Filepath, FILE_WRITE);
        if (logFile) {
            Serial.println("Logging started.");
            isLogging = true;
        }
        else {
            Serial.println("Failed to open log.txt for writing.");
        }
    }
}

void stopLogging() {
    if (isLogging) {
        logFile.close();
        Serial.println("Logging stopped.");
        isLogging = false;
    }
}

void continueLogging() {
    if (!isLogging) {
        logFile = SD.open(Filepath, FILE_APPEND);
        if (logFile) {
            Serial.println("Logging continued.");
            isLogging = true;
        }
        else {
            Serial.println("Failed to reopen log.txt.");
        }
    }
}

void writeToSD(String dataLine) {
    if (isLogging && logFile) {
        logFile.println(dataLine);
        logFile.flush(); // Ensure it's written immediately
        Serial.println("Wrote: " + dataLine);
    }
    else {
        Serial.println("Not logging. Cannot write.");
    }
}

void readSDFile() {
    File file = SD.open(Filepath);
    if (file) {
        Serial.println("--- Reading log.txt ---");
        while (file.available()) {
            Serial.write(file.read());
        }
        file.close();
        Serial.println("\n--- End of File ---");
    }
    else {
        Serial.println("Failed to open log.txt for reading.");
    }
}

void processSerialCommands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command == "start") {
            startLogging();
        }
        else if (command == "stop") {
            stopLogging();
        }
        else if (command == "continue") {
            continueLogging();
        }
        else if (command == "read") {
            readSDFile();
        }
        else if (command.startsWith("write ")) {
            String data = command.substring(6);
            writeToSD(data);
        }
        else {
            Serial.println("Unknown command. Use: start, stop, continue, read, write <text>");
        }
    }
}
