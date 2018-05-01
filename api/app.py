import json
import cv2
from flask import Flask
from bot import Master
from time import sleep
# app = Flask(__name__)

currnet_index = 0
infos = [None, None]
bot_ids = [91, 125, 86, 121]
bot_ids = [i for i in range(70)]
bot_ids = [14, 32]
cap = None
try:
    cap = cv2.VideoCapture(1)

    master = Master(bot_ids, cap)
    master.start()
    # sleep(1)
    while True:
        bots = master.bots
        # print(bots)
        if not bots:
            continue
finally:
    if cap:
        cap.release()
