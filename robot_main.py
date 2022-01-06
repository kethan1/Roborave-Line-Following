#!/usr/bin/env python3

# Importing modules

import sys
import time
import json
import math
import threading
import argparse
from typing import Dict, Union, List

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
TB.Init()  # Set the board up (checks the board is connected)

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


def show_color(led_pins: dict, color_dict: dict, on: bool = True):
    for color, brightness in color_dict.items():
        GPIO.output(led_pins[color], int(not brightness) if on else brightness)


# Reading Configuration Values

with open("robot_config.json") as robot_config_file:
    robot_config = json.load(robot_config_file)

HALL_EFFECT_PIN: int = robot_config["HALL_EFFECT_PIN"]
MAINTAIN_SPEED_P: float = robot_config["MAINTAIN_SPEED_PID"]["P"]
MAINTAIN_SPEED_I: float = robot_config["MAINTAIN_SPEED_PID"]["I"]
MAINTAIN_SPEED_D: float = robot_config["MAINTAIN_SPEED_PID"]["D"]
GRAYSCALE_THRESHOLD: int = robot_config["GRAYSCALE_THRESHOLD"]
BASE_SPEED: float = robot_config["BASE_SPEED"]
INTERSECTION_PORTION: float = robot_config["INTERSECTION_PORTION"]
LED_CONFIG: Dict[str, int] = robot_config["LED_CONFIG"]
LED_COLOR_COMBOS: Dict[str, Dict[str, int]] = robot_config["LED_COLOR_COMBOS"]
CROPPING: Dict[str, Union[bool, float]] = robot_config["CROPPING"]
L298N_PINS: Dict[str, int] = robot_config["L298N_PINS"]
STOP_SWITCH: int = robot_config["STOP_SWITCH"]
TIMING_SWITCH: int = robot_config["TIMING_SWITCH"]
INTERSECTION_TIMING: Dict[str, float] = robot_config["INTERSECTION_TIMINGS"]
ONE_BALL_UNLOADING: int = robot_config["ONE_BALL_UNLOADING"]
MANY_BALL_UNLOADING: int = robot_config["MANY_BALL_UNLOADING"]


# Command line flags

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--prod", help="production or not, if production does not show video",
                    action="store_true", default=not robot_config["debug"])
parser.add_argument("-bw", "--bl-wh", help="controls whether the display",
                    action="store_true", default=False)
parser.add_argument("-np", "--no-print", help="whether to print or not",
                    action="store_true", default=False)

parser.add_argument("--P", help="controls the P term for the rev per second PID",
                    type=float, default=robot_config["P"])
parser.add_argument("--I", help="controls the I term for the rev per second PID",
                    type=float, default=robot_config["I"])
parser.add_argument("--D", help="controls the D term for the rev per second PID",
                    type=float, default=robot_config["D"])

args = parser.parse_args()


DEBUG = not args.prod
BL_WH = args.bl_wh
P_VALUE = args.P
I_VALUE = args.I
D_VALUE = args.D

if args.no_print:
    sys.stdout = None


initialize_encoder()
encoder_left = Encoder(*robot_config["Encoder_Left"])
encoder_right = Encoder(*robot_config["Encoder_Right"])


GPIO.setmode(GPIO.BCM)
pinlist_out = list(LED_CONFIG.values()) + [*L298N_PINS.values()]
pinlist_in = [HALL_EFFECT_PIN]
pinlist_in_pull_down = [TIMING_SWITCH, STOP_SWITCH]
# Motor1 - Right
# Motor2 - Left
GPIO.setup(pinlist_out, GPIO.OUT)
GPIO.setup(pinlist_in, GPIO.IN)
GPIO.setup(pinlist_in_pull_down, GPIO.IN, GPIO.PUD_DOWN)
GPIO.add_event_detect(HALL_EFFECT_PIN, GPIO.FALLING)
GPIO.add_event_detect(STOP_SWITCH, GPIO.BOTH)
GPIO.add_event_detect(TIMING_SWITCH, GPIO.BOTH)
GPIO.output(list(LED_CONFIG.values()), GPIO.HIGH)
show_color(LED_CONFIG, LED_COLOR_COMBOS["blue"])
LEFT, RIGHT = 0, 1


finish = towerFound = False
target_speed: int = 0
ball_unloading_time: int = ONE_BALL_UNLOADING
speed_separate: List[int] = []
manual_speed_control: List[int] = []
stop_flag: bool = False
intersection_turns = [LEFT if turn == "LEFT" else RIGHT for turn in robot_config["intersection_turns"]]
intersection_turns_index = 0
rev_per_second = PID(
    P=P_VALUE, I=I_VALUE, D=D_VALUE, debug=DEBUG, file="rev_per_second.csv"
)
maintain_speed_PID_left = PID(
    P=MAINTAIN_SPEED_P,
    I=MAINTAIN_SPEED_I,
    D=MAINTAIN_SPEED_D,
    file="maintain_speed_left.csv",
)
maintain_speed_PID_right = PID(
    P=MAINTAIN_SPEED_P,
    I=MAINTAIN_SPEED_I,
    D=MAINTAIN_SPEED_D,
    file="maintain_speed_right.csv",
)


