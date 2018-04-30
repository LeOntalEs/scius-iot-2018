import cv2

for i in range(20):
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()
    if frame is None:
        continue
    else:
        print(i)
    while True:
        ret, frame = cap.read()
        cv2.imshow('img', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
