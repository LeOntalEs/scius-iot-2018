import json
from time import sleep
from collections import OrderedDict

import cv2
import numpy as np

from bot import Bot

ALL_COLORS = [60, 130, 200, 300]

def f(c, all_prob, unique, d, md, all_colors):
    if not c:
        c = []
    if d == md:
        all_prob.append(c)
        v = "({})".format(', '.join(str(x) for x in sorted(c)))
        if not v in unique:
            unique.append(v)
    else:
        for x in all_colors:
            _c = c + [x]
            f(_c, all_prob, unique, d+1, md, all_colors)


def combi(all_colors):
    k = dict()
    unique = list()
    all_prob = list()
    f([], all_prob, unique, 0, 4, all_colors)
    idxs = {c: i for i, c in enumerate(unique)}
    for c in all_prob:
        sorted_c = sorted(c)
        kc1 = "({})".format(', '.join(str(x) for x in c))
        kc2 = "({})".format(', '.join(str(x) for x in sorted_c))
        k[kc1] = idxs[kc2]
    k = OrderedDict(sorted(k.items(), key=lambda x: x[1]))
    return k, unique


def norm_color(val):
    return val

def sse(arr):
    avg = np.mean(arr)
    return int(np.sum(np.square(arr-avg)))

def detect_circle(img):
    gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=40, param2=25, minRadius=5, maxRadius=50)[0]
    return circles

def get_all_color(cap):
    while True:
        _, img = cap.read()
        timg = img.copy()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 20,
                                    param1=40, param2=25, minRadius=5, maxRadius=50)[0]
        all_code = list()
        all_colors = list()
        for i in circles:
            x, y = i[0], i[1]
            cv2.circle(timg, (i[0], i[1]), i[2], (255, 255, 0), 2)
            cv2.circle(timg, (i[0], i[1]), 2, (255, 255, 0), 2, 3)
            y, x = int(y), int(x)
            # code = norm_color(hsv[y, x, 0:3:2])
            code = norm_color(hsv[y, x, 0])
            if not code in all_code:
                all_code.append(code)
                all_colors.append(tuple(hsv[y, x]))

        cv2.imshow('img', timg)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        # sleep(3)
            
    return all_code, all_colors

if  __name__ == '__main__':
    cap = None
    try:
        cap = cv2.VideoCapture(0)
        # 
        # 1. Run this to get all centriod color 
        #       then, set to ALL COLOR 
        # 
        # codes, colors = get_all_color(cap)
        # for z in zip(codes, colors):
        #     print(z)
        # print(sorted(codes))
        # codes = ALL_COLORS
        # codes = [30, 65, 105, 160]
        # [4, 64, 107, 110, 166]
        codes = [30, 70, 110, 175]

        # 
        # 2. generate cindex.json
        # 
        k, idxs = combi(codes)
        with open('testindex.json', 'w+') as fp:
            json.dump(k, fp, indent=2)
    finally:
        cv2.destroyAllWindows()
        if cap:
            cap.release()
