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
pid_left = PID(P = 2.0, I = 0.025, D = 1.8, file="maintain_speed_left_seperate.csv")
pid_right = PID(P = 2.0, I = 0.025, D = 1.8, file="maintain_speed_right_seperate.csv")

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
prevStepsLeft, prevStepsRight = 0, 0
rev = random.randint(6, 10) / 10
x = time.time()
y = 0.5 * math.sin((math.pi * 4) * x) + 0.5
y = 1
c = 1
last_five_encoder_values = {
    "left": [],
    "right": []
}
try:
    while True:
        x += 1
        cTime, stepsLeft, stepsRight = \
            time.time(), encoder_left.getSteps(), encoder_right.getSteps()

        if len(last_five_encoder_values['left']) < 5:
            last_five_encoder_values['left'].append(stepsLeft - prevStepsLeft)
            last_five_encoder_values['right'].append(stepsRight - prevStepsRight)
        else:
            last_five_encoder_values["left"] = \
                last_five_encoder_values['left'][1:] + [stepsLeft - prevStepsLeft]
            last_five_encoder_values["right"] = \
                last_five_encoder_values['right'][1:] + [stepsRight - prevStepsRight]

        current_speed_left = \
            ((sum(last_five_encoder_values['left']) / len(last_five_encoder_values['left'])) / (cTime - prevTime) * 3) / 3591.84
        current_speed_right = \
            ((sum(last_five_encoder_values['right']) / len(last_five_encoder_values['right'])) / (cTime - prevTime) * 3) / 3591.84

        # if c == 100:
        y = 0.5 * math.sin((math.pi * 4) * time.time()) + 0.5
        # y = 1
        # c = 0
        print(f"stepsLeft: {stepsLeft}, Steps Change: {stepsLeft - prevStepsLeft}, Current Speed Left: {current_speed_left}, Speed Left: {sum(last_five_encoder_values['left']) / len(last_five_encoder_values['left'])}, Rev: {y}")
        print(f"stepsRight: {stepsRight}, Steps Change: {stepsRight - prevStepsRight}, Current Speed Right: {current_speed_right}, Speed Right: {sum(last_five_encoder_values['right']) / len(last_five_encoder_values['right'])}, Rev: {y}")

        TB.SetMotor1(
            pid_left.update(
                # 1.75 if y > 1.75 else y,
                y,
                current_speed_left
            )
        )
        TB.SetMotor2(
            pid_right.update(
                # 1.75 if y > 1.75 else y,
                y,
                current_speed_right
            )
        )
        prevStepsRight, prevStepsLeft, prevTime = stepsRight, stepsLeft, cTime
        time.sleep(0.005)

        c += 1
except KeyboardInterrupt:
    pid_left.close()
    pid_right.close()
    print(99)
    TB.MotorsOff()
    print(100)
