from interception import ffi, lib
from interception.utils import raise_process_priority

import threading
import time

SCANCODE_ESC = 0x01


INTERCEPTION_MOUSE_MOVE_RELATIVE = 0x000
INTERCEPTION_MOUSE_MOVE_ABSOLUTE = 0x001
INTERCEPTION_MOUSE_VIRTUAL_DESKTOP = 0x002
INTERCEPTION_MOUSE_ATTRIBUTES_CHANGED = 0x004
INTERCEPTION_MOUSE_MOVE_NOCOALESCE = 0x008
INTERCEPTION_MOUSE_TERMSRV_SRC_SHADOW = 0x100
INTERCEPTION_MOUSE_CUSTOM = 0x200
INTERCEPTION_MAX_KEYBOARD = 10


INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN = 0x001
INTERCEPTION_MOUSE_LEFT_BUTTON_UP = 0x002
INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN = 0x004
INTERCEPTION_MOUSE_RIGHT_BUTTON_UP = 0x008
INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN = 0x010
INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP = 0x020

def INTERCEPTION_KEYBOARD(index):
    return index + 1


def INTERCEPTION_MOUSE(index):
    return INTERCEPTION_MAX_KEYBOARD + index + 1

class MouseThread(threading.Thread):
    
    def __init__(self, deviceId, aimmode) -> None:
        super(MouseThread,self).__init__()
        raise_process_priority()
        self.context = lib.interception_create_context()
        self.emptyStroke = ffi.new('InterceptionMouseStroke *')
        self.deviceId = deviceId
        self.stroke = ffi.new('InterceptionMouseStroke *')
        self.stroke.flags = INTERCEPTION_MOUSE_MOVE_RELATIVE | INTERCEPTION_MOUSE_CUSTOM
        self.keystroke = ffi.new('InterceptionKeyStroke *')
        lib.interception_set_filter(self.context, lib.interception_is_mouse, lib.INTERCEPTION_FILTER_MOUSE_MOVE)
        self.isInjected = False
        self.X = 0.0#缩放后的冗余值
        self.Y = 0.0
        self.speed = 0.0
        self.aimmode = aimmode #吸附模式
    def run(self):
        while True and not self.isInjected:
            # 如果收到退出信号，就退出
            device = lib.interception_wait(self.context)
            if not lib.interception_receive(self.context, device, self.emptyStroke, 1):
                break
            if self.aimmode == 4 and self.speed != 0.0:
                movex, movey = self.emptyStroke.x*self.speed, self.emptyStroke.y*self.speed
                self.emptyStroke.x = int(movex + self.X)
                self.emptyStroke.y = int(movey+ self.Y)
                self.X = self.X + movex - int(self.emptyStroke.x)
                self.Y = self.Y + movey - int(self.emptyStroke.y)
            lib.interception_send(self.context, device, self.emptyStroke, 1)
        lib.interception_destroy_context(self.context)
    def move(self, x, y):
        self.stroke.x = x
        self.stroke.y = y
        lib.interception_send(self.context, self.deviceId, self.stroke, 1)
        
    def click(self):
        self.state= 0
        self.keystroke.code = INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
        lib.interception_send(self.context, self.deviceId, self.keystroke, 1)
        time.sleep(0.3)
        self.keystroke.code = INTERCEPTION_MOUSE_LEFT_BUTTON_UP
        lib.interception_send(self.context, self.deviceId, self.keystroke, 1)
        
    def setSpeed(self, speed):
        self.speed = speed
    def resetSpeed(self):
        self.speed = 0.0
        self.X = 0.0
        self.Y = 0.0
    def stop(self):
        print("stop")
        self.isInjected = True
    def isStop(self):
        return self.isInjected