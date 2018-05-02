import json
import http.client
from time import sleep
from threading import Thread

from flask import Flask, render_template, request, abort

BOT_IDX = 0
IS_SLEEP = False
NEED_OTHER_STATUS = False

GATEWAY_ADDR = '192.168.1.99:8000'
STOP_IDX = 0
STOP_TIME = 1
TURN_TIME = 0.5

app = Flask(__name__)
own_status = {
    'id': BOT_IDX,
    'x': -1,
    'y': -1,
    'theta': -1,
    'temp': 0,
    'humi': 0,
}

INSTRUCTION_IDX = 1
buffer = ['0'*27, '0'*27]

class Synchronizer(Thread):
    def __init__(self, is_sleep, *args, **kwargs):
        super(Synchronizer, self).__init__(*args, **kwargs)
        self.current_idx = 0
        self.is_sleep = is_sleep

    def run(self):
        while True:
            self.current_idx = INSTRUCTION_IDX
            if self.is_sleep:
                if self.current_idx == INSTRUCTION_IDX:
                    sleep(TURN_TIME)
                else:
                    sleep(STOP_TIME)
                self.current_idx = (self.current_idx + 1) % 2
            else:
                pass


sync = Synchronizer(is_sleep=IS_SLEEP)
sync.start()


def request_gateway_status():
    connection = False
    try:
        connection = http.client.HTTPConnection(GATEWAY_ADDR)
        connection.request("GET", '/getstatus/')
        response = connection.getresponse()
        data = response.read().decode("utf-8")
        return data
    except Exception as _:
        return None
    finally:
        if connection:
            connection.close()


def bad_authen(idx, secret):
    # 
    # always trust local network
    # 
    return True


@app.route("/setcmd/<idx>/<secret>/<cmd>/")
def setcmd(idx=None, secret=None, cmd=None):
    if bad_authen(idx, secret):
        buffer[INSTRUCTION_IDX] = cmd
        return buffer[INSTRUCTION_IDX], 200
    else:
        abort(403)


@app.route("/getcmd/<idx>/<temp>/<humi>/")
def getcmd(idx=None, temp=None, humi=None):
    if idx:
        own_status['id'] = idx
    if temp:
        own_status['temp'] = temp
    if humi:
        own_status['humi'] = humi
    return buffer[INSTRUCTION_IDX]


@app.route("/getstatus/")
def getstatus():
    if NEED_OTHER_STATUS:
        geather_status = request_gateway_status()
        if geather_status:
            pass
        return None
    else:
        return json.dumps({own_status['id']: own_status})


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
    # app.run(host='0.0.0.0')
