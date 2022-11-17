#!/usr/bin/env python3

import os, sys, time, random
import zmq
import pickle
from dotenv import load_dotenv

load_dotenv()

USE_DISCORD_WEBHOOK = os.getenv("USE_DISCORD_WEBHOOK")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if USE_DISCORD_WEBHOOK.lower() == "true":
    USE_DISCORD_WEBHOOK = True
    import requests
elif USE_DISCORD_WEBHOOK.lower() == "false":
    USE_DISCORD_WEBHOOK = False
else:
    sys.exit("Invalid boolean for 'USE_DISCORD_WEBHOOK'")


USE_IMAGE = os.getenv("USE_IMAGE")

if USE_IMAGE.lower() == "true":
    USE_IMAGE = True
    import cv2

    prediction_address = os.getenv("PREDICTION_AND_IMAGE_ADDRESS")
    prediction_port = os.getenv("PREDICTION_AND_IMAGE_PORT")

elif USE_IMAGE.lower() == "false":
    USE_IMAGE = False

    prediction_address = os.getenv("PREDICTION_ADDRESS")
    prediction_port = os.getenv("PREDICTION_PORT")

else:
    sys.exit("Invalid boolean for 'USE_IMAGE'")

context = zmq.Context()
prediction_socket = context.socket(zmq.SUB)
# prediction socket can be either PREDICTION or PREDICTION_AND_IMAGE depending
# on the value of USE_IMAGE
prediction_socket.connect(f"tcp://{prediction_address}:{prediction_port}")
prediction_socket.setsockopt(zmq.SUBSCRIBE, b"")

def send_discord(message, timestamp = None, frame = None, color = "blue"):
    colors = {"red": 16711680, "green": 65280, "blue": 255}
    iso8601_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z", timestamp)
    payload = {
            #"content": message,
            "embeds": [
                {
                    "title": message,
                    #"description": "this is a description",
                    "timestamp": iso8601_timestamp,
                    "color": colors[color],
                },
            ],
        }
    requests.post(url = DISCORD_WEBHOOK_URL, json = payload)

    if frame is not None:
        ret, image = cv2.imencode('.png', frame)
        file = {f"{iso8601_timestamp}.png": image.tobytes()}
        requests.post(url = DISCORD_WEBHOOK_URL, files=file)


if USE_DISCORD_WEBHOOK:
    send_discord("Alert system started.", time.localtime())

## +===============+====================================+============+=========+
## | current state |               input                | next state | output  |
## +===============+====================================+============+=========+
## | armed         | >=75% land rover for 20 frames     | unarmed    | 4 beeps |
## +---------------+------------------------------------+------------+---------+
## | armed         | <75% land rover                    | armed      | none    |
## +---------------+------------------------------------+------------+---------+
## | unarmed       | >=85% not land rover for 80 frames | armed      | 1 beep  |
## +---------------+------------------------------------+------------+---------+
## | unarmed       | <85% not land rover                | unarmed    | none    |
## +---------------+------------------------------------+------------+---------+

while True:
    # unarmed
    count = 0
    while True:
        if USE_IMAGE:
            pred, timestamp, frame = pickle.loads(prediction_socket.recv())
        else:
            pred, timestamp = pickle.loads(prediction_socket.recv())
        print(pred)

        if pred[1] > 0.85:
            count += 1
            if count >= 1:
                break
        elif count > 0:
            count = 0

    # 1 beep
    print("1 beep")
    if USE_DISCORD_WEBHOOK:
        if USE_IMAGE:
            send_discord("land rover left", timestamp, frame, "green")
            cv2.imwrite(time.strftime("%Y-%m-%dT%H:%M:%S%z", timestamp) +
                        '_(' + str(random.randrange(1,100,1)) + ').png',
                        frame)
        else:
            send_discord("land rover left", timestamp, color = "green")

    # armed
    count = 0
    while True:
        if USE_IMAGE:
            pred, timestamp, frame = pickle.loads(prediction_socket.recv())
        else:
            pred, timestamp = pickle.loads(prediction_socket.recv())
        print(pred)

        if pred[0] > 0.75:
            count += 1
            if count >= 1:
                break
        elif count > 0:
            count = 0

    # 4 beeps
    print("4 beeps")
    if USE_DISCORD_WEBHOOK:
        if USE_IMAGE:
            send_discord("land rover detected", timestamp, frame, "red")
            cv2.imwrite(time.strftime("%Y-%m-%dT%H:%M:%S%z", timestamp) +
                        '_(' + str(random.randrange(1,100,1)) + ').png',
                        frame)
        else:
            send_discord("land rover detected", timestamp, color = "red")
