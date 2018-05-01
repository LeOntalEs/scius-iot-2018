import json
from time import sleep
from threading import Thread

import cv2
from flask import Flask, render_template, request, abort

app = Flask(__name__)

BOT_IDS = [0, 1,2,3,4]
BOT_IDS = [str(x) for x in BOT_IDS]
BOT_SECRET = { str(k): str(k)*4 for k in BOT_IDS}

STOP_IDX = 0
TURN_TIME = 1
INSTRUCTION_IDX = 1
current_idx = 0
buffer = [{str(k): '0'*26 for k in BOT_IDS}, {str(k): '0'*26 for k in BOT_IDS}]

def get_init_status(idx):
    return {
                'id': idx,
                'x': -1,
                'y': -1,
                'theta': -1,
                'temp': 0,
                'humi': 0,
            }
status = {k:get_init_status(k) for k in BOT_IDS}

class Synchronizer(Thread):
    def __init__(self, *args, **kwargs):
        super(Synchronizer, self).__init__(*args, **kwargs)
        self.current_idx = 0

    def run(self):
        while True:
            self.current_idx = (self.current_idx + 1) % 2
            sleep(TURN_TIME)

sync = Synchronizer()
sync.start()

def bad_authen(idx, secret):
    if idx in BOT_SECRET and BOT_SECRET[idx] == secret:
        return True
    return False

@app.route("/setcmd/<idx>/<secret>/<cmd>/")
def setcmd(idx=None, secret=None, cmd=None):
    if bad_authen(idx, secret):
        buffer[INSTRUCTION_IDX][idx] = cmd
        return buffer[INSTRUCTION_IDX][idx], 200
    else:
        abort(403)


@app.route("/getcmd/<idx>/<temp>/<humi>/")
def getcmd(idx=None, temp=None, humi=None):
    if idx and idx in BOT_IDS:
        if temp:
            status[idx]['temp'] = temp
        if humi:
            status[idx]['humi'] = humi
        return buffer[sync.current_idx][idx]
    else:
        abort(404)


@app.route("/getstatus/")
def getstatus():
    return json.dumps(status)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
