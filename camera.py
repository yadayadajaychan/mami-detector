#!/usr/bin/env python3

import cv2
import zmq
import pickle

camera = cv2.VideoCapture(0)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

while True:
    success, frame = camera.read()
    if success:
        pickled_frame = pickle.dumps(frame)

        # wait for request from client
        message = socket.recv()
        socket.send(pickled_frame)

camera.release()
