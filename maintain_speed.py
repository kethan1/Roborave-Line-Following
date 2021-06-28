#!/usr/bin/env python3

from PID import PID
from CPP_Libraries.Encoder_CPP.encoder import Encoder, init as initialize
import Libraries.ThunderBorg3 as ThunderBorg

import time
import sys
import random
import math

initialize()

# Right motor
encoder_left = Encoder(23, 24)
encoder_right = Encoder(22, 25)
#              0      -0.15       0.5
pid_left = PID(P = -0.2, I = -0.005, D = -0.2, file="maintain_speed_left_seperate.csv")
pid_right = PID(P = -0.2, I = -0.005, D = -0.2, file="maintain_speed_right_seperate.csv")

TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
# TB.i2cAddress = 0x15           # Uncomment and change the value if you have changed the board address
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

prevTime = 0
prevStepLeft, prevStepRight = 0, 0
rev = random.randint(6, 10)/10
x = time.time()
y = 0.5 * math.sin((math.pi * 4) * x) + 0.5
c = 1
try:
    while True:
        cTime, stepsLeft, stepsRight = time.time(), encoder_left.getSteps(), encoder_right.getSteps()

        current_speed_left = \
            ((stepsLeft - prevStepLeft) / 3591.84) / (cTime - prevTime) * 3
        current_speed_right = \
            ((stepsRight - prevStepRight) / 3591.84) / (cTime - prevTime) * 3
        
        prevStepsRight, prevStepsLeft, prevTime = stepsRight, stepsLeft, cTime

        time.sleep(0.001)
        if c == 100:
            y = 0.5 * math.sin((math.pi * 4) * time.time()) + 0.5
            c = 0
        print(f"Speed Left: {current_speed_left}, Speed Right: {current_speed_right}, Rev: {y}")
        TB.SetMotor1(pid_left.update(y, current_speed_left))
        TB.SetMotor2(pid_right.update(y, current_speed_right))
        c += 1
except KeyboardInterrupt:
    pass

pid_left.close()
pid_right.close()
print(99)
TB.MotorsOff()
print(100)
