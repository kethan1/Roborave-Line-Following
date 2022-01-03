#!/usr/bin/env python3

import time
import encoder

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

encoder.init()
encoder1 = encoder.Encoder(23, 24)
encoder2 = encoder.Encoder(22, 25)
prevSteps1 = 0
prevSteps2 = 0
prevTime = 0
try:
    while True:
        cTime = time.time()
        steps1, steps2 = encoder1.getSteps(), encoder2.getSteps()
        speed1 = (steps1 - prevSteps1) / (cTime - prevTime) * 3
        speed2 = (steps2 - prevSteps2) / (cTime - prevTime) * 3
        prevTime = cTime
        prevSteps1, prevSteps2 = steps1, steps2
        print(
            f"1, Steps: {encoder1.getSteps()}, Direction: {encoder1.getDirection()}, Speed in rev/sec: {speed1 / 3591.84}"
        )
        print(
            f"2, Steps: {encoder2.getSteps()}, Direction: {encoder2.getDirection()}, Speed in rev/sec: {speed2 / 3591.84}"
        )
        time.sleep(1)
except KeyboardInterrupt:
    pass
