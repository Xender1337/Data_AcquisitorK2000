from Library.k2000_driver import K2000Driver
import datetime

test = K2000Driver()

start = datetime.datetime.now()

test.init_serial('/dev/serial/by-path/platform-3f980000.usb-usb-0:1.2:1.0-port0')
test.init_k2000()
test.trig_k2000()
rslt = test.get_data()

end = datetime.datetime.now() - start

# Print raw value from RS232
# print(rslt)


data = rslt.split(",")

index = 0

for a_data in data:
    test.decode_data(a_data)
    index += 1

print("Have {} value in this test.".format(index))
print("Take {} for execute test ".format(end))

