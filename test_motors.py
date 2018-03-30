import nxt.locator
import nxt.brick
from nxt.motor import *
import time
import pickle

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

    m = Motor(b, PORT_A)
    max_tacho = 130

    all_tachos = []
    try:
        for tacho in range(5, max_tacho, 10):
            tacholist = ([], [], [])
            for power in range(20, 130, 10):
                start_time = time.time()
                m.turn(power, tacho)
                m.turn(power * -1, tacho)
                delta_time = time.time() - start_time
                tacholist[0].append(tacho)
                tacholist[1].append(power)
                tacholist[2].append(delta_time / tacho / 2)
            all_tachos.append(tacholist)
            m.idle()
            time.sleep(5)
    except:
        pass
    pickle.dump(all_tachos, open('calibration_MM.p', 'wb'))

    b.sock.close()
except:
    print("Error while running test:")
    traceback.print_tb(sys.exc_info()[2])
    print(str(sys.exc_info()[1]))
    if b in locals():
        b.sock.close()
