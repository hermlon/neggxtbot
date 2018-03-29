import nxt.locator
import nxt.brick
from nxt.motor import *
import time
from gcode_parser import NeggxtBotGCodeParser

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

    m_a = Motor(b, PORT_A)
    m_b = Motor(b, PORT_B)
    m_c = Motor(b, PORT_C)

    #g = NeggxtBotGCodeParser(m_c, m_a, m_b)

    #import pdb; pdb.set_trace()


    b.sock.close()
except:
    print("Error while running test:")
    traceback.print_tb(sys.exc_info()[2])
    print(str(sys.exc_info()[1]))
    if b in locals():
        b.sock.close()
