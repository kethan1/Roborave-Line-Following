#!/usr/bin/env python3

import sys
import time
import json
import math
# import timeit
import threading
import os

import cv2
import numpy as np
import picamera
import picamera.array
import RPi.GPIO as GPIO
import scipy.ndimage

import Libraries.ThunderBorg3 as ThunderBorg
from PID import PID
from hall_effect_sensor import Hall_Effect_Sensor
from CPP_Libraries.Encoder_CPP.encoder import Encoder, init as initialize_encoder


TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
# TB.i2cAddress = 0x15          # Uncomment and change the value if you have changed the board address
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

TB.SetBatteryMonitoringLimits(10, 13)  # Set LED Battery Indicator

with open("robot_config.json") as robot_config_file:
    robot_config = json.load(robot_config_file)

P_VALUE = robot_config["P"]
I_VALUE = robot_config["I"]
D_VALUE = robot_config["D"]
MAINTAIN_SPEED_P_VALUE = robot_config["MAINTAIN_SPEED_PID"]["P"]
MAINTAIN_SPEED_I_VALUE = robot_config["MAINTAIN_SPEED_PID"]["I"]
MAINTAIN_SPEED_D_VALUE = robot_config["MAINTAIN_SPEED_PID"]["D"]
GRAYSCALE_THRESHOLD = robot_config["GRAYSCALE_THRESHOLD"]
BASE_SPEED = robot_config["BASE_SPEED"]

debug = False if "--prod" in sys.argv[1:] else robot_config["debug"]
bl_wh = True if "--bl_wh" in sys.argv[1:] else False
if "--P" in sys.argv[1:]:
    P_VALUE = float(sys.argv[sys.argv.index("--P") + 1])
if "--I" in sys.argv[1:]:
    I_VALUE = float(sys.argv[sys.argv.index("--I") + 1])
if "--D" in sys.argv[1:]:
    D_VALUE = float(sys.argv[sys.argv.index("--D") + 1])

if not debug and "--print-prod" in sys.argv[1:]:
    sys.stdout = None


def magnet_callback():
    global speed_separate, targetSpeed
    speed_separate, targetSpeed = [], 0
    end_program()


initialize_encoder()
encoder_left = Encoder(*robot_config["Encoder_Left"])
encoder_right = Encoder(*robot_config["Encoder_Right"])
hall_effect_sensor = Hall_Effect_Sensor(16, magnet_callback)


GPIO.setmode(GPIO.BCM)
pinlistOut = []
pinlistIn = [25, 22, 24, 23]
# Motor1 - Right
# Motor2 - Left
GPIO.setup(pinlistOut, GPIO.OUT)
GPIO.setup(pinlistIn, GPIO.IN)
GPIO.output(pinlistOut, 0)
LEFT, RIGHT = 0, 1


image, finish, targetSpeed, towerFound = None, False, 0, False
speed_separate = []
intersection_turns = [RIGHT, LEFT, LEFT]
intersection_turns_index = 0
rev_per_second = PID(P=P_VALUE, I=I_VALUE, D=D_VALUE, debug=debug, file="rev_per_second.csv")
maintain_speed_PID_left = PID(P=MAINTAIN_SPEED_P_VALUE, I=MAINTAIN_SPEED_I_VALUE, D=MAINTAIN_SPEED_D_VALUE, file="maintain_speed_left.csv")
maintain_speed_PID_right = PID(P=MAINTAIN_SPEED_P_VALUE, I=MAINTAIN_SPEED_I_VALUE, D=MAINTAIN_SPEED_D_VALUE, file="maintain_speed_right.csv")


def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)


def set_speed():
    global targetSpeed
    prevStepsLeft = prevStepsRight = prevTime = 0

    while not finish:
        cTime, stepsLeft, stepsRight = time.time(), encoder_left.getSteps(), encoder_right.getSteps()

        current_speed_left = \
            ((stepsLeft - prevStepsLeft) / 3591.84) / (cTime - prevTime) * 3
        current_speed_right = \
            ((stepsRight - prevStepsRight) / 3591.84) / (cTime - prevTime) * 3
        prevStepsRight, prevStepsLeft, prevTime = stepsRight, stepsLeft, cTime

        if not speed_separate:
            if targetSpeed != 0:
                speed_left = maintain_speed_PID_left.update(BASE_SPEED + targetSpeed, current_speed_left)
                speed_right = maintain_speed_PID_right.update(BASE_SPEED - targetSpeed, current_speed_right)
            else:
                speed_left = speed_right = 0
        elif speed_separate:
            speed_left = maintain_speed_PID_left.update(speed_separate[0], current_speed_left)
            speed_right = maintain_speed_PID_right.update(speed_separate[1], current_speed_right)

        if speed_separate or targetSpeed != 0:
            if speed_left > 0:
                speed_left = speed_left if speed_left > 0.15 else 0.15
            else:
                speed_left = speed_left if speed_left < -0.15 else -0.15
            if speed_right > 0:
                speed_right = speed_right if speed_right > 0.15 else 0.15
            else:
                speed_right = speed_right if speed_right < -0.15 else -0.15

        # print(f"Speed Left: {speed_left}, Speed Right: {speed_right}, targetSpeed: {targetSpeed}, current_speed_left: {current_speed_left}, current_speed_right: {current_speed_right}")

        # If the motors drop too low, they won't move. This brings up the
        # power level to 0.15 if it is lower than that.
        # speed_left = speed_left if speed_left > 0.15 else 0.15
        # speed_right = speed_right if speed_right > 0.15 else 0.15

        TB.SetMotor1(speed_left)
        TB.SetMotor2(speed_right)
        time.sleep(0.005)

    maintain_speed_PID_left.close()
    maintain_speed_PID_right.close()


