import serial
import time
import re


class K2000Driver:
    ser = None

    def __init__(self):
        pass

    def init_serial(self, interface):
        self.ser = serial.Serial(
            # port='/dev/serial/by-path/platform-3f980000.usb-usb-0:1.2:1.0-port0',
            port=interface,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS,
            timeout=100000,
        )
        return self.ser

    def decode_data(self, data):
        searchObj = re.match(r'.*([+-])(\d*?)[.](\d*)[E]([+-])(\d{2}).*', data)

        if searchObj:
            # print(searchObj.group(1))# Polarity
            # print(searchObj.group(2))# First digit
            # print(searchObj.group(3))# 8 digit after
            # print(searchObj.group(4))# factor sign
            # print(searchObj.group(5))# factor

            voltage_str = searchObj.group(2) + searchObj.group(3)

            # To V
            if searchObj.group(4) is '+':
                factor = int(searchObj.group(5)) + 1
                voltage = voltage_str[:factor] + '.' + voltage_str[factor:]
                # print("Voltage : {} V ".format(voltage))
                return voltage, "V"

            # To mV
            elif searchObj.group(4) is '-':
                if int(searchObj.group(5)) is 5:
                    voltage = "0.0" + voltage_str
                    # print("Voltage : {} mV ".format(voltage))
                    return voltage, "mV"
                if int(searchObj.group(5)) is 4:
                    voltage = "0." + voltage_str
                    # print("Voltage : {} mV ".format(voltage))
                    return voltage, "mV"
                if int(searchObj.group(5)) is 3:
                    voltage = voltage_str[:1] + '.' + voltage_str[1:]
                    # print("Voltage : {} mV ".format(voltage))
                    return voltage, "mV"
                elif int(searchObj.group(5)) is 2:
                    voltage = voltage_str[:2] + '.' + voltage_str[2:]
                    # print("Voltage : {} mV ".format(voltage))
                    return voltage, "mV"
                elif int(searchObj.group(5)) is 1:
                    voltage = voltage_str[:3] + '.' + voltage_str[3:]
                    # print("Voltage : {} mV ".format(voltage))
                    return voltage, "mV"
                else:
                    print("Can't decode value : {} 6d7e781c-90a6-4d68-80e2-99d3702154f2".format(data))
                    return None

            else:
                print("Can't decode value : {} 29e2a4e8-a841-4543-b446-f1c5825fc20d".format(data))
                return None

        else:
            print("Can't decode value : {} 7d787841-5b5d-41ac-b90b-2c3604bf06d0".format(data))
            return None

    def init_k2000(self, smpl_nbr=1024, trg_source="BUS", nplc="0.1", delay="0.000"):

        if trg_source in ("BUS", "MANUAL", "IMMediate", "TIMer", "EXTernal"):
            pass
        else:
            print("Error not a valid trigger source : {} 98a08c7a-269c-4622-b324-c4bcd3cd256c".format(trg_source))
            raise Exception(ValueError)

        # 0.01 / 0,0062763671875 sec per measure
        # 0.1 / 0,007452734375 sec per measure
        # 1 / 0,02763671875 sec per measure
        # 10 / 0,6133642578125 sec per measure
        if nplc in ("0.01", "0.1", "1", "10"):
            pass
        else:
            print("Error not a valid PLC Number : {} dfcd8450-8662-4c42-854f-d3f2ea09e8b0".format(trg_source))
            raise Exception(ValueError)

        self.ser.write("*RST\n")
        self.ser.write(":TRAC:POIN {}\n".format(smpl_nbr))
        time.sleep(0.1)
        self.ser.write(":VOLTage:DC:NPLCycles {}\n".format(nplc))
        time.sleep(0.1)
        self.ser.write(":TRIG:DELAY {}\n".format(delay))
        time.sleep(0.1)

        # External Trigger
        # ser.write(":TRIG:SOURCE EXT \n")
        # Software Trigger
        self.ser.write(":Trigger:Source {}\n".format(trg_source))
        time.sleep(0.1)

        self.ser.write(":SAMPLE:COUNT {}\n".format(smpl_nbr))
        time.sleep(0.1)
        self.ser.write(":INIT\n")
        time.sleep(0.1)

    def trig_k2000(self, wait_acquisition=True):
        # raw_input("Start sampling press ENTER : ")
        self.ser.write("*TRG\n")
        if wait_acquisition is True:
            self.ser.write("*wai\n")

    def get_status(self):
        # Operation Register
        # [0 - 3] None
        # 4 Measuring
        # 5 Triggering
        # [6 - 9] None
        # 10 Idle
        # [11 - 15] None
        # Measure 100000 / 32
        # Trigger an Measure 1100000 / 48
        # Idle 10000000000 / 1024

        self.ser.write(":STATus:OPERation?\n")
        rslt = re.sub("[^0-9]", "", self.ser.readline())
        # print(rslt)
        # print("{0:b}".format(int(rslt)))
        return rslt

    def get_data(self):
        self.ser.write(":TRAC:DATA?\n")

        print("Get Result. Can take a while ...")
        rslt = self.ser.readline()
        self.ser.flush()
        return rslt
