#!/usr/bin/env python3

import cv2
import zmq
import pickle

camera = cv2.VideoCapture(0)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

while True:
    success, frame = camera.read()
    if success:
        socket.send(pickle.dumps(frame))

camera.release()