set_speed_thread = threading.Thread(target=set_speed)


def end_program():
    global finish

    print("Ending Program")
    finish = True
    cv2.destroyAllWindows()
    TB.MotorsOff()
    GPIO.cleanup()
    rev_per_second.close()
    set_speed_thread.join()
    sys.exit()


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        # time.sleep(1)  # Allow camera warmup
        for _ in range(40):
            camera.capture(stream, "bgr", use_video_port=True)
            image = stream.array

            imshow_debug("Video Stream with Circle", image)

            stream.seek(0)
            stream.truncate()

        set_speed_thread.start()

        while True:
            try:
                # start_time = timeit.default_timer()
                camera.capture(stream, "bgr", use_video_port=True)
                image = stream.array

                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY_INV
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

                if grayscale_image_resized.shape[1] * 0.9 <= max_pixels:
                    print("Intersection spotted")
                    print(f"{max_pixels/grayscale_image_resized.shape[1]}, max_pixels_pos={max_pixels_pos}")

                    print("Going through the intersection")

                    speed_separate = [1.2, 1.2]
                    # need a mx + b equation because we need to move a so that
                    # the start of the robot's camera is at the intersection,
                    # and then move a certain amount forward so that the
                    # center of mass of the robot is over the intersection
                    time.sleep((abs(grayscale_image_resized.shape[0] - max_pixels_pos) * 0.00057) + 0.15)

                    if not towerFound:
                        if intersection_turns[intersection_turns_index] == RIGHT:
                            print(f"Intersection Turn: {intersection_turns}")
                            speed_separate = [-0.5, 0.5]
                        elif intersection_turns[intersection_turns_index] == LEFT:
                            print(f"Intersection Turn: {intersection_turns}")
                            speed_separate = [0.5, -0.5]
                    else:
                        if intersection_turns[intersection_turns_index] == LEFT:
                            print(f"Intersection Turn: {intersection_turns}")
                            speed_separate = [-0.5, 0.5]
                        elif intersection_turns[intersection_turns_index] == RIGHT:
                            print(f"Intersection Turn: {intersection_turns}")
                            speed_separate = [0.5, -0.5]
                    time.sleep(0.95)
                    speed_separate = []
                    targetSpeed = 0

                    intersection_turns_index += 1
                    if intersection_turns_index > len(intersection_turns) - 1:
                        intersection_turns_index = len(intersection_turns) - 1

                    stream.seek(0)
                    stream.truncate()

                    continue

                height, width = grayscale_image.shape

                line_found = False
                for current_y in range(height, 0, -20):
                    cropped_image = grayscale_image[current_y: current_y + 20, 0: -1]
                    if np.sum(cropped_image) > 20*255 and current_y + 20 < height:
                        line_found = True
                        center_of_mass_y, center_of_mass_x = \
                            scipy.ndimage.center_of_mass(cropped_image)
                        break

                if not line_found or (np.sum(grayscale_image) < 50 * 255):  # Criteria for line lost
                    print("Line Lost")
                    targetSpeed = 0
                    # Moving backwards until line found again
                    speed_separate = [-1, -1]
                    time.sleep(0.2)
                    speed_separate = []

                    stream.seek(0)
                    stream.truncate()
                    continue

                targetSpeed_tmp = rev_per_second.update(width/2, center_of_mass_x)
                targetSpeed = targetSpeed_tmp if abs(targetSpeed_tmp) <= 1.4 \
                    else math.copysign(1.4, targetSpeed_tmp)
                # if abs(targetSpeed_tmp) > 1.4:
                #     targetSpeed = math.copysign(1.4, targetSpeed_tmp)
                # else:
                #     targetSpeed = targetSpeed_tmp
                # if targetSpeed_tmp > 0:
                #     targetSpeed = targetSpeed_tmp if targetSpeed_tmp < 1.5 else 1.5
                # elif targetSpeed_tmp < 0:
                #     targetSpeed = targetSpeed_tmp if targetSpeed_tmp > -1.5 else -1.5
                # else:
                #     targetSpeed = 0

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
                # end_time = timeit.default_timer()
                # print(f"Frame Time: {1/(end_time-start_time)}")
            except KeyboardInterrupt:
                end_program()

if not finish:
    end_program()
