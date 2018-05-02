import json
from time import sleep
from threading import Thread

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import cv2
from app.bot import Master

BOT_IDS = [14, 32]
BOT_IDS = [i for i in range(20)]
BOT_IDS = [str(x) for x in BOT_IDS]
BOT_SECRET = {str(k): str(k) for k in BOT_IDS}

STOP_IDX = 0
TURN_TIME = 0.5
STOP_TIME = 1
INSTRUCTION_IDX = 1

current_idx = 0
# cap = cv2.VideoCapture(0)
cap = None
buffer = [{str(k): '0'*27 for k in BOT_IDS}, {str(k): '0'*27 for k in BOT_IDS}]

class Synchronizer(Thread):
    def __init__(self, is_sleep=False, *args, **kwargs):
        super(Synchronizer, self).__init__(*args, **kwargs)
        self.currentidx = 0
        self.is_sleep = is_sleep

    def run(self):
        self.currentidx = INSTRUCTION_IDX
        while True:
            if self.is_sleep:
                self.currentidx = (self.currentidx + 1) % 2
                if self.currentidx == INSTRUCTION_IDX:
                    sleep(TURN_TIME)
                else:
                    sleep(STOP_TIME)
            else:
                pass

sync = Synchronizer(is_sleep=False)
sync.start()

def get_init_status(idx):
    return {
        'id': idx,
        'x': -1,
        'y': -1,
        'theta': -1,
        'temp': 0,
        'humi': 0,
    }


status = {k: get_init_status(k) for k in BOT_IDS}

master = Master(bot_ids=BOT_IDS, cap=cap)


def bad_authen(idx, secret):
    if idx in BOT_SECRET and BOT_SECRET[idx] == secret:
        return True
    return False
    

def setcmd(request, idx=None, secret=None, cmd=None):
    if bad_authen(idx, secret):
        buffer[INSTRUCTION_IDX][idx] = cmd
        return HttpResponse(buffer[INSTRUCTION_IDX][idx], status=200)
    else:
        return HttpResponse(status=404)

def getcmd(request, idx=None, temp=None, humi=None):
    temp = int(temp)
    humi = int(humi)
    if request.method == 'GET':
        if idx and idx in BOT_IDS:
            if temp:
                status[idx]['temp'] = temp
            if humi:
                status[idx]['humi'] = humi
            return HttpResponse(buffer[sync.currentidx][idx])
        else:
            return HttpResponse('Not found device', status=404)

def int_or_none(val):
    if val is None:
        return -1
    elif isinstance(val, str) and val.isdigit():
        return int(val)
    else:
        return int(val)
def getstatus(request):
    infos = master.get_info()
    for k, v in infos.items():
        status[k]['x'] = int_or_none(v['x'] )
        status[k]['y'] = int_or_none(v['y'] )
        status[k]['theta'] = int_or_none(v['theta'])
    return JsonResponse(status, safe=False)

def test(request):
    infos = master.get_info()
    for info in infos:
        val = infos[info]
        print(val['id'], val['x'], val['y'], val['theta'])
