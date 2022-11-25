import numpy as np
import cv2
from mss import mss

sct = mss()
y_portion = 0.4  # 数值越小，越往下， 从上往下头的比例距离
# Use the first monitor, change to desired monitor number
dimensions = sct.monitors[1]

# Compute the center square of the screen to parse
dimensions['left'] = dimensions['width'] // 2
dimensions['top'] = 0
dimensions['width'] = 500
dimensions['height'] = 500

# cap = cv2.VideoCapture(0)
# cap.set(3,640)
# cap.set(4,480)
# cap.set(10,100)#右往高亮，往低暗

def empty(a):
    pass
def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver
while True:
    # success,img = cap.read()
    img = np.asarray(sct.grab(dimensions))
    cv2.namedWindow("TrackBars")
    cv2.resizeWindow("TrackBars", 640, 400)
    cv2.createTrackbar("H_Min", "TrackBars", 0  , 255, empty)  # 跟踪杆
    cv2.createTrackbar("H_Max", "TrackBars", 255, 255, empty)  # 跟踪杆
    cv2.createTrackbar("S_Min", "TrackBars", 0  , 255, empty)  # 跟踪杆
    cv2.createTrackbar("S_Max", "TrackBars", 255, 255, empty)  # 跟踪杆
    cv2.createTrackbar("V_Min", "TrackBars", 0  , 255, empty)  # 跟踪杆
    cv2.createTrackbar("V_Max", "TrackBars", 255, 255, empty)  # 跟踪杆
    while True:
        # success,img = cap.read()
        img = np.asarray(sct.grab(dimensions))
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 将BGR转换为HSV
        h_min = cv2.getTrackbarPos("H_Min", "TrackBars")  # 设定杆
        h_max = cv2.getTrackbarPos("H_Max", "TrackBars")  # 设定杆
        s_min = cv2.getTrackbarPos("S_Min", "TrackBars")  # 设定杆
        s_max = cv2.getTrackbarPos("S_Max", "TrackBars")  # 设定杆
        v_min = cv2.getTrackbarPos("V_Min", "TrackBars")  # 设定杆
        v_max = cv2.getTrackbarPos("V_Max", "TrackBars")  # 设定杆
        lower = np.array([h_min, s_min, v_min])  # 确定最小
        upper = np.array([h_max, s_max, v_max])  # 确定最大
        mask = cv2.inRange(imgHSV, lower, upper)  # 蒙盖
        imgResult = cv2.bitwise_and(img, img, mask=mask)  # 结果
        # imgStack = stackImages(0.6, ([img, imgHSV], [mask, imgResult]))  # 拼接
        cv2.imshow("STACK", imgResult)
 
        cv2.waitKey(1)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break