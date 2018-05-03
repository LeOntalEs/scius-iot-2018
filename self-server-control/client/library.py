import json
import math
from time import sleep  # sleep(second)
import http.client

import numpy as np

from flask_socketio import SocketIO, send, emit
from flask import Flask, request, render_template

from melody import Melody


##### EDIT HEAR #####
ID = '4'
secret = '1234'
#####################
# MARK : Server Service
locationHostIP = "localhost:5000"

WIDTH = 640
HEIGHT = 480

isPrintAction = False


def printAction(message):
    if isPrintAction:
        print(message)


Data = {'isEnable': True,
        'led': {'r': 0, 'g': 0, 'b': 0},
        'motor': [0, 0, 0, 0],
        'temp': 0,
        'humi': 0,
        'sound': {'melody': 0, 'melodykey': '', 'duration': 4},
        'location': {'x': 0, 'y': 0, 'direction': 0}}
rawData = {}

# minSpeed = 600
# maxSpeed = 999
minSpeed = 600
maxSpeed = 999

dhtEnable = False

# MARK : Local Service


def led(r, g, b):
    Data['led']['r'] = r
    Data['led']['g'] = g
    Data['led']['b'] = b
    printAction('[car] LED - R:'+str(r)+' G:'+str(g)+' B:'+str(b))
    upload()


def sound(melody, duration=4):
    global Data
    if melody in Melody:
        Data['sound']['melodykey'] = melody
        Data['sound']['melody'] = Melody[melody]
    else:
        Data['sound']['melody'] = 0
        printAction('[car] Sound - Melody Incorrect')
        return
    Data['sound']['duration'] = duration
    printAction('[car] Sound - Melody:'+str(melody))
    upload()


def sounds(notes):
    noteArray = notes.split(' ')
    for note in noteArray:
        sound(note)
        sleep(0.4)


fieldHeight = 1000
fieldWidth = 1000


def directionFromPoint(x, y):
    differentX = x - Data['location']['x']
    differentY = y - Data['location']['y']
    if differentX == 0 and differentY == 0:
        targetDirection = 0
    elif differentX == 0:
        if differentY >= 0:
            targetDirection = 90
        else:
            targetDirection = 270
    elif differentY == 0:
        if differentX >= 0:
            targetDirection = 0
        else:
            targetDirection = 180
    else:
        targetDirection = math.atan(differentY/differentX) * (180/math.pi)
        if differentX > 0 and differentY > 0:  # Q1
            pass
        elif differentX < 0 and differentY > 0:  # Q2
            targetDirection += 90
        elif differentX < 0 and differentY < 0:  # Q3
            targetDirection += 180
        elif differentX > 0 and differentY < 0:  # Q4
            targetDirection += 360
    return targetDirection

def goto(x, y, rspeed, fspeed):
    offset = 50
    y = HEIGHT - y
    update()
    print('move to: ', x, y)
    print(y, HEIGHT - rawData[ID]['y'])
    while True:
        update()
        bx, by = rawData[ID]['x'], HEIGHT - rawData[ID]['y']
        if abs(x-bx) < offset and abs(y-by) < offset:
            break
 
        vec = (x-bx, by-y)
        theta = np.arctan2(vec[1], vec[0]) * 180 / np.pi
        if theta < 0:
            theta += 360

        rotate(theta, rspeed)
        update()
        motor(fspeed, fspeed)
        sleep(0.1)
        stop()
        sleep(0.1)
    

def rotate(direction, speed):
    direction = int(direction)%360
    update()
    maxError = 10
    while True:
        if abs(direction-Data['location']['direction']) < maxError:
            return
        cnt = 0
        tmp = Data['location']['direction']
        while True:
            if tmp == direction: 
                break
            tmp = (tmp+1)%360
            cnt += 1
        if cnt > 180:
            motor(speed, -speed)
        else:
            motor(-speed, speed)
        sleep(0.0025)
        stop()
        sleep(0.1)
        update()
        
    # print(Data)
    # print(direction, Data['location']['direction'])
    # differentDirection = direction - Data['location']['direction']
    # print(differentDirection)
    # while math.fabs(differentDirection) > maxError:
    #     if differentDirection > 0:
    #         motor(-speed, speed)
    #     else:
    #         motor(speed, -speed)
    #     sleep(0.001)
    #     stop()
    #     sleep(0.3)
    #     update()
    #     differentDirection = direction - Data['location']['direction']


def motor(L, R):  # L,R is (Int) -999(maxSpeed) to 999(maxSpeed)
    # Protection
    if L < -maxSpeed:
        L = -maxSpeed
    elif L > maxSpeed:
        L = maxSpeed
    if R < -maxSpeed:
        R = -maxSpeed
    elif R > maxSpeed:
        R = maxSpeed
    # Action
    if L < 0:
        Data['motor'][0] = 0
        Data['motor'][1] = abs(L)
    else:
        Data['motor'][0] = abs(L)
        Data['motor'][1] = 0
    if R < 0:
        Data['motor'][2] = 0
        Data['motor'][3] = abs(R)
    else:
        Data['motor'][2] = abs(R)
        Data['motor'][3] = 0
    printAction('[car] Motor - L:'+str(L)+' R:'+str(R))
    # print(Data['motor'])
    upload()


def humi():
    printAction('[car] Humi '+str(Data['humi'])+' %')
    return Data['humi']


def temp():
    printAction('[car] Temp '+str(Data['temp'])+' *c')
    return Data['temp']


def offsensor():
    global dhtEnable
    dhtEnable = False
    upload()


def onsensor():
    global dhtEnable
    dhtEnable = True
    upload()


def requestServer(path):
    connection = http.client.HTTPConnection(locationHostIP)
    connection.request("GET", path)
    response = connection.getresponse()
    data = response.read().decode("utf-8")
    connection.close()
    return data


def upload():
    dataForSend = str(("{0:0=3d}".format(int(Data['motor'][0]))) +
                      ("{0:0=3d}".format(int(Data['motor'][1]))) +
                      ("{0:0=3d}".format(int(Data['motor'][2]))) +
                      ("{0:0=3d}".format(int(Data['motor'][3]))) +
                      ("{0:0=3d}".format(int(Data['led']['r']))) +
                      ("{0:0=3d}".format(int(Data['led']['g']))) +
                      ("{0:0=3d}".format(int(Data['led']['b']))) +
                      ("{0:0=4d}".format(int(Data['sound']['melody']))) +
                      ("{0:0=1d}".format(int(Data['sound']['duration']))) +
                      ("{0:0=1d}".format(int(dhtEnable))))
    requestServer('/setcmd/'+str(ID)+'/'+secret+'/'+dataForSend+'/')


def update():
    global Data, rawData
    printAction('[car] request...')
    rawData = json.loads(requestServer('/getstatus/'))
    Data['location']['x'] = rawData[ID]['x']
    Data['location']['y'] = rawData[ID]['y']
    Data['location']['direction'] = rawData[ID]['theta']
    Data['temp'] = rawData[ID]['temp']
    Data['humi'] = rawData[ID]['humi']

def getx(idx):
    data = rawData.get(str(idx), None)
    if data:
        return data['x']
    else:
        return -1

def gety(idx):
    data = rawData.get(str(idx), None)
    if data:
        return data['y']
    else:
        return -1

def getdegree(idx):
    data = rawData.get(str(idx), None)
    if data:
        return data['theta']
    else:
        return -1

# def rotate()

def stop():
    motor(0, 0)


def reset():
    motor(0, 0)
    sound('0')
    led(0, 0, 0)
