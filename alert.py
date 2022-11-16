#!/usr/bin/env python3

import os, sys, time
import zmq
import pickle
from dotenv import load_dotenv

load_dotenv()
PREDICTION_ADDRESS = os.getenv("PREDICTION_ADDRESS")
PREDICTION_PORT = os.getenv("PREDICTION_PORT")

context = zmq.Context()
prediction_socket = context.socket(zmq.SUB)
prediction_socket.connect(f"tcp://{PREDICTION_ADDRESS}:{PREDICTION_PORT}")
prediction_socket.setsockopt(zmq.SUBSCRIBE, b"")

USE_DISCORD_WEBHOOK = os.getenv("USE_DISCORD_WEBHOOK")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if USE_DISCORD_WEBHOOK == "True":
    USE_DISCORD_WEBHOOK = True
    import requests
elif USE_DISCORD_WEBHOOK == "False":
    USE_DISCORD_WEBHOOK = False
else:
    sys.exit("Invalid boolean for 'USE_DISCORD_WEBHOOK'")

def send_discord(message, timestamp = None, frame = None, color = "blue"):
    colors = {"red": 16711680, "green": 65280, "blue": 255}
    payload = {
            #"content": message,
            "embeds": [
                {
                    "title": message,
                    #"description": "this is a description",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z", timestamp),
                    "color": colors[color],
                },
            ],
        }
    requests.post(url = DISCORD_WEBHOOK_URL, json = payload)



if USE_DISCORD_WEBHOOK:
    send_discord("Alert system started.", time.localtime())

## +===============+====================================+============+=========+
## | current state |               input                | next state | output  |
## +===============+====================================+============+=========+
## | armed         | >=75% land rover for 5 frames      | unarmed    | 4 beeps |
## +---------------+------------------------------------+------------+---------+
## | armed         | <75% land rover                    | armed      | none    |
## +---------------+------------------------------------+------------+---------+
## | unarmed       | >=85% not land rover for 30 frames | armed      | 1 beep  |
## +---------------+------------------------------------+------------+---------+
## | unarmed       | <85% not land rover                | unarmed    | none    |
## +---------------+------------------------------------+------------+---------+

while True:
    # armed
    count = 0
    while True:
        pred, timestamp = pickle.loads(prediction_socket.recv())
        print(pred)
        if pred[0] > 0.75:
            count += 1
            if count >= 5:
                break
        elif count > 0:
            count = 0

    # 4 beeps
    print("4 beeps")
    if USE_DISCORD_WEBHOOK:
        send_discord("land rover detected", timestamp, color = "red")

    # unarmed
    count = 0
    while True:
        pred, timestamp = pickle.loads(prediction_socket.recv())
        print(pred)
        if pred[1] > 0.85:
            count += 1
            if count >= 30:
                break
        elif count > 0:
            count = 0

    # 1 beep
    print("1 beep")
    if USE_DISCORD_WEBHOOK:
        send_discord("land rover left", timestamp, color = "green")
