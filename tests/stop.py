# GPIO 25 - Encoder A for Motor1
# GPIO 22 - Encoder B for Motor1
# GPIO 24 - Encoder A for Motor2
# GPIO 23 - Encoder B for Motor2
import os
import sys
import inspect
import json
from typing import Dict

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    ),
)

import Libraries.Thunderborg as ThunderBorg
import RPi.GPIO as GPIO

with open(
    os.path.join(os.path.dirname(__file__), "..", "robot_config.json")
) as robot_config_file:
    robot_config = json.load(robot_config_file)
L298N_PINS: Dict[str, int] = robot_config["L298N_PINS"]

GPIO.setmode(GPIO.BCM)
GPIO.setup(list(L298N_PINS.values()), GPIO.OUT)


TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
TB.Init()

# Set the board up (checks the board is connected)
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
    # sys.exit()

TB.MotorsOff()

GPIO.output(list(L298N_PINS.values()), GPIO.LOW)
GPIO.cleanup()
