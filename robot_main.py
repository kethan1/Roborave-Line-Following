#!/usr/bin/env python3

# Importing modules

import sys
import time
import json
import math
import threading
from typing import Dict, Union

import cv2
import numpy as np
import picamera
import picamera.array
import RPi.GPIO as GPIO
import scipy.ndimage

import Libraries.Thunderborg as ThunderBorg
from PID import PID
from CPP_Libraries.Encoder_CPP.encoder import Encoder, init as initialize_encoder


TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
TB.i2cAddress = 0x15            # Uncomment and change the value if you have changed the board address
TB.Init()                       # Set the board up (checks the board is connected)

# TB2 = ThunderBorg.ThunderBorg()
# TB2.i2cAddress = 0x15
# TB2.Init()

# Thunderborg Checks
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print("No ThunderBorg found, check you are attached :)")
    else:
        print(f"No ThunderBorg at address {TB.i2cAddress}, but we did find boards:")
        for board in boards:
            print("    %02X (%d)" % (board, board))
        print("If you need to change the I²C address change the setup line so it is correct, e.g.")
        print("TB.i2cAddress = 0x%02X" % (boards[0]))
    sys.exit()

TB.SetBatteryMonitoringLimits(10, 13)  # Set LED Battery Indicator


def show_color(led_pins: dict, color_dict: dict, on: bool = True):
    for color, brightness in color_dict.items():
        GPIO.output(led_pins[color], int(not brightness) if on else brightness)


# Reading Configuration Values

with open("robot_config.json") as robot_config_file:
    robot_config = json.load(robot_config_file)

P_VALUE: float = robot_config["P"]
I_VALUE: float = robot_config["I"]
D_VALUE: float = robot_config["D"]
HALL_EFFECT_PIN: int = robot_config["HALL_EFFECT_PIN"]
MAINTAIN_SPEED_P: float = robot_config["MAINTAIN_SPEED_PID"]["P"]
MAINTAIN_SPEED_I: float = robot_config["MAINTAIN_SPEED_PID"]["I"]
MAINTAIN_SPEED_D: float = robot_config["MAINTAIN_SPEED_PID"]["D"]
GRAYSCALE_THRESHOLD: int = robot_config["GRAYSCALE_THRESHOLD"]
BASE_SPEED: float = robot_config["BASE_SPEED"]
INTERSECTION_PORTION: float = robot_config["INTERSECTION_PORTION"]
LED_CONFIG: Dict[str, int] = robot_config["LED_CONFIG"]
LED_COLOR_COMBOS: Dict[str, Dict[str, int]] = robot_config["LED_COLOR_COMBOS"]
CROPPING: Dict[str, Union[bool, int]] = robot_config["CROPPING"]
L298N_PINS: Dict[str, int] = robot_config["L298N_PINS"]


# Command line flags

debug = False if "--prod" in sys.argv[1:] else robot_config["debug"]
bl_wh = "--bl_wh" in sys.argv[1:]
if "--P" in sys.argv[1:]:
    P_VALUE = float(sys.argv[sys.argv.index("--P") + 1])
if "--I" in sys.argv[1:]:
    I_VALUE = float(sys.argv[sys.argv.index("--I") + 1])
if "--D" in sys.argv[1:]:
    D_VALUE = float(sys.argv[sys.argv.index("--D") + 1])

if not debug and "--print-prod" in sys.argv[1:]:
    sys.stdout = None


initialize_encoder()
encoder_left = Encoder(*robot_config["Encoder_Left"])
encoder_right = Encoder(*robot_config["Encoder_Right"])


GPIO.setmode(GPIO.BCM)
pinlistOut = list(LED_CONFIG.values()) + [*L298N_PINS.values()]
pinlistIn = [HALL_EFFECT_PIN]
# Motor1 - Right
# Motor2 - Left
GPIO.setup(pinlistOut, GPIO.OUT)
GPIO.setup(pinlistIn, GPIO.IN)
GPIO.add_event_detect(HALL_EFFECT_PIN, GPIO.FALLING)
GPIO.output(list(LED_CONFIG.values()), GPIO.HIGH)
show_color(LED_CONFIG, LED_COLOR_COMBOS["blue"])
LEFT, RIGHT = 0, 1


