#!usr/bin/python3
print("Importing required packages")
from LinearRegressionModel import LinearRegressionModel
from GpioDeclarations import *
from AllConstants import *
import RPi.GPIO as GPIO
from Functions import *
from serial import *
from collections import Counter
from picamera import PiCamera
from time import time

print("Setting up the required configuration")
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(ALCOHOL_SENSOR, GPIO.IN)
GPIO.setup(VIBRATION_SENSOR, GPIO.IN)

camera = PiCamera()

port = Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)

model = LinearRegressionModel(path_of_dataset, tuning_value)

config_gsm_to_sms_mode(port)

print("The system begins now")
# Never ending loop starts here
while True:
    # Create a collection of vibration data for a second
    # Find out the frequency of HIGH pulses and convert to Khz
    count = 1
    vibration_data = []
    init_time = time()
    time_stamp = 0
    while (time() - init_time) <= 1:
        time_stamp = time() - init_time
        vibration_state = GPIO.input(VIBRATION_SENSOR)
        vibration_data.append(vibration_state)
        count+=1
    
    frequency = collections.Counter(vibration_data)
    length_of_dict = len(frequency)

    # Apply ML to the data only when there are HIGH pulses only
    if length_of_dict == 2:
        frequency = float(dict(frequency)[1])/1000
        print("Frequency of vibration ", frequency, " Khz")
        accident_flag = model.predict_accident(frequency)
        # Send out the messages if there is any sign of accident.
        if accident_flag:
            latitude, longitude = get_geolocation()
            location_link = "https://maps.google.com/?q="+latitude+" ,"+longitude
            msg = "There has been an accident suspected at the location with the coordinates "+latitude+","+longitude+".\r Try with the google maps link to locate the position. "+location_link
            capture_pictures(camera)
            send_message(port, emergency_number, msg)
            send_images_in_telegram(msg)
            print("Messages and the images are sent to the contact numbers and emergency departments.")
        else:
            print("There is no sign of accident")
        # Print a new line character, to give a line space
        print("\n")

    # Monitor if the driver is drunk
    alcohol_state = GPIO.input(ALCOHOL_SENSOR)
    # If he is drunk, then send message of his location via SMS.
    if alcohol_state:
        while alcohol_state:
            alcohol_state = GPIO.input(ALCOHOL_SENSOR)
        print("The person is drunk")
        latitude, longitude = get_geolocation()
        location_link = "https://maps.google.com/?q="+latitude+","+longitude
        msg = "The person is drunk. Please check his location with the Google Maps link : "+location_link
        send_message(port, emergency_number, msg)
        print("The messages are sent to the family persons")
        # Print a new line character, to give a line space
        print("\n")