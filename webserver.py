#!/usr/bin/env python3

from flask import Flask, render_template, Response
import cv2
import time
import zmq
from concurrent.futures import ThreadPoolExecutor

app = Flask("__name__")

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:5556")
socket.setsockopt(zmq.SUBSCRIBE, b"\xFF\xD8\xFF")

def get_frame():
    while True:
        frame = socket.recv()

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video")
def video():
    return Response(get_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
