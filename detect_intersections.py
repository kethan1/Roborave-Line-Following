#!/usr/bin/env python3

import os

import cv2
import numpy as np
import picamera
import picamera.array

# The below data will be used by hardcoding which way the robot should turn
# when it detects an intersection.

images_correct = {
    "1.png": False,
    "2.png": False,
    "3.png": False,
    "4.png": False,
    "5.png": False,
    "6.png": False,
    "7.png": False,
    "8.png": True,
    "9.png": True,
    "10.png": True,
    "11.png": True,
    "12.jpg": False,
    "13.png": True,
    "14.png": False,
    "15.png": False,
    "16.png": False,
    "17.png": False,
    "18.png": False,
    "19.png": True,
    "20.png": True,
    "21.png": True,
    "22.png": True,
    "23.png": True,
    "24.png": True,
    "25.png": True,
}

for image_path in os.listdir("images/intersection_images"):
    image1 = cv2.imread(
        f"images/intersection_images/{image_path}", cv2.IMREAD_GRAYSCALE
    )

    image1 = cv2.resize(
        image1,
        dsize=(int(image1.shape[0] * 0.2), int(image1.shape[1] * 0.2)),
        interpolation=cv2.INTER_CUBIC,
    )

    image_summed = np.sum(image1, 1)
    max_pixels = np.max(image_summed) / 255
    img_width = image1.shape[1]
    # 7 and 15 are falsely detected, but they have the same (or very close)
    # pixel values to real intersections. The intersection detection isn't
    # really detecting intersections, it's for detecting turns that are too
    # sharp for the line following. 7 and 15 are too sharp for the line
    # following, so this is fine.
    if (img_width * 1 / 3) <= max_pixels:
        print(f"Intersection spotted {image_path}")
        print(max_pixels)
        if image_path in images_correct:
            if not images_correct[image_path]:
                print("Bad")


# Live Video Testing

file_number = max(
    map(int, [file.split(".")[0] for file in os.listdir("images/intersection_images")])
)

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    with picamera.array.PiRGBArray(camera) as stream:
        for _ in range(5):
            camera.capture(stream, "bgr", use_video_port=True)
            stream.seek(0)
            stream.truncate()

        while True:
            try:
                # start_time = timeit.default_timer()
                camera.capture(stream, "bgr", use_video_port=True)
                image = stream.array

                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    70,
                    255,
                    cv2.THRESH_BINARY_INV,
                )

                grayscale_image_resized = cv2.resize(
                    grayscale_image,
                    dsize=(int(image.shape[1] * 0.2), int(image.shape[0] * 0.2)),
                    interpolation=cv2.INTER_CUBIC,
                )

                image_summed = np.sum(grayscale_image_resized, 1)
                max_pixels = np.max(image_summed) / 255
                if (grayscale_image_resized.shape[1] * 0.4) <= max_pixels:
                    print("Intersection spotted")
                    print(f"{max_pixels/grayscale_image_resized.shape[1]}")

                cv2.imshow("Video Stream", grayscale_image)

                keypressed = cv2.waitKey(1)

                if keypressed & 0xFF == ord("q"):
                    break
                elif keypressed & 0xFF == ord("s"):
                    cv2.imwrite(
                        f"images/intersection_images/{file_number}.jpg", grayscale_image
                    )
                    file_number += 1

                stream.seek(0)
                stream.truncate()

            except KeyboardInterrupt:
                cv2.destroyAllWindows()