finish, targetSpeed, towerFound = False, 0, False
speed_separate = []
intersection_turns = [RIGHT, LEFT, LEFT] * 10
intersection_turns_index = 0
rev_per_second = PID(P=P_VALUE, I=I_VALUE, D=D_VALUE, debug=debug,
                     file="rev_per_second.csv")
maintain_speed_PID_left = PID(P=MAINTAIN_SPEED_P, I=MAINTAIN_SPEED_I,
                              D=MAINTAIN_SPEED_D,
                              file="maintain_speed_left.csv")
maintain_speed_PID_right = PID(P=MAINTAIN_SPEED_P, I=MAINTAIN_SPEED_I,
                               D=MAINTAIN_SPEED_D,
                               file="maintain_speed_right.csv")


def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)


# A seperate function that runs the PID that adjusts the motor speed depending
# on the encoders. This allows the robot to run smoothly on many surfaces. This
# function runs in a separate thread.
def set_speed():
    global targetSpeed
    prevStepsLeft = prevStepsRight = prevTime = 0

    # To get the speed from the encoders, we can track the numbers of steps
    # between now and a previous time
    while not finish:
        cTime, stepsLeft, stepsRight = time.time(), encoder_left.getSteps(), \
            encoder_right.getSteps()

        current_speed_left = \
            ((stepsLeft - prevStepsLeft) / 3591.84) / (cTime - prevTime) * 3
        current_speed_right = \
            ((stepsRight - prevStepsRight) / 3591.84) / (cTime - prevTime) * 3
        prevStepsRight, prevStepsLeft, prevTime = stepsRight, stepsLeft, cTime

        if speed_separate:
            speed_left = maintain_speed_PID_left.update(speed_separate[0],
                                                        current_speed_left)
            speed_right = maintain_speed_PID_right.update(speed_separate[1],
                                                          current_speed_right)
        elif targetSpeed != 0:
            speed_left = maintain_speed_PID_left.update(
                BASE_SPEED - targetSpeed, current_speed_left)
            speed_right = maintain_speed_PID_right.update(
                BASE_SPEED + targetSpeed, current_speed_right)
        else:
            speed_left = speed_right = 0

        # If the motors drop too low, they won"t move. This brings up the
        # power level to 0.15 if it is lower than that.
        if speed_separate or targetSpeed != 0:
            speed_left = speed_left if abs(speed_left) > 0.15 else \
                math.copysign(0.15, speed_left)
            speed_right = speed_right if abs(speed_right) > 0.15 else \
                math.copysign(0.15, speed_right)

        TB.SetMotor1(speed_left)
        TB.SetMotor2(speed_right)
        time.sleep(0.01)

    maintain_speed_PID_left.close()
    maintain_speed_PID_right.close()


set_speed_thread = threading.Thread(target=set_speed)


