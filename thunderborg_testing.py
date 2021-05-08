import Libraries.ThunderBorg3 as ThunderBorg
import sys
import time

TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
#TB.i2cAddress = 0x15           # Uncomment and change the value if you have changed the board address
TB.Init()                       # Set the board up (checks the board is connected)
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print('No ThunderBorg found, check you are attached :)')
    else:
        print(f'No ThunderBorg at address {TB.i2cAddress}, but we did find boards:')
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the I²C address change the setup line so it is correct, e.g.')
        print('TB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()

# TB.SetLedShowBattery(False)
TB.SetBatteryMonitoringLimits(7.5, 9)

# TB.SetLed1(0, 0, 255)
# time.sleep(0.2)
# TB.SetLed1(0, 0, 0)
# time.sleep(0.2)

# TB.SetLed1(0, 0, 255)
# time.sleep(0.2)
# TB.SetLed1(0, 0, 0)
# time.sleep(0.2)

# TB.SetLed1(0, 255, 0)

# TB.SetMotor1(1)
# time.sleep(2)
# TB.SetMotor1(0)
from Encoder import Encoder
encoder = Encoder(23)
try:
    TB.SetMotor2(1)
    time.sleep(30)
except:
    pass
TB.MotorsOff()

# TB.SetLed1(255, 255, 0)
# time.sleep(0.2)
# TB.SetLed1(0, 0, 0)
# time.sleep(0.2)

# TB.SetLed1(255, 255, 0)
# time.sleep(0.2)
# TB.SetLed1(0, 0, 0)
# time.sleep(0.2)

# TB.SetLedShowBattery(True)
