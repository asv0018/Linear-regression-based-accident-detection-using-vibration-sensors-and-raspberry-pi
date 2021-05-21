#!usr/bin/python3
from LinearRegressionModel import LinearRegressionModel
from program_constants import *
from GpioDeclarations import *
import RPi.GPIO as GPIO
from Functions import *
from serial import *
import collections
import picamera
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(ALCOHOL_SENSOR, GPIO.IN)
GPIO.setup(VIBRATION_SENSOR, GPIO.IN)

camera = picamera.PiCamera()

port = Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)

model = LinearRegressionModel(path_of_dataset, tuning_value)

while True:
    # Create a collection of vibration data for a second
    # Find out the frequency of HIGH pulses and convert to Khz
    count = 1
    vibration_data = []
    init_time = time.time()
    time_stamp = 0
    while (time.time() - init_time) <= 1:
        time_stamp = time.time() - init_time
        vibration_state = GPIO.input(VIBRATION_SENSOR)
        vibration_data.append(vibration_state)
        count+=1
    
    frequency = collections.Counter(vibration_data)
    length_of_dict = len(frequency)

    # Apply ML to the data only when there are HIGH pulses only
    if length_of_dict == 2:
        frequency = float(dict(frequency)[1])/1000
        print(frequency)
        accident_flag = model.predict_accident(frequency)
        if accident_flag:
            print("SHOULD SEND MESSAGES AND ALERTS")
        else:
            print("THERE IS NOTHING TO BE DONE SO CHILL")