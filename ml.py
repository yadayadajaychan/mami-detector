#!/usr/bin/env python3

import os
import cv2
import numpy as np
import zmq
import pickle
from keras.models import load_model
from dotenv import load_dotenv

load_dotenv() # load env variables from .env file
CAMERA_ADDRESS = os.getenv("CAMERA_ADDRESS")
CAMERA_PORT = os.getenv("CAMERA_PORT")
PREDICTION_PORT = os.getenv("PREDICTION_PORT")
PREDICTION_AND_IMAGE_PORT = os.getenv("PREDICTION_AND_IMAGE_PORT")

# create zmq context
context = zmq.Context()
# socket for receiving frames
frame_socket = context.socket(zmq.REQ)
frame_socket.connect(f"tcp://{CAMERA_ADDRESS}:{CAMERA_PORT}")
# socket for publishing predictions
prediction_socket = context.socket(zmq.PUB)
prediction_socket.bind(f"tcp://*:{PREDICTION_PORT}")
# socket for publishing predictions + img
prediction_and_image_socket = context.socket(zmq.PUB)
prediction_and_image_socket.bind(f"tcp://*:{PREDICTION_AND_IMAGE_PORT}")

# Load the model
model = load_model('keras_model.h5')

# Grab the labels from the labels.txt file. This will be used later.
labels = open('labels.txt', 'r').readlines()

while True:
    # grab numpy array from socket
    frame_socket.send(b"GET")
    frame = pickle.loads(frame_socket.recv())
    # Make the image a numpy array and reshape it to the models input shape.
    image = np.asarray(frame, dtype=np.float32).reshape(1, 224, 224, 3)
    # Normalize the image array
    image = (image / 127.5) - 1
    # Have the model predict what the current image is. Model.predict
    # returns an array of percentages. Example:[0.2,0.8] meaning its 20% sure
    # it is the first label and 80% sure its the second label.
    probabilities = model.predict(image)
    readable_probabilities = "land rover    : %6.2f%%\nnot land rover: %6.2f%%"\
                % ((probabilities[0][0] * 100), (probabilities[0][1] * 100))
    print(readable_probabilities)
    pred_and_img = (readable_probabilities, frame)
    prediction_and_image_socket.send(pickle.dumps(pred_and_img))
