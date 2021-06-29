#!/usr/bin/env python3

# GPIO 25 - Encoder A for Motor1
# GPIO 22 - Encoder B for Motor1
# GPIO 24 - Encoder A for Motor2
# GPIO 23 - Encoder B for Motor2
import Libraries.ThunderBorg3 as ThunderBorg
import sys
import time

motor_left = 1
motor_right = 0
try:
    motor_left = int(sys.argv[1])
except ValueError:
    print("Invalid Argument")
except IndexError:
    pass

try:
    motor_right = int(sys.argv[2])
except ValueError:
    print("Invalid Argument")
except IndexError:
    pass

TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
# TB.i2cAddress = 0x15           # Uncomment and change the value if you have changed the board address
TB.Init()                       # Set the board up (checks the board is connected)
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print('No ThunderBorg found, check you are attached :)')
    else:
        print(f'No ThunderBorg at address {TB.i2cAddress}, \
                but we did find boards:')
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the I²C address change the setup line so \
            it is correct, e.g.')
        print('TB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()

TB.SetBatteryMonitoringLimits(11, 13)

try:
    TB.SetMotor1(motor_left)
    TB.SetMotor2(motor_right)
    while True:
        time.sleep(1)
        print(TB.GetBatteryReading())
except KeyboardInterrupt:
    pass
TB.MotorsOff()