def imshow_debug(image_to_show, title):
    if DEBUG:
        cv2.imshow(image_to_show, title)


def reverse_intersection_turns():
    print("Reversing Intersection Turns")
    if len(intersection_turns) > 1:
        intersection_turns[0], intersection_turns[-1] = 1 - intersection_turns[-1], 1 - intersection_turns[0]
    elif len(intersection_turns) > 0:
        print(intersection_turns[0])
        intersection_turns[0] = 1 - intersection_turns[0]
        print(intersection_turns[0])


# A seperate function that runs the PID that adjusts the motor speed depending
# on the encoders. This allows the robot to run smoothly on many surfaces. This
# function runs in a separate thread.
def set_speed():
    global target_speed
    prevStepsLeft = prevStepsRight = prevTime = 0

    lock = threading.RLock()

    # To get the speed from the encoders, we can track the numbers of steps
    # between now and a previous time
    while not finish:
        cTime, stepsLeft, stepsRight = (
            time.time(),
            encoder_left.getSteps(),
            encoder_right.getSteps(),
        )

        current_speed_left = (
            ((stepsLeft - prevStepsLeft) / 3591.84) / (cTime - prevTime) * 3
        )
        current_speed_right = (
            ((stepsRight - prevStepsRight) / 3591.84) / (cTime - prevTime) * 3
        )
        prevStepsRight, prevStepsLeft, prevTime = stepsRight, stepsLeft, cTime

        with lock:
            if stop_flag:
                speed_left = speed_right = 0
            elif speed_separate:
                speed_left = maintain_speed_PID_left.update(
                    speed_separate[0], current_speed_left
                )
                speed_right = maintain_speed_PID_right.update(
                    speed_separate[1], current_speed_right
                )
            elif manual_speed_control:
                speed_left, speed_right = manual_speed_control
            else:
                speed_left = maintain_speed_PID_left.update(
                    BASE_SPEED - target_speed, current_speed_left
                )
                speed_right = maintain_speed_PID_right.update(
                    BASE_SPEED + target_speed, current_speed_right
                )

        # If the motors drop too low, they won"t move. This brings up the
        # power level to 0.15 if it is lower than that.
        with lock:
            if speed_separate or target_speed != 0:
                speed_left = (
                    speed_left
                    if abs(speed_left) > 0.15
                    else math.copysign(0.15, speed_left)
                )
                speed_right = (
                    speed_right
                    if abs(speed_right) > 0.15
                    else math.copysign(0.15, speed_right)
                )

        TB.SetMotor1(speed_left)
        TB.SetMotor2(speed_right)
        time.sleep(0.005)

    maintain_speed_PID_left.close()
    maintain_speed_PID_right.close()


set_speed_thread = threading.Thread(target=set_speed)


