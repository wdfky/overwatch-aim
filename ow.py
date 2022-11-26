import cv2
from math import pow, sqrt
from mss import mss
import numpy as np
from mouse import MouseThread
import  win32con, win32api
import lib.viz as viz
import time
import random
if __debug__:
    cv2.namedWindow('res', cv2.WINDOW_NORMAL)

# The size of the window to scan for targets in, in pixels
# i.e. SQUARE_SIZE of 600 => 600 x 600px
SQUARE_SIZE = 600
viz.SQUARE_SIZE = SQUARE_SIZE

# 瞄准模式，0为默认左键，1为右键， 2为左右键， 3为自动开枪，4是摁住左键吸附瞄准
aim_mode = 4
aim_jitter_percent=0
# 游戏灵敏度
sensitivity=10.0
# 每次最多移动多少像素,锁死可能需要10+
aim_max_move_pixels=3

# 自动涉及模式的误差，太小了会导致不会开火
flick_shoot_pixels=2
# 开枪休息时间 (200 for 麦克雷, 350 for 艾什, 270 for 百合)
flick_pause_duration=210

# 吸附模式范围
flick_range=4
# 吸附模式速度减到多少
flick_speed = 0.2

# The maximum possible pixel distance that a character's center
# can be before locking onto them
TARGET_SIZE = 100
MAX_TARGET_DISTANCE = sqrt(2 * pow(TARGET_SIZE, 2))
viz.TARGET_SIZE = TARGET_SIZE
viz.MAX_TARGET_DISTANCE = MAX_TARGET_DISTANCE

# Create an instance of mss to capture the selected window square
sct = mss()

# Use the first monitor, change to desired monitor number
dimensions = sct.monitors[1]

# Compute the center square of the screen to parse
dimensions['left'] = int((dimensions['width'] / 2) - (SQUARE_SIZE / 2))
dimensions['top'] = int((dimensions['height'] / 2) - (SQUARE_SIZE / 2))
dimensions['width'] = SQUARE_SIZE
dimensions['height'] = SQUARE_SIZE


# Calls the Windows API to simulate mouse movement events that are sent to OW
def mouse_move(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)


# Determines if the Caps Lock key is pressed in or not
def is_activated(aim_mod: int):
    if aim_mod == 0:
        return win32api.GetAsyncKeyState(win32con.VK_LBUTTON)
    if aim_mod == 1:
        return win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
    if aim_mod == 2:
        return win32api.GetAsyncKeyState(win32con.VK_LBUTTON) or win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
    if aim_mod == 4:
        return win32api.GetAsyncKeyState(win32con.VK_LBUTTON) or win32api.GetAsyncKeyState(win32con.VK_RBUTTON)
    return False
    # return win32api.GetAsyncKeyState(0x14) != 0
        
def locate_target(target):
    # compute the center of the contour
    moment = cv2.moments(target)
    if moment["m00"] == 0:
        return

    cx = int(moment["m10"] / moment["m00"])
    cy = int(moment["m01"] / moment["m00"])

    mid = SQUARE_SIZE / 2
    x = -(mid - cx) if cx < mid else cx - mid
    y = -(mid - cy) if cy < mid else cy - mid

    target_size = cv2.contourArea(target)
    distance = sqrt(pow(x, 2) + pow(y, 2))

    # There's definitely some sweet spot to be found here
    # for the sensitivity in regards to the target's size
    # and distance
    slope = ((1.0 / 3.0) - 1.0) / (MAX_TARGET_DISTANCE / target_size)
    multiplier = ((MAX_TARGET_DISTANCE - distance) / target_size) * slope + 1


    # moveSmooth(int(x * multiplier), int(y * multiplier), AimSpeed)

    if __debug__:
        # draw the contour of the chosen target in green
        cv2.drawContours(frame, [target], -1, (0, 255, 0), 2)
        # draw a small white circle at their center of mass
        cv2.circle(frame, (cx, cy), 7, (255, 255, 255), -1)
    return int(x * multiplier), int(y * multiplier)

    
mouse = MouseThread(12, aim_mode)
mouse.start()

isSlow = False
# Main lifecycle
while True:

    frame = np.asarray(sct.grab(dimensions))
    contours = viz.process(frame)
    # For now, just attempt to lock on to the largest contour match
    if len(contours) > 1:
        # contour[0] == bounding window frame
        # contour[1] == closest/largest character
        x, y = locate_target(contours[1])
        randomSensitivityMultiplier = 1.0 - random.uniform(0.0, aim_jitter_percent)/100.0
        moveX, moveY =  x/sensitivity*randomSensitivityMultiplier, y/sensitivity*randomSensitivityMultiplier
        # 自动开火模式
        last_time = time.perf_counter()
        if aim_mode == 3:
            if abs(moveX) < flick_shoot_pixels and abs(moveY) < flick_shoot_pixels:
                mouse.click()
                time.sleep(flick_pause_duration/1000.0)
        # 吸附模式
        elif aim_mode == 4 and not isSlow and is_activated(aim_mode):
            if moveX < flick_range and moveY < flick_range :
                isSlow = True
                mouse.setSpeed(flick_speed)
        elif aim_mode == 4 and isSlow and not is_activated(aim_mode):
            isSlow = False
            mouse.resetSpeed()
        # 吸附模式不要自瞄
        elif aim_mode != 4 and is_activated(aim_mode):
            mouse.move(min(int(moveX), aim_max_move_pixels), min(int(moveY), aim_max_move_pixels))
    else:
        if isSlow:
            isSlow = False
            mouse.resetSpeed()
    if __debug__:
        # Green contours are the "character" matcheqs
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
        cv2.imshow('res', frame)
    # Press `[` to stop the program
    if cv2.waitKey(1) & 0xFF == ord("["):
            break


mouse.stop()
sct.close()
cv2.destroyAllWindows()
