import cv2
import numpy as np
MAX_CODE = 3
BOT_REDIUS = 40 
ALL_COLORS = [6, 18, 62, 97, 110, 150, 170]
DIR_COLOR = 6
COLOR_OFFSET = 10
WIDTH, HEIGHT = 800, 600

def sse(arr):
    print(arr)
    avg = np.mean(arr)
    return int(np.sum(np.square(arr-avg)))

img = cv2.imread('out5.png')
timg = img.copy()
gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 20,
                        param1=40, param2=25, minRadius=5, maxRadius=50)[0]
bots = list()
code_circles = list()
all_colors = set()
# print(len(circles))
for circle in circles:
    x, y, r = (int(x) for x in circle)
    rc = hsv[y, x, 0:3:2]
    if rc[0] == 0 and rc[1] == 255:
        continue
    c = sse(rc)
    all_colors.add(c)
    cv2.circle(timg,(x, y), r, (255, 255, 0), 1)
    cv2.circle(timg,(x, y), 1, (255, 255, 0), 1)
print(sse([0, 255]))
print(sorted(all_colors))
cv2.imshow('img', timg)
if cv2.waitKey(1000*60) & 0xFF == ord('q'):
    pass