# Ending program function -- Closes everything
def end_program():
    global finish

    print("Ending Program")
    finish = True
    cv2.destroyAllWindows()
    GPIO.output(list(LED_CONFIG.values()), GPIO.LOW)
    GPIO.cleanup()
    rev_per_second.close()
    set_speed_thread.join()
    TB.MotorsOff()
    sys.exit()


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        lock = threading.RLock()
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
                    GRAYSCALE_THRESHOLD,
                    255,
                    cv2.THRESH_BINARY_INV,
                )

                height, width = grayscale_image.shape

                grayscale_image_resized = cv2.resize(
                    grayscale_image,
                    dsize=(int(image.shape[1] * 0.4), int(image.shape[0] * 0.4)),
                    interpolation=cv2.INTER_AREA,
                )

                if CROPPING["do"]:
                    cv2.rectangle(
                        grayscale_image, (0, 0), (int(CROPPING["left"] * width), height), (0, 0, 0), -1
                    )
                    cv2.rectangle(
                        grayscale_image, (width - (int(CROPPING["right"] * width)), 0), (width, height),
                        (0, 0, 0), -1
                    )
                    cv2.rectangle(
                        grayscale_image, (0, 0), (width, int(CROPPING["top"] * height)), (0, 0, 0), -1
                    )

                pixels_sum = np.sum(grayscale_image_resized, 1)
                max_pixels_pos = np.argmax(pixels_sum)
                max_pixels = pixels_sum[max_pixels_pos] / 255

                if (
                    grayscale_image_resized.shape[1] * INTERSECTION_PORTION
                    <= max_pixels
                ):
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["yellow"])
                    print("Intersection spotted")
                    print(
                        f"{max_pixels/grayscale_image_resized.shape[1]}, max_pixels_pos={max_pixels_pos}"
                    )

                    print("Going through the intersection")

                    speed_separate = [1.2, 1.2]
                    # need a mx + b equation because we need to move a so that
                    # the start of the robot"s camera is at the intersection,
                    # and then move a certain amount forward so that the
                    # center of mass of the robot is over the intersection
                    time.sleep(
                        (INTERSECTION_TIMING["M"] * (grayscale_image_resized.shape[0] - max_pixels_pos))
                        + INTERSECTION_TIMING["B"]
                    )

                    if intersection_turns[intersection_turns_index] == RIGHT:
                        print("Turning Right for Intersection")
                        speed_separate = [1, -1]
                    elif intersection_turns[intersection_turns_index] == LEFT:
                        print("Turning Left for Intersection")
                        speed_separate = [-1, 1]
                    time.sleep(INTERSECTION_TIMING["turning_timing"])
                    speed_separate = []
                    target_speed = 0

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
                    cropped_image = grayscale_image[current_y : current_y + 20, 0:-1]
                    if np.sum(cropped_image) > 20 * 255 and current_y + 20 < height:
                        line_found = True
                        (
                            center_of_mass_y,
                            center_of_mass_x,
                        ) = scipy.ndimage.center_of_mass(cropped_image)
                        break

                # Criteria for line lost
                if not line_found or (np.sum(grayscale_image) < 50 * 255):
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["red"])
                    print("Line Lost")
                    # Moving backwards until line found again
                    manual_speed_control = [-0.4, -0.4]
                    time.sleep(0.2)
                    manual_speed_control = []
                    # end_program()

                    stream.seek(0)
                    stream.truncate()
                    continue
                else:
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["green"])

                target_speed_tmp = rev_per_second.update(width / 2, center_of_mass_x)
                with lock:
                    target_speed = (
                        target_speed_tmp
                        if abs(target_speed_tmp) <= 1.4
                        else math.copysign(1.4, target_speed_tmp)
                    )

                if not BL_WH:
                    imshow_debug(
                        "Video Stream with Circle",
                        cv2.circle(
                            image,
                            (
                                round(center_of_mass_x),
                                current_y + round(center_of_mass_y),
                            ),
                            10,
                            (0, 0, 255),
                            10,
                        ),
                    )
                else:
                    imshow_debug(
                        "Video Stream with Circle",
                        cv2.circle(
                            cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR),
                            (
                                round(center_of_mass_x),
                                current_y + round(center_of_mass_y),
                            ),
                            10,
                            (0, 0, 255),
                            10,
                        ),
                    )

                stream.seek(0)
                stream.truncate()

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if GPIO.event_detected(HALL_EFFECT_PIN) and not towerFound:
                    towerFound = True
                    reverse_intersection_turns()
                    intersection_turns_index = 0
                    print("Magnet detected")
                    stop_flag = True
                    target_speed = 0
                    speed_separate = []
                    GPIO.output(L298N_PINS["FORWARD"], GPIO.HIGH)
                    time.sleep(ball_unloading_time)
                    GPIO.output(L298N_PINS["FORWARD"], GPIO.LOW)
                    stop_flag = False
                    speed_separate = [-1.2, -1.2]
                    time.sleep(0.6)
                    speed_separate = [-1.2, 1.2]
                    time.sleep(0.95)
                    speed_separate = []

                if GPIO.event_detected(TIMING_SWITCH):
                    unloading_time = MANY_BALL_UNLOADING \
                        if unloading_time == ONE_BALL_UNLOADING \
                        else MANY_BALL_UNLOADING

                if GPIO.event_detected(STOP_SWITCH):
                    print("Stop Switch Detected")
                    towerFound = False
                    target_speed = 0
                    speed_separate = [-1.2, 1.2]
                    time.sleep(0.95)
                    speed_separate = []
                    show_color(LED_CONFIG, LED_COLOR_COMBOS["blue"])
                    reverse_intersection_turns()
                    intersection_turns_index = 0

                    stop_flag = True

                    wait = GPIO.wait_for_edge(STOP_SWITCH, GPIO.BOTH)
                    time.sleep(1)

                    print("Switch Press Detected, Continuing Program")
                    GPIO.event_detected(STOP_SWITCH)
                    if wait is None:
                        print("Timeout for stop switch was trigged")
                    else:
                        pass
                    stop_flag = False
        except KeyboardInterrupt:
            end_program()

if not finish:
    end_program()
