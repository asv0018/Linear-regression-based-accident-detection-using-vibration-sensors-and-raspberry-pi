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

# Function to send messages to the contact numbers through GSM
def send_message(port, emergency_number, msg):
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

# Function to obtain GPS location through IP address
def get_geolocation():
    url = 'http://api.hostip.info/get_json.php'
    resp = requests.get(url)
    info = json.loads(resp.content.decode('utf-8'))
    ip = info['ip']
    latlong_response = requests.get("http://ipinfo.io/"+ip+"?token=8216e090b04b16")
    data = json.loads(latlong_response.content.decode("utf-8"))
    return data["loc"].split(",")[0], data["loc"].split(",")[1]

# Function to capture images and store them
def capture_pictures(camera):
    i = 1
    while i < 6:
        camera.capture("./images/accident-snapshot-"+str(i)+".jpg")
        i += 1

# Function to send messages via telegram
def send_messages_telegram(msg):
    resp = requests.get("https://api.telegram.org/bot1859820472:AAFxymdOoQrRcrLNKPR5lGYUBG8Qtz_EV5k/sendMessage?chat_id=584870711&text={0}".format(msg))
    print(resp.status_code)

# Function to send images via telegram
def send_images_in_telegram(msg):
    for i in range(1,6):
        img_name = './images/accident-snapshot-'+str(i)+'.jpg'
        files={"photo":open(img_name, "rb")}
        url = "https://api.telegram.org/bot1859820472:AAFxymdOoQrRcrLNKPR5lGYUBG8Qtz_EV5k/sendPhoto?chat_id=584870711&caption="+msg
        print(url)
        resp = requests.post(url, files=files)
        print(resp.status_code)
        print(resp.text)