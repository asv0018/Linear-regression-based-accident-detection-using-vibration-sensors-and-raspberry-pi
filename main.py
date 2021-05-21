import RPi.GPIO as GPIO
import urllib.request
import collections
import requests
import json
import serial
import os
from GpioDeclarations import *
import cv2
import time

# Provide the emergency number & message
emergency_number = "7795330913"
msg = "There has an accident taken place at so and so location. come fast and save them."

# Disable the warnings and set the board to BCM mode
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Declare the pins as Input
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)
GPIO.setup(ALCOHOL_SENSOR, GPIO.IN)
GPIO.setup(VIBRATION_SENSOR, GPIO.IN)

# Few important functions
def send_message(emergency_number, msg):
    port.write(b'AT\r')
    rcv = port.read(30)
    print(rcv)
    port.write(b"AT+CMGF=1\r")
    print("Text Mode Enabled…")
    time.sleep(3)
    port.write(b'AT+CMGS="'+str.encode(emergency_number)+b'"\r')
    #msg = "test message from SIM900A…"
    print("sending message….")
    time.sleep(3)
    port.reset_output_buffer()
    time.sleep(1)
    port.write(str.encode(msg+chr(26)))
    time.sleep(3)
    print("message sent…")

def get_geolocation():
    url = 'http://api.hostip.info/get_json.php'
    resp = requests.get(url)
    info = json.loads(resp.content.decode('utf-8'))
    ip = info['ip']
    latlong_response = requests.get("http://ipinfo.io/"+ip+"?token=8216e090b04b16")
    data = json.loads(latlong_response.content.decode("utf-8"))
    return data["loc"].split(",")[0], data["loc"].split(",")[1]

def capture_pictures():
    camera = cv2.VideoCapture(0)
    i = 0
    while i < 10:
        return_value, image = camera.read()
        cv2.imwrite('./images/accident-image'+str(i)+'.png', image)
        i += 1
    del(camera)

def send_messages_telegram(msg):
    resp = requests.get("https://api.telegram.org/bot1859820472:AAFxymdOoQrRcrLNKPR5lGYUBG8Qtz_EV5k/sendMessage?chat_id=584870711&text={0}".format(msg))
    print(resp.status_code)

def send_images_in_telegram(msg):
    for i in range(0,10):
        img_name = './images/accident-image'+str(i)+'.png'
        files={"photo":open(img_name, "rb")}
        url = "https://api.telegram.org/bot1859820472:AAFxymdOoQrRcrLNKPR5lGYUBG8Qtz_EV5k/sendPhoto?chat_id=584870711&caption="+msg
        print(url)
        resp = requests.post(url, files=files)
        print(resp.status_code)
        print(resp.text)
        
        
# Never ending loop
#latitude, longitude = get_geolocation()
#location_link = "https://maps.google.com/?q="+latitude+" ,"+longitude
#msg = "There has been an accident suspected at the location with the coordinates "+latitude+","+longitude+".\r Try with the google maps link to locate the position. "+location_link
#capture_pictures()
#send_message(emergency_number, msg)
print("STARTING NOW")
while True:
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
    if length_of_dict == 2:
        frequency = float(dict(frequency)[1])/1000
        print(frequency)

    
