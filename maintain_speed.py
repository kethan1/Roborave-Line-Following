#!/usr/bin/env python3

from PID import PID
from CPP_Libraries.Encoder_CPP.encoder import Encoder, init as initialize_encoder
import Libraries.Thunderborg as ThunderBorg


import time
import sys
import math

initialize_encoder()

# Right motor
encoder_left = Encoder(22, 25)
encoder_right = Encoder(23, 24)
#              0      -0.15       0.5
pid_left = PID(P=2.0, I=0.025, D=1.8, file="maintain_speed_left_seperate.csv")
pid_right = PID(P=2.0, I=0.025, D=1.8, file="maintain_speed_right_seperate.csv")

TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
TB.i2cAddress = (
    0x15  # Uncomment and change the value if you have changed the board address
)
TB.Init()  # Set the board up (checks the board is connected)
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

prevTime = time.time()
prevStepsLeft, prevStepsRight = 0, 0
y = 0.5 * math.sin((math.pi * 4) * time.time()) + 0.5
# y = 1
last_five_encoder_values = {"left": [], "right": []}
try:
    while True:
        cTime, stepsLeft, stepsRight = (
            time.time(),
            encoder_left.getSteps(),
            encoder_right.getSteps(),
        )

        if len(last_five_encoder_values["left"]) < 5:
            last_five_encoder_values["left"].append(stepsLeft - prevStepsLeft)
            last_five_encoder_values["right"].append(stepsRight - prevStepsRight)
        else:
            last_five_encoder_values["left"] = last_five_encoder_values["left"][1:] + [
                stepsLeft - prevStepsLeft
            ]
            last_five_encoder_values["right"] = last_five_encoder_values["right"][
                1:
            ] + [stepsRight - prevStepsRight]

        current_speed_left = (
            (
                sum(last_five_encoder_values["left"])
                / len(last_five_encoder_values["left"])
            )
            / (cTime - prevTime)
            * 3
        ) / 3591.84
        current_speed_right = (
            (
                sum(last_five_encoder_values["right"])
                / len(last_five_encoder_values["right"])
            )
            / (cTime - prevTime)
            * 3
        ) / 3591.84

        current_speed_left = (
            (stepsLeft - prevStepsLeft) / (cTime - prevTime) * 3
        ) / 3591.84
        current_speed_right = (
            (stepsRight - prevStepsRight) / (cTime - prevTime) * 3
        ) / 3591.84

        y = 0.5 * math.sin((math.pi * 4) * time.time()) + 0.5
        print(
            f"stepsLeft: {stepsLeft}, Steps Change: {stepsLeft - prevStepsLeft}, Current Speed Left: {current_speed_left}, Speed Left: {sum(last_five_encoder_values['left']) / len(last_five_encoder_values['left'])}, Rev: {y}"
        )
        print(
            f"stepsRight: {stepsRight}, Steps Change: {stepsRight - prevStepsRight}, Current Speed Right: {current_speed_right}, Speed Right: {sum(last_five_encoder_values['right']) / len(last_five_encoder_values['right'])}, Rev: {y}"
        )

        TB.SetMotor1(pid_left.update(y, current_speed_left))
        TB.SetMotor2(pid_right.update(y, current_speed_right))
        prevStepsRight, prevStepsLeft, prevTime = stepsRight, stepsLeft, cTime
        time.sleep(0.005)
except KeyboardInterrupt:
    pid_left.close()
    pid_right.close()
    TB.MotorsOff()
