#ifndef SD_LOGGER_H
#define SD_LOGGER_H

#include "helper.h"


extern const char *filename;
extern bool loggingEnabled;
extern unsigned long baseTime;

// פונקציות להפעלה מהקוד הראשי
void initSDCard();
void startLogging();
void stopLogging();
void continueLogging();
void readSDFile();
void writeToSD(String dataLine);
void processSerialCommands();

#endif
