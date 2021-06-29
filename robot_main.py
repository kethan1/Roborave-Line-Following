#!/usr/bin/env python3

import sys
import time
import json
import timeit
import threading

import cv2
import numpy as np
import picamera
import picamera.array
import RPi.GPIO as GPIO
import scipy.ndimage

import Libraries.ThunderBorg3 as ThunderBorg
from PID import PID
from CPP_Libraries.Encoder_CPP.encoder import Encoder, init as initialize


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

if not debug and "--print-prod" not in sys.argv[1:]:
    sys.stdout = None


initialize()
encoder_left = Encoder(*robot_config["Encoder_Left"])
encoder_right = Encoder(*robot_config["Encoder_Right"])


GPIO.setmode(GPIO.BCM)
pinlistOut = []
pinlistIn = [25, 22, 24, 23]
# Motor1 - Right
# Motor2 - Left
GPIO.setup(pinlistOut, GPIO.OUT)
GPIO.setup(pinlistIn, GPIO.IN)
GPIO.output(pinlistOut, 0)


image, finish, targetSpeed = None, False, 0
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

        speed_left = maintain_speed_PID_left.update(BASE_SPEED - targetSpeed, current_speed_left)
        speed_right = maintain_speed_PID_right.update(BASE_SPEED + targetSpeed, current_speed_right)

        print(f"Speed Left: {speed_left}, Speed Right: {speed_right}, targetSpeed: {targetSpeed}, current_speed_left: {current_speed_left}, current_speed_right: {current_speed_right}")

        # If the motors drop too low, they won't move. This brings up the
        # power level to 0.15 if it is lower than that.
        # speed_left = speed_left if speed_left > 0.15 else 0.15
        # speed_right = speed_right if speed_right > 0.15 else 0.15
        if speed_left > 0:
            speed_left = speed_left if speed_left > 0.15 else 0.15
        else:
            speed_left = speed_left if speed_left < -0.15 else -0.15
        if speed_right > 0:
            speed_right = speed_right if speed_right > 0.15 else 0.15
        else:
            speed_right = speed_right if speed_right < -0.15 else -0.15

        TB.SetMotor1(speed_left)
        TB.SetMotor2(speed_right)
        time.sleep(0.005)

    maintain_speed_PID_left.close()
    maintain_speed_PID_right.close()


set_speed_thread = threading.Thread(target=set_speed)


def end_program():
    global finish
    finish = True
    cv2.destroyAllWindows()
    TB.MotorsOff()
    GPIO.cleanup()
    rev_per_second.close()
    set_speed_thread.join()


set_speed_thread.start()

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        while True:
            try:
                # start_time = timeit.default_timer()
                image, cropped_image = None, None
                while image is None:
                    camera.capture(stream, "bgr", use_video_port=True)
                    image = stream.array

                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY_INV
                )

                height, width = grayscale_image.shape

                if np.sum(grayscale_image) < 50 * 255:
                    print("Line Lost")
                    end_program()
                    sys.exit()

                for current_y in range(height, 0, -20):
                    cropped_image = grayscale_image[current_y: current_y + 20, 0: -1]
                    if np.sum(cropped_image) > 20*255 and current_y+20 < height:
                        center_of_mass_y, center_of_mass_x = \
                            scipy.ndimage.center_of_mass(cropped_image)
                        break

                if cropped_image is None:
                    print("Line Lost")
                    end_program()
                    sys.exit()

                targetSpeed_tmp = rev_per_second.update(width/2, center_of_mass_x)
                if targetSpeed_tmp > 0:
                    targetSpeed = targetSpeed_tmp if targetSpeed_tmp < 1.5 else 1.5
                elif targetSpeed_tmp < 0:
                    targetSpeed = targetSpeed_tmp if targetSpeed_tmp > -1.5 else -1.5

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
                            cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR), (
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
                break

end_program()
