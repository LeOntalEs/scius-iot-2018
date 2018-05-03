import json
from time import time, sleep
import threading
import traceback

import cv2
import numpy as np


BOT_REDIUS = 20
# DIR_COLOR = 32512
# ALL_COLORS = [0, 3698, 4232, 6050, 11250, 25312] + [DIR_COLOR]
DIR_COLOR = 0
# ALL_COLORS = [60, 130, 200, 300] + [DIR_COLOR]
ALL_COLORS = [30, 70, 110, 175] + [DIR_COLOR]
MISSING_OFFSET = 10

COLOR_OFFSET = 50
WIDTH, HEIGHT = 640, 480

master = None

with open('testindex.json', 'r') as fp:
    colormap = json.load(fp)


class Master:
    class __Master(threading.Thread):
        def __init__(self, bot_ids=None, cap=None):
            self.cap = cap
            self.bots = None
            self.currentidx = 0
            self.max_alloc = 2
            self.nbots = len(bot_ids)
            self.bot_ids = bot_ids
            self.latest_state = {
                str(x): self.get_init_status(x) for x in self.bot_ids}
            self.missing = {str(x): 0 for x in self.bot_ids}
            self.infos = [None for _ in range(self.max_alloc)]
            threading.Thread.__init__(self)

        def __exit__(self, exception_type, exception_value, traceback):
            if self.cap:
                self.cap.release()
            super(__Master, self).__exit__(
                exception_type, exception_value, traceback)

        def get_init_status(self, ids):
            return {
                'id': str(ids),
                'x': -1,
                'y': -1,
                'theta': -1,
            }

        def get_info(self):
            return self.infos[self.currentidx]

        def update(self):
            self.infos = self.infos

        def run(self):
            if self.cap:
                self.dojob()
            else:
                context = {str(k): self.get_init_status(k) for k in self.bot_ids}
                self.infos[self.currentidx] = context

        def dojob(self):
            while True:
                # sleep(3)
                start = time()
                # self.bots = list()
                try:
                    _, img = self.cap.read()
                    if img is None:
                        continue
                    timg = img.copy()
                    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # 20
                    circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 20,
                                               param1=75, param2=20, minRadius=2, maxRadius=35)[0]
                                            #    param1=40, param2=25, minRadius=2, maxRadius=50)[0]
                    for i in circles:
                        cv2.circle(timg, (i[0], i[1]), i[2], (255, 255, 0), 2)
                        cv2.circle(timg, (i[0], i[1]), 2, (255, 255, 0), 2, 3)

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
                        c = hsv[y, x, 0]
                        for bot in bots:
                            if bot.contain(x, y, r, c):
                                break
                    #
                    # remove unacceptable bot
                    #

                    def acceptable(bot): return len(bot.codes) > 3
                    bots = [bot for bot in bots if acceptable(bot)]

                    ubots = list()
                    unknown = set(str(x) for x in self.bot_ids)
                    context = {str(x): self.get_init_status(
                        x) for x in self.bot_ids}
                    for bot in bots:
                        bot.process()
                        if (not bot.id is None) and (bot.id in self.bot_ids):
                            context[bot.id] = bot.get_status()
                            unknown.difference_update(set([bot.id]))
                            self.missing[bot.id] = 0
                        else:
                            ubots.append(bot)
                    #
                    # find nearly to assiment unknow bot
                    #
                    def determine_exit(idx):
                        self.missing[idx] += 1
                        if self.missing[idx] > MISSING_OFFSET:
                            self.missing[idx] = MISSING_OFFSET+1
                            return self.get_init_status(idx)
                        else:
                            return self.latest_state[idx]

                    nubt = len(ubots)
                    nukw = len(unknown)
                    lst = [str(x) for x in list(unknown)]
                    if unknown:
                        if nukw == 1:
                            if nubt == 1:
                                bot = ubots[0]
                                bot.id = lst[0]
                                bot.find_direction()
                                context[bot.id] = bot.get_status()
                            else:
                                context[lst[0]] = determine_exit(lst[0])
                        else:
                            for idx in lst:
                                context[idx] = self.latest_state[idx]
                    for bot in bots:
                        if not bot.id:
                            continue
                        latest = self.latest_state[bot.id]
                        element = context[bot.id]
                        if (element['theta'] is None) and (not latest['theta'] is None):
                            element['theta'] = latest['theta']
                        if (element['x'] is None) and (not latest['x'] is None):
                            element['x'] = latest['x']
                        if (element['y'] is None) and (not latest['y'] is None):
                            element['y'] = latest['y']

                    context.pop(None, None)

                    self.latest_state = context
                    self.infos[self.currentidx] = context

                    if self.infos[self.currentidx]:
                        for info in sorted(self.infos[self.currentidx],key=lambda x: int(x)):
                            val = self.infos[self.currentidx][info]
                            print(val['id'], val['x'], val['y'], val['theta'])
                        print()

                    self.currentidx = (self.currentidx+1) % self.max_alloc
                    self.bots = bots
                    # print()
                    # print('bot count: ', len(self.bots))
                    # print(time()-start)
                except Exception as err:
                    pass
                    # print('from Master Error: ', err, type(err))
                    # print(traceback.format_exc())
                    # print(self.infos[self.currentidx])
    instance = None

    def __init__(self, bot_ids=None, cap=None):
        if not Master.instance:
            Master.instance = Master.__Master(bot_ids=bot_ids, cap=cap)
            Master.instance.start()
        else:
            pass

    def __getattr__(self, name):
        return getattr(self.instance, name)


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
        norm_color = self.norm_color(color)
        # print(color)
        # print(norm_color)
        # for c in ALL_COLORS:
        #     if abs(norm_color-c) < COLOR_OFFSET:
        #         print(norm_color, c, abs(norm_color-c))
        #         return c
        # return None
        d = [(abs(norm_color-c), c) for c in ALL_COLORS]
        return min(d, key=lambda x: x[0])[1]

    def norm_color(self, arr):
        return arr

    def sse(self, arr):
        avg = np.mean(arr)
        return int(np.sum(np.square(arr-avg)))

    def identify(self):
        try:
            self.id = str(colormap[str(tuple(c[-1] for c in self.id_codes))])
            print('IN BOT ID: ', self.id)
        except KeyError:
            self.id = None

    def find_direction(self):
        if not self.dir_code is None and not self.centroid is None:
            vx = (self.centroid[0]-self.dir_code[0],
                  self.centroid[1]-self.dir_code[1])
            self.direction = (np.rad2deg(
                np.arctan2(vx[0], vx[1])+np.pi) - 90) % 360
            if self.direction is None:
                self.direction = -1
            print('IN BOT DIRECTION: ', self.direction)

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
