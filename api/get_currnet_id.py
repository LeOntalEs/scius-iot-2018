import json
from time import sleep, time

import cv2
from flask import Flask
from bot import Master
# app = Flask(__name__)
cap = None
try:
    cap = cv2.VideoCapture(0)
    currnet_index = 0
    bot_ids = [14, 32]
    master = Master(bot_ids, cap)
    master.start()
    while True:
        bots = master.bots
        # print(bots)
        start = time()
        infos = master.get_info()
        if infos:
            for info in infos:
                val = infos[info]
                if val['theta'] != -1:
                    # print(val)
                    pass
finally:
    cv2.destroyAllWindows()
    if cap:
        cap.release()
