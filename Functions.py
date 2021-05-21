#!usr/bin/python3
import picamera
import RPi.GPIO as GPIO
import urllib.request
import collections
import requests
import json
from serial import *
import os
from GpioDeclarations import *
import time
from AllConstants import *

# Function to send messages to the contact numbers through GSM

def config_gsm_to_sms_mode(port):
    num = port.write(b'AT\r')
    rcv = port.read(num)
    print(rcv)
    port.write(b"AT+CMGF=1\r")
    print("Text Mode Enabled…")

def send_message(port, emergency_number, msg):
    port.write(b'AT+CMGS="'+str.encode(emergency_number)+b'"\r')
    print("sending message….")
    time.sleep(1)
    port.reset_output_buffer()
    time.sleep(1)
    port.write(str.encode(msg+chr(26)))
    print("message sent…")

# Function to obtain GPS location through IP address
def get_geolocation():
    url = 'http://api.hostip.info/get_json.php'
    resp = requests.get(url)
    global ip
    try:
        info = json.loads(resp.content.decode('utf-8'))
        ip = info['ip']
    except ValueError as e:
        print("data is missed, fetching location from cached ip address.")
    print("The ip of the system is : ",ip)
    latlong_response = requests.get("http://ipinfo.io/"+ip+"?token=8216e090b04b16")
    if latlong_response.status_code==200:
        data = json.loads(latlong_response.content.decode("utf-8"))
        global lat, lon
        lat, lon =  data["loc"].split(",")[0], data["loc"].split(",")[1]
    
    return lat, lon

# Function to capture images and store them
def capture_pictures(camera):
    path = os.path.dirname(__file__)
    i = 1
    while i < 6:
        camera.capture(path+"/images/accident-snapshot-"+str(i)+".jpg")
        i += 1

# Function to send messages via telegram
def send_messages_telegram(msg):
    resp = requests.get("https://api.telegram.org/bot1859820472:AAFxymdOoQrRcrLNKPR5lGYUBG8Qtz_EV5k/sendMessage?chat_id=584870711&text={0}".format(msg))
    print(resp.status_code)
    print("Message is sent if the code is 200. The code is :- ",resp.status_code)

# Function to send images via telegram
def send_images_in_telegram(msg):
    path = os.path.dirname(__file__)
    for i in range(1,6):
        img_name = path+'/images/accident-snapshot-'+str(i)+'.jpg'
        files={"photo":open(img_name, "rb")}
        url = "https://api.telegram.org/bot1859820472:AAFxymdOoQrRcrLNKPR5lGYUBG8Qtz_EV5k/sendPhoto?chat_id=584870711&caption="+msg
        resp = requests.post(url, files=files)
        print("Message is sent if the code is 200. The code is :- ",resp.status_code)
        # print(resp.text)