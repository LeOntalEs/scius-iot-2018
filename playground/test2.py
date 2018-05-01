import json
from heapq import heappush, heappop
import cv2
import numpy as np
from time import time
MAX_CODE = 3
BOT_REDIUS = 40 
ALL_COLORS = [6, 18, 62, 97, 110, 150, 170]
DIR_COLOR = 6
COLOR_OFFSET = 10
WIDTH, HEIGHT = 800, 600

with open('cindex.json', 'r') as fp:
    colormap = json.load(fp)

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
        for c in ALL_COLORS:
            if abs(color-c) < COLOR_OFFSET:
                return c
        return None

    def identify(self):
        try:
            self.id = colormap[str(tuple(c[-1] for c in self.id_codes))]
        except KeyError:
            self.id = None

    def find_direction(self):
        if not self.dir_code is None and not self.centroid is None:
            vx = (self.centroid[0]-self.dir_code[0],
                self.centroid[1]-self.dir_code[1])
            self.direction = (np.rad2deg(np.arctan2(vx[0], vx[1])+np.pi) - 90) % 360

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
        
def code_in_bot(code, bot):
    bx, by, br = bot['centroid']
    cx, cy, _ = code
    distance = np.sqrt((cx-bx)**2 + (cy-by)**2)
    return distance < br

start = time()

_s = time()
img = cv2.imread('out4.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
timg = img.copy()
print(time()-_s)
_s = time()
circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT,1,20,
                            param1=40, param2=25, minRadius=5, maxRadius=50)[0]
print(time()-_s)
_s = time()
bots = list()
code_circles = list()
for circle in circles:
    if circle[2] >= BOT_REDIUS:
        bots.append(Bot(circle))   
    else:
        code_circles.append(circle)

all_colors = set()
for code in code_circles:
    x, y, r = (int(x) for x in code)
    c = hsv[y, x, 0]
    for bot in bots:
        if bot.contain(x, y, r, c):
            break

# infos = sorted([b.get_status() for b in bots], key=lambda x: x['id'])
# for info in infos:
#     print(info)

ucnt = -1
info = dict()
for bot in bots:
    bot.process()
    if not bot.id is None :
        ids = bot.id
    else:
        ids = ucnt
        ucnt -= 1
    info[ids] = bot.get_status()
print(info)
