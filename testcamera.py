#!/usr/bin/env python3

import cv2
import zmq

camera = cv2.VideoCapture(0)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:5556")

while True:
    success, frame = camera.read()
    if success:
        retval, buffer = cv2.imencode(".jpg", frame)
        socket.send(buffer.tobytes())

camera.release()
