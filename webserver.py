#!/usr/bin/env python3

from flask import Flask, render_template, Response
import os
from time import strftime
import cv2
import time
import zmq
import pickle
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()
PREDICTION_AND_IMAGE_ADDRESS = os.getenv("PREDICTION_AND_IMAGE_ADDRESS")
PREDICTION_AND_IMAGE_PORT = os.getenv("PREDICTION_AND_IMAGE_PORT")

app = Flask("__name__")

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect(f"tcp://{PREDICTION_AND_IMAGE_ADDRESS}:{PREDICTION_AND_IMAGE_PORT}")
socket.setsockopt(zmq.SUBSCRIBE, b"")

def get_frame():
    while True:
        pred, timestamp, frame = pickle.loads(socket.recv())
        readable_pred = ("land rover    : %6.2f%%" % (pred[0] * 100),
                         "not land rover: %6.2f%%" % (pred[1] * 100))
        timestamp = strftime("%Y-%m-%dT%H:%M:%S%z", timestamp)

        img = cv2.putText(frame, readable_pred[0], (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv2.LINE_AA)
        img = cv2.putText(img, readable_pred[1], (10,40), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv2.LINE_AA)
        img = cv2.putText(img, timestamp, (8,220), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv2.LINE_AA)
        ret, image = cv2.imencode(".jpg", img)

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + image.tobytes() + b'\r\n')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video")
def video():
    return Response(get_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
