from Library.k2000_driver import K2000Driver
import datetime
import sys

SERIAL_INTERFACE = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.2:1.0-port0'

test = K2000Driver()


test.init_serial(SERIAL_INTERFACE)

# delay = 0.02505265 / NPLC = 1 for ~0.05 sec per measurement
# test.init_k2000(smpl_nbr=1024, trg_source="BUS", nplc="1", delay=0.02505265)

test.init_k2000(smpl_nbr=1024, trg_source="BUS", nplc="0.1")

test.trig_k2000(wait_acquisition=False)

start = datetime.datetime.now()

print("Execute Measurement")
while True:
    if int(test.get_status()) == 1024:
        print
        break
    else:
        sys.stdout.write('.')
        sys.stdout.flush()

end = datetime.datetime.now() - start

rslt = test.get_data()


# Print raw value from RS232
# print(rslt)


data = rslt.split(",")

index = 0

for a_data in data:
    #print(test.decode_data(a_data))
    index += 1

print("Have {} value in this test.".format(index))
print("Take {} for execute test ".format(end))

