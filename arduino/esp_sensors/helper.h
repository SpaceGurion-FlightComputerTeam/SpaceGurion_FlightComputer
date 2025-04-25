#ifndef  HELPER
#define HELPER

#include <Arduino.h>
#include "ICM_20948.h"
#include "barometer.h"
#include <Adafruit_BMP280.h>
#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#define SEA_LEVEL_PRESSURE_HPA 1013.25
#include "SparkFun_u-blox_GNSS_Arduino_Library.h"
#define XBEE_RX 16  // ESP32 RX pin connected to XBee TX
#define XBEE_TX 17  // ESP32 TX pin connected to XBee RX
#define SD_CS_PIN 5
#define I2C_DATA  115200
#define LOG_TIME 36000
#endif