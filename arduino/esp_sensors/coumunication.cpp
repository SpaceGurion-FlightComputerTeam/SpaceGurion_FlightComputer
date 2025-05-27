
#include "coumunication.h"

void start_socket(int rate,int rx,int tx)
{
   Serial2.begin(rate, SERIAL_8N1, rx, tx);
}

/*
input :msg-the mesage to send
*/
void send(String msg)
{
   Serial2.print(msg);
}

/*
masege to recive
*/
String  recive()
{
    return "";//Serial2.read();
}

