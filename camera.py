#!/usr/bin/env python3

import os
import cv2
import zmq
import pickle
from dotenv import load_dotenv

load_dotenv()
CAMERA_PORT = os.getenv("CAMERA_PORT")

camera = cv2.VideoCapture(0)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://*:{CAMERA_PORT}")

# assuming image is wider than height
def crop_square(img):
    height = img.shape[0]
    mid_width = img.shape[1] // 2

    start_width = mid_width - (height // 2)
    end_width = mid_width + (height // 2)

    return img[:, start_width:end_width]


while True:
    success, frame = camera.read()
    if success:
        #crop image into square
        frame = crop_square(frame)
        # Resize the raw image into (224-height,224-width) pixels.
        frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)

        pickled_frame = pickle.dumps(frame)

        # wait for request from client
        message = socket.recv()
        socket.send(pickled_frame)

camera.release()
