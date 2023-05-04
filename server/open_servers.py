import re
import socket
import numpy as np
import cv2
from flask import Flask, Response, request
from flask_cors import CORS
import threading
from mss import mss
import asyncio
import websockets
import pyautogui


# Get the IP Address of the server
def is_ipv4_address(address):
    # Expressão regular para verificar se a string é um endereço IPv4 válido
    ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')

    # Verifica se a string corresponde ao padrão do endereço IPv4
    if ipv4_pattern.match(address):
        # Divide a string em partes separadas por ponto e verifica se cada parte está no intervalo correto
        parts = address.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return True
    return address == "localhost"


hostname = socket.gethostname()
address_info_list = socket.getaddrinfo(hostname, None)

ip_addresses = set()

for address_info in address_info_list:
    if is_ipv4_address(address_info[4][0]):
        ip_addresses.add(address_info[4][0])
ip_addresses = list(ip_addresses)
ip_position = 0

if len(ip_addresses) > 1:
    print("Looks like your computer had more than one IPV4, which one you want to use?")
    for i in range(len(ip_addresses)):
        print("(" + str(i) + ") " + ip_addresses[i])
    ip_position = int(input("Use the number before the IP to choose"))

while ip_position > (len(ip_addresses) - 1) or ip_position < 0:
    print("This isn`t a valid options. Try again.")
    for i in range(len(ip_addresses)):
        print("(" + str(i) + ") " + ip_addresses[i])
    ip_addresses = int(input("Use the number before the IP to choose"))

# Get Screen Resolution and Padding

screen_resolution = input("Insert the screen resolution using this mask 'X value * Y value'")
screen_res_parse = screen_resolution.split("*")
screen_res_parse = [int(x) for x in screen_res_parse]
print(screen_res_parse)
while len(screen_res_parse) != 2 or all(x < 0 for x in screen_res_parse):
    screen_resolution = input("This isn`t a valid resolution. Use this mask 'X value * Y value' and remember X and Y "
                              "need to be positive")
    screen_res_parse = screen_resolution.split("*")
    screen_res_parse = [int(x) for x in screen_res_parse]

get_padding = input("Do you want to pad the screen capture? (Y/N)")
while get_padding.upper() not in ("Y", "N", "YES", "NO"):
    get_padding = input("Do you want to pad the screen capture? (Y/N)")

padding = "0*0"
padding_parse = padding.split("*")
padding = [int(x) for x in padding_parse]
if get_padding.upper() in ("Y", "YES"):
    padding = input("Insert the screen padding using this mask 'X value * Y value'")
    padding_parse = padding.split("*")
    padding_parse = [int(x) for x in padding_parse]
    while len(padding_parse) != 2 or all(x > 0 for x in padding_parse):
        padding = input(
            "This isn`t a valid padding. Use this mask 'X value * Y value' and remember X and Y "
            "need to be positive")
        padding_parse = padding.split("*")
        padding_parse = [int(x) for x in padding_parse]

# Get key
key_connection = input(
    "Insert a connection key (If you dont want protection just leave empty)\nThe client will ask for but, "
    "remember the key.\nIf you leave empty just put anything in client key")


def frame_capture(sct, bound_box):
    sct_img = sct.grab(bound_box)
    return cv2.imencode('.jpg', (np.array(sct_img)))[1].tobytes()


app = Flask(__name__)
CORS(app)
screen = mss()
bounding_box = {'top': screen.monitors[2]['top'] + padding[1], 'left': screen.monitors[2]['left'] + padding[0],
                'width': screen_res_parse[0], 'height': screen_res_parse[1]}


def gen(sct, bound_box):
    while True:
        # get camera frame
        frame = frame_capture(sct, bound_box)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed', methods=['GET'])
def video_feed():
    key = request.args.get('key')
    if key == key_connection or key_connection == "":
        return Response(gen(screen, bounding_box),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "F"


res_correction = 0

sct = mss()


async def handler(websocket):
    global res_correction
    async for message in websocket:
        split_msg = message.split(";")
        if split_msg[0] not in ("OK", "Connected"):
            if key_connection == "" or key_connection == split_msg[0]:
                resp = float(split_msg[1])
                x = int(resp)
                y = (resp - x) * 1000
                x = x * res_correction[0]
                y = y * res_correction[1]
                pyautogui.moveTo(x - 1920, y)
                pyautogui.click()
        else:
            print("Connected")
            screen_res_client = split_msg[1].split("*")
            res_correction = [int(screen_res_parse[0]) / float(screen_res_client[0]),
                              int(screen_res_parse[1]) / float(screen_res_client[1])]


async def start_server():
    async with websockets.serve(handler, ip_addresses[ip_position], 433):
        await asyncio.Future()


threading.Thread(target=lambda: asyncio.run(start_server()), args=()).start()

app.run(host=ip_addresses[ip_position], port='5000', debug=False)
