#!/usr/bin/env python3

# GPIO 25 - Encoder A for Motor1
# GPIO 22 - Encoder B for Motor1
# GPIO 24 - Encoder A for Motor2
# GPIO 23 - Encoder B for Motor2
import Libraries.Thunderborg as ThunderBorg
import sys
import time

motor_left = 1
motor_right = 1
try:
    motor_left = float(sys.argv[1])
except ValueError:
    print("Invalid Argument")
except IndexError:
    pass

try:
    motor_right = float(sys.argv[2])
except ValueError:
    print("Invalid Argument")
except IndexError:
    pass

print(
    f"Running at left motor at {motor_left} speed, and Running the right motor at {motor_right}"
)

TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x15
TB.Init()

# Thunderborg Checks
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print("No ThunderBorg found, check you are attached :)")
    else:
        print(f"No ThunderBorg at address {TB.i2cAddress}, but we did find boards:")
        for board in boards:
            print("    %02X (%d)" % (board, board))
        print(
            "If you need to change the I²C address change the setup line so it is correct, e.g."
        )
        print("TB.i2cAddress = 0x%02X" % (boards[0]))
    sys.exit()

TB.SetBatteryMonitoringLimits(10, 13)  # Set LED Battery Indicator

try:
    loop = 1
    while True:
        TB.SetMotor1(motor_left)
        TB.SetMotor2(motor_right)
        loop += 1
        if loop % 2 == 0:
            motor_right += 0.41
            motor_left += 0.41
        else:
            motor_right -= 0.41
            motor_left -= 0.41
        if loop == 1000:
            motor_right = -motor_right
            motor_left = -motor_left
            loop = 0
        # print(TB.GetBatteryReading(), end='\r')
except KeyboardInterrupt:
    pass
TB.MotorsOff()
