import json
from time import time
import threading

import cv2
import numpy as np


BOT_REDIUS = 20
# DIR_COLOR = 32512
# ALL_COLORS = [0, 3698, 4232, 6050, 11250, 25312] + [DIR_COLOR]
DIR_COLOR = 0
# ALL_COLORS = [60, 130, 200, 300] + [DIR_COLOR]
ALL_COLORS = [30, 65, 105, 160] + [DIR_COLOR]

COLOR_OFFSET = 50
WIDTH, HEIGHT = 640, 480

with open('testindex.json', 'r') as fp:
    colormap = json.load(fp)

class Master(threading.Thread):
    def __init__(self, bot_ids=None, cap=None):
        threading.Thread.__init__(self)
        if cap is None:
            cap = cv2.VideoCapture(1)
        self.cap = cap
        self.currentidx = 0
        self.max_alloc = 50
        self.bot_ids = bot_ids
        self.infos = [None for _ in range(self.max_alloc)]

    def __exit__(self, exception_type, exception_value, traceback):
        if self.cap:
            self.cap.release()
        super(Master, self).__exit__(exception_type, exception_value, traceback)

    def get_init_status(self, ids):
        return {
            'id': ids,
            'x': -1,
            'y': -1,
            'theta': -1,
        } 

    def get_info(self):
        return self.infos[self.currentidx]

    def run(self):
        while True:
            start = time()
            try:
                # img = cv2.imread('out5.png')
                _, img = self.cap.read()
                if img is None:
                    continue
                timg = img.copy()
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 20,
                                        param1=40, param2=25, minRadius=2, maxRadius=50)[0]
                # for i in circles:
                #     cv2.circle(timg, (i[0], i[1]), i[2], (255, 255, 0), 2)
                #     cv2.circle(timg, (i[0], i[1]), 2, (255, 255, 0), 2, 3)

                cv2.imshow('img', timg)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                bots = list()
                code_circles = list()
                for circle in circles:
                    if circle[2] >= BOT_REDIUS:
                        bots.append(Bot(circle))
                    else:
                        code_circles.append(circle)
                for code in code_circles:
                    x, y, r = (int(x) for x in code)
                    # c = hsv[y, x, 0:3:2]
                    c = hsv[y, x, 0]
                    for bot in bots:
                        if bot.contain(x, y, r, c):
                            break
                context = {x: self.get_init_status(x) for x in self.bot_ids}
                for bot in bots:
                    bot.process()
                    # print(bot.id)
                    if bot.id != None:
                        context[bot.id] = bot.get_status()
                self.infos[self.currentidx] = context
                self.currentidx = (self.currentidx+1) % self.max_alloc
                self.bots = bots
                print(time()-start)
            except Exception as err:
                print(err)

class Bot:

    def __init__(self, circle):
        self.id = None
        self.dir_code = None
        self.direction = None
        self.codes = list()
        self.id_codes = list()
        self.radius = circle[2]
        self.centroid = circle[0], circle[1]

    def get_status(self):
        if self.id == None or self.direction == None:
            self.process()
        return {
            'id': self.id,
            'x': self.centroid[0],
            'y': HEIGHT - self.centroid[1],
            'theta': self.direction,
        }

    def process(self):
        self.identify()
        self.find_direction()

    def normalize_color(self, color):
        # print(color)
        # print(norm_color)
        # for c in ALL_COLORS:
        #     if abs(norm_color-c) < COLOR_OFFSET:
        #         print(norm_color, c, abs(norm_color-c))
        #         return c
        # return None
        norm_color = self.norm_color(color)
        d = [(abs(norm_color-c), c) for c in ALL_COLORS]
        return min(d, key=lambda x: x[0])[1]
    
    def norm_color(self, arr):
        return arr
    
    def sse(self, arr):
        avg = np.mean(arr)
        return int(np.sum(np.square(arr-avg)))

    def identify(self):
        try:
            # print(self.id_codes)
            self.id = colormap[str(tuple(c[-1] for c in self.id_codes))]
        except KeyError:
            self.id = None

    def find_direction(self):
        if not self.dir_code is None and not self.centroid is None:
            vx = (self.centroid[0]-self.dir_code[0],
                  self.centroid[1]-self.dir_code[1])
            self.direction = (np.rad2deg(
                np.arctan2(vx[0], vx[1])+np.pi) - 90) % 360

    def add_code(self, x, y, r, c):
        nc = self.normalize_color(c)
        circle = np.array((x, y, r, nc))
        self.codes.append(circle)
        if nc == DIR_COLOR:
            self.dir_code = circle
        else:
            self.id_codes.append(circle)

    def distance(self, x, y):
        cx, cy = self.centroid
        return np.sqrt((cx-x)**2 + (cy-y)**2)

    def contain(self, x, y, r, c):
        distance = self.distance(x, y)
        ismember = distance < self.radius
        if ismember:
            self.add_code(x, y, r, c)
            return True
        else:
            return False
