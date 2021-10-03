#!/usr/bin/env python3

import json
import sys

import cv2
import scipy.ndimage
import numpy as np
import picamera
import picamera.array

debug = True
with open("robot_config.json") as robot_config_file:
    grayscale_threshold = json.load(robot_config_file)["GRAYSCALE_THRESHOLD"]


def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)


def custom_round(number):
    return int(round(number))


if sys.argv[1:]:
    grayscale_threshold = int(sys.argv[1])


image = None


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        try:
            while True:
                camera.capture(stream, "bgr", use_video_port=True)
                image = stream.array

                grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, black_and_white_image = cv2.threshold(
                    grayscale_image, grayscale_threshold, 255, cv2.THRESH_BINARY_INV
                )

                height, width = black_and_white_image.shape

                cv2.line(
                    image,
                    (int(image.shape[1] / 2), 0),
                    (int(image.shape[1] / 2), image.shape[0]),
                    (255, 0, 0),
                    3,
                )

                # if np.sum(black_and_white_image) < 50 * 255:
                #     print("Line Lost")
                #     sys.exit()

                if np.sum(black_and_white_image) < 50 * 255:
                    center_of_mass_y = 10
                    center_of_mass_x = 120

                for current_y in range(height, 0, -20):
                    cropped_image = black_and_white_image[
                        current_y : current_y + 20, 0:-1
                    ]
                    if np.sum(cropped_image) > 20 * 255 and current_y + 20 < height:
                        (
                            center_of_mass_y,
                            center_of_mass_x,
                        ) = scipy.ndimage.center_of_mass(cropped_image)
                        break

                # if cropped_image is None:
                #     print("Line Lost")
                #     sys.exit()

                if cropped_image is None:
                    center_of_mass_y = 10
                    center_of_mass_x = 120

                debugging = cv2.circle(
                    image,
                    (
                        custom_round(center_of_mass_x),
                        current_y + custom_round(center_of_mass_y),
                    ),
                    10,
                    (0, 0, 255),
                    10,
                )
                imshow_debug("Grayscale Image", grayscale_image)
                imshow_debug("Black and White Image", black_and_white_image)
                imshow_debug("Color Image", debugging)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                stream.seek(0)
                stream.truncate()
        except KeyboardInterrupt:
            pass


cv2.destroyAllWindows()