# Ending program function -- Closes everything
def end_program():
    global finish
    # global hall_effect_sensor

    print("Ending Program")
    finish = True
    cv2.destroyAllWindows()
    GPIO.output(list(LED_CONFIG.values()), GPIO.LOW)
    # del hall_effect_sensor
    GPIO.cleanup()
    rev_per_second.close()
    set_speed_thread.join()
    TB.MotorsOff()
    sys.exit()


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        # Capture 40 frames to get the camera to warmup
        for _ in range(40):
            camera.capture(stream, "bgr", use_video_port=True)
            image = stream.array

            imshow_debug("Video Stream with Circle", image)

            stream.seek(0)
            stream.truncate()

        GPIO.output(LED_CONFIG["blue"], GPIO.LOW)
        GPIO.output(LED_CONFIG["green"], GPIO.HIGH)
        set_speed_thread.start()

        try:
            while True:
                camera.capture(stream, "bgr", use_video_port=True)
                image = stream.array

                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY_INV
                )

                height, width = grayscale_image.shape

                if CROPPING["do"]:
                    cv2.rectangle(
                        grayscale_image, (0, 0),
                        (CROPPING["left"] * width, height)
                    )
                    cv2.rectangle(
                        grayscale_image,
                        (width - (CROPPING["right"] * width), 0),
                        (height, width)
                    )
                    cv2.rectangle(
                        grayscale_image, (0, 0),
                        (width, CROPPING["top"] * height)
                    )

                grayscale_image_resized = cv2.resize(
                    grayscale_image, dsize=(
                        int(image.shape[1] * 0.4), int(image.shape[0] * 0.4)
                    ),
                    interpolation=cv2.INTER_AREA
                )

                pixels_sum = np.sum(grayscale_image_resized, 1)
                max_pixels_pos = np.argmax(pixels_sum)
                max_pixels = pixels_sum[max_pixels_pos] / 255

                if grayscale_image_resized.shape[1] * INTERSECTION_PORTION <= max_pixels:
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["yellow"])
                    print("Intersection spotted")
                    print(f"{max_pixels/grayscale_image_resized.shape[1]}, max_pixels_pos={max_pixels_pos}")

                    print("Going through the intersection")

                    speed_separate = [1.2, 1.2]
                    # need a mx + b equation because we need to move a so that
                    # the start of the robot"s camera is at the intersection,
                    # and then move a certain amount forward so that the
                    # center of mass of the robot is over the intersection
                    time.sleep((0.0017 * (grayscale_image_resized.shape[0] - max_pixels_pos)) + 0.12)

                    if not towerFound:
                        if intersection_turns[intersection_turns_index] == RIGHT:
                            print("Turning Right for Intersection")
                            speed_separate = [1.2, -1.2]
                        elif intersection_turns[intersection_turns_index] == LEFT:
                            print("Turning Left for Intersection")
                            speed_separate = [-1.2, 1.2]
                    else:
                        if intersection_turns[intersection_turns_index] == LEFT:
                            print("Turning Right for Intersection")
                            speed_separate = [1.2, -1.2]
                        elif intersection_turns[intersection_turns_index] == RIGHT:
                            print("Turning Left for Intersection")
                            speed_separate = [-1.2, 1.2]
                    time.sleep(0.475)
                    speed_separate = []
                    targetSpeed = 0

                    intersection_turns_index += 1
                    if intersection_turns_index > len(intersection_turns) - 1:
                        intersection_turns_index = len(intersection_turns) - 1

                    stream.seek(0)
                    stream.truncate()
                else:
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["green"])

                height, width = grayscale_image.shape

                line_found = False
                for current_y in range(height, 0, -20):
                    cropped_image = grayscale_image[current_y: current_y + 20, 0: -1]
                    if np.sum(cropped_image) > 20*255 and current_y + 20 < height:
                        line_found = True
                        center_of_mass_y, center_of_mass_x = \
                            scipy.ndimage.center_of_mass(cropped_image)
                        break

                # Criterea for line lost
                if not line_found or (np.sum(grayscale_image) < 50 * 255):
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["red"])
                    print("Line Lost")
                    targetSpeed = 0
                    # Moving backwards until line found again
                    speed_separate = [-1, -1]
                    time.sleep(0.2)
                    speed_separate = []

                    stream.seek(0)
                    stream.truncate()
                    continue
                else:
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["green"])

                targetSpeed_tmp = rev_per_second.update(width/2, center_of_mass_x)
                targetSpeed = targetSpeed_tmp if abs(targetSpeed_tmp) <= 1.4 \
                    else math.copysign(1.4, targetSpeed_tmp)

                if not bl_wh:
                    imshow_debug(
                        "Video Stream with Circle",
                        cv2.circle(image, (
                                round(center_of_mass_x),
                                current_y + round(center_of_mass_y)
                            ),
                            10, (0, 0, 255), 10
                        )
                    )
                else:
                    imshow_debug("Video Stream with Circle", cv2.circle(
                            cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR),
                            (
                                round(center_of_mass_x),
                                current_y + round(center_of_mass_y)
                            ), 10, (0, 0, 255), 10
                        )
                    )

                stream.seek(0)
                stream.truncate()

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if GPIO.event_detected(HALL_EFFECT_PIN) and not towerFound:
                    towerFound = True
                    intersection_turns.reverse()
                    intersection_turns_index = 0
                    print("Magnet detected")
                    targetSpeed = 0
                    GPIO.output(L298N_PINS["FORWARD"], GPIO.HIGH)
                    time.sleep(5)
                    GPIO.output(L298N_PINS["FORWARD"], GPIO.LOW)
                    speed_separate = [-1.2, -1.2]
                    time.sleep(0.5)
                    speed_separate = [-1.2, 1.2]
                    time.sleep(0.8)
                    speed_separate = []
        except KeyboardInterrupt:
            end_program()

if not finish:
    end_program()
