import serial
import time
import datetime
import sys
import io
import re

import timeit

ser = serial.Serial(
    port='/dev/serial/by-path/platform-3f980000.usb-usb-0:1.2:1.0-port0',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS,
    timeout=100000,
)


#time.sleep(3)
#ser.write(':CONFigure:VOLTage:DC\n')
#time.sleep(3)
#ser.write('*CLS\r\n')

sample_per_s = 0
time_out = datetime.datetime.now() + datetime.timedelta(seconds=1)

#ser.write('MEASure:VOLTage:DC?\r\n')


while True:
    ser.write("*RST\n")
    ser.write(":TRAC:POIN 1024\n")
    time.sleep(0.1)
    ser.write(":VOLTage:DC:NPLCycles 0.01\n")
    time.sleep(0.1)
    ser.write(":TRIG:DELAY 0.0\n")
    time.sleep(0.1)

    # External Trigger
    #ser.write(":TRIG:SOURCE EXT \n")
    # Software Trigger
    ser.write(":Trigger:Source BUS\n")
    time.sleep(0.1)

    ser.write(":SAMPLE:COUNT 1024\n")
    time.sleep(0.1)
    ser.write(":INIT\n")
    time.sleep(0.1)

    raw_input("Start sampling press ENTER : ")
    ser.write("*TRG\n")

    ser.write("*wai\n")

    start = datetime.datetime.now()

    ser.write(":TRAC:DATA?\n")

    print("Can take a while ...")
    rslt = ser.readline()

    end = datetime.datetime.now() - start

    # Print raw value from RS232
    # print(rslt)

    ser.flush()

    data = rslt.split(",")

    index = 0

    for a_data in data:
        searchObj = re.match(r'([+-])(\d*?)[.](\d*)[E]([+-])(\d{2})', a_data)

        if searchObj:
            #print(searchObj.group(1))# Polarity
            #print(searchObj.group(2))# First digit
            #print(searchObj.group(3))# 8 digit after
            #print(searchObj.group(4))# factor sign
            #print(searchObj.group(5))# factor

            voltage_str = searchObj.group(2) + searchObj.group(3)

            # To V
            if searchObj.group(4) is '+':
                factor = int(searchObj.group(5)) + 1
                voltage = voltage_str[:factor] + '.' + voltage_str[factor:]
                print("Voltage : {} V ".format(voltage))

            # To mV
            elif searchObj.group(4) is '-':
                if int(searchObj.group(5)) is 3:
                    voltage = voltage_str[:1] + '.' + voltage_str[1:]
                    print("Voltage : {} mV ".format(voltage))
                elif int(searchObj.group(5)) is 2:
                    voltage = voltage_str[:2] + '.' + voltage_str[2:]
                    print("Voltage : {} mV ".format(voltage))
                elif int(searchObj.group(5)) is 1:
                    voltage = voltage_str[:3] + '.' + voltage_str[3:]
                    print("Voltage : {} mV ".format(voltage))
            else:
                print("Can't decode value : {}".format(a_data))

        else:
            pass

        index += 1

    print("Have {} value in this test.".format(index))
    print("Take {} for execute test ".format(end))
