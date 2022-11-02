#!/usr/bin/env python3

from flask import Flask, render_template, Response
import cv2
import time
import zmq
import pickle
from concurrent.futures import ThreadPoolExecutor

app = Flask("__name__")

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:5557")
socket.setsockopt(zmq.SUBSCRIBE, b"")

def get_frame():
    while True:
        frame = pickle.loads(socket.recv())
        ret, image = cv2.imencode(".jpg", frame)

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + image.tobytes() + b'\r\n')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video")
def video():
    return Response(get_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
