import nxt.locator
import nxt.brick
from nxt.motor import *
import time

debug = True

b = None
try:
    b = nxt.locator.find_one_brick(debug=debug)
    name, host, signal_strength, user_flash = b.get_device_info()
    print('NXT brick name: %s' % name)
    print('Host address: %s' % host)
    print('Bluetooth signal strength: %s' % signal_strength)
    print('Free user flash: %s' % user_flash)
    prot_version, fw_version = b.get_firmware_version()
    print('Protocol version %s.%s' % prot_version)
    print('Firmware version %s.%s' % fw_version)
    millivolts = b.get_battery_level()
    print('Battery level %s mV' % millivolts)

    m_c = Motor(b, PORT_C)

    powers = range(20, 130, 10)
    times = []
    for power in powers:
        start_time = time.time()
        m_c.turn(power, 3000)
        delta_time = time.time() - start_time
        times.append(delta_time)

    with open('motor_test_3000.csv','w') as file:
        file.write('power,time\n')
        for i in range(len(powers)):
            file.write(str(powers[i]) + ',' + str(times[i]))
            file.write('\n')

    b.sock.close()
except:
    print("Error while running test:")
    traceback.print_tb(sys.exc_info()[2])
    print(str(sys.exc_info()[1]))
    if b in locals():
        b.sock.close()
