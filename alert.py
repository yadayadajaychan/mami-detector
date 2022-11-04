#!/usr/bin/env python3

import zmq
from dotenv import load_dotenv

load_dotenv()
context = zmq.Context()
prediction_socket = context.socket(zmq.SUB)
prediction_socket.connect(f"tcp://{PREDICTION_ADDRESS}:{PREDICTION_PORT}")

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
        pred = prediction_socket.recv()
        if pred[0] > 0.75:
            count += 1
            if count >= 5:
                break
        elif count > 0:
            count = 0

    # 4 beeps
    print("4 beeps")

    # unarmed
    count = 0
    while True:
        pred = prediction_socket.recv()
        if pred[1] > 0.85:
            count += 1
            if count >= 30:
                break
        elif count > 0:
            count = 0

    # 1 beep
    print("1 beep")
