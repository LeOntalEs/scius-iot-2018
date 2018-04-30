import cv2

img = cv2.imread('out5.png')
gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
params = list()
for p1 in range(10, 70, 5):
    for p2 in range(10, 100, 5):
        params.append( (p1, p2) )
# params = [(65, 26, 3, 50)]

for param in params:
    timg = img.copy()
    circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 2,
                                param1=param[0], param2=param[1], minRadius=3, maxRadius=10)
    if not circles is None:
        print(param, circles.shape)
        for i in circles[0,:]:
            cv2.circle(timg,(i[0],i[1]),i[2],(255,255,0),2)
            cv2.circle(timg,(i[0],i[1]),2,(255,255,0),3)

    circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 10,
                                param1=param[0], param2=param[1], minRadius=20, maxRadius=50)
    if not circles is None:
        for i in circles[0,:]:
            cv2.circle(timg,(i[0],i[1]),i[2],(255,0,255),2)
            cv2.circle(timg,(i[0],i[1]),2,(255,0,255),3)

    cv2.imwrite('out/out{}_{}.png'.format(*param), timg)