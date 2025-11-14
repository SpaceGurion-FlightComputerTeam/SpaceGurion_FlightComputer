#include "imu.h"
ICM_20948_I2C myICM;
void ImuSetup() {
  // SERIAL_PORT.begin(115200);
  while (!Serial) {
  };




  myICM.enableDebugging();  //good for debaging
  bool initialized = false;
  while (!initialized) {


    myICM.begin(Wire, 1);  //ic2

    Serial.print(F("Initialization of the sensor returned: "));
    Serial.println(myICM.statusString());
    if (myICM.status != ICM_20948_Stat_Ok) {
      Serial.println("Trying again...");
      delay(500);
    } else {
      initialized = true;
    }
  }
}


String readIMU() {
  String ans = "";
  if (myICM.dataReady()) {

    myICM.getAGMT();  // Read data
      // ask shachar what he need from the imu

    ans += String(myICM.accX()) + ",";
    ans += String(myICM.accY()) + ",";
    ans += String(myICM.accZ()) + ",";

    //gyro part
    ans += String(myICM.gyrX()) + ",";
    ans += String(myICM.gyrY()) + ",";
    ans += String(myICM.gyrZ()) + ",";

    //magnetic part

    ans += String(myICM.magX()) + ",";
    ans += String(myICM.magY()) + ",";
    ans += String(myICM.magZ());
  }
  return ans;
}
