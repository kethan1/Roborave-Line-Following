#!/usr/bin/env python3

from PID import PID
from Encoder_CPP.encoder import Encoder, init as initialize
import Libraries.ThunderBorg3 as ThunderBorg

import time
import sys
import random

initialize()

# Right motor
encoder = Encoder(23, 24)
#              0      -0.15       0.5
pid1 = PID(P = -1, I = -0.05, D = 0.9, file="maintain_speed.csv")

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
prevSteps = 0
rev = random.randint(6, 10)/10
# direction = random.randint(1, 2)
# rev = -rev if direction == 2 else rev
c = 1
try:
    while True:
        cTime = time.time()
        steps = encoder.getSteps()
        speed = ((steps - prevSteps) / (cTime - prevTime) / 3591.84) * 3
        prevTime = cTime
        prevSteps = steps
        time.sleep(0.01)
        if c == 10:
            rev = random.randint(6, 10)/10
            # direction = random.randint(1, 2)
            # rev = -rev if direction == 2 else rev
            c = 0
        # print(f"Speed: {speed}, Rev: {rev}")
        TB.SetMotor1(pid1.update(rev, speed))
        if abs(speed - rev) > 0.15:
            if c > 5:
                print(f"worry worry worry, Speed: {speed}, rev: {rev}")
        c += 1
except KeyboardInterrupt:
    pass

pid1.close()
print(99)
TB.MotorsOff()
print(100)
