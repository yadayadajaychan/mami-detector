#!/usr/bin/env python3

import cv2
import numpy as np
import zmq
import pickle
from keras.models import load_model

# create zmq context
context = zmq.Context()
# socket for receiving frames
frame_socket = context.socket(zmq.REQ)
frame_socket.connect("tcp://localhost:5556")
# socket for publishing predictions + img
prediction_socket = context.socket(zmq.PUB)
prediction_socket.bind("tcp://*:5557")

# Load the model
model = load_model('keras_model.h5')

# Grab the labels from the labels.txt file. This will be used later.
labels = open('labels.txt', 'r').readlines()

# assuming image is wider than height
def crop_square(img):
    height = img.shape[0]
    mid_width = img.shape[1] // 2

    start_width = mid_width - (height // 2)
    end_width = mid_width + (height // 2)

    return img[:, start_width:end_width]

while True:
    # grab numpy array from socket
    frame_socket.send(b"GET")
    frame = pickle.loads(frame_socket.recv())
    # crop image into square
    frame = crop_square(frame)
    # Resize the raw image into (224-height,224-width) pixels.
    frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
    # Show the image in a window
    cv2.imshow('Webcam Image', frame)
    # Make the image a numpy array and reshape it to the models input shape.
    image = np.asarray(frame, dtype=np.float32).reshape(1, 224, 224, 3)
    # Normalize the image array
    image = (image / 127.5) - 1
    # Have the model predict what the current image is. Model.predict
    # returns an array of percentages. Example:[0.2,0.8] meaning its 20% sure
    # it is the first label and 80% sure its the second label.
    probabilities = model.predict(image)
    # Print what the highest value probabilitie label
    #print(labels[np.argmax(probabilities)])
    print(probabilities)
    # Listen to the keyboard for presses.
    keyboard_input = cv2.waitKey(1)
    # 27 is the ASCII for the esc key on your keyboard.
    if keyboard_input == 27:
        break

cv2.destroyAllWindows()
