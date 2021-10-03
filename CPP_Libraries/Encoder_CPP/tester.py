#!/usr/bin/env python3

import time
import encoder

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

encoder.init()
encoder1 = encoder.Encoder(23, 24)
prevSteps = 0
prevTime = 0
try:
    while True:
        cTime = time.time()
        steps = encoder1.getSteps()
        speed = (steps - prevSteps) / (cTime - prevTime) * 3
        prevTime = cTime
        prevSteps = steps
        print(
            f"Steps: {encoder1.getSteps()}, Direction: {encoder1.getDirection()}, Speed in rev/sec: {speed / 3591.84}"
        )
        time.sleep(1)
except KeyboardInterrupt:
    pass
