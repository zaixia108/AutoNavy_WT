import ctypes
import time
import pydirectinput as pdi
import win32api
import win32con
from win32con import MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, \
    MOUSEEVENTF_WHEEL
import keyboard

pdi.FAILSAFE = False

# -左+右 -上+下 +滚轮上 -滚轮下
KEYBOARD_MAPPING = {
    'f3': 0x3D,
    'f4': 0x3E,
    'delete': 0xD3 + 1024,
    'capslock': 0x3A,
    'f': 0x21,
    'g': 0x22,
    'h': 0x23,
    'j': 0x24,
    'l': 0x26,
    'enter': 0x1C,
    'return': 0x1C,
    'shift': 0x2A,
    'm': 0x32,
    ',': 0x33,
    '.': 0x34,
    '/': 0x35,
    'ctrl': 0x1D,
    'win': 0xDB + 1024,
    'alt': 0x38,
    'space': 0x39,
    'decimal': 0x53,
}


class Mouse:
    def __init__(self):
        pass

    def move(self, dx, dy):
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

    def click(self, pos=None):
        if pos:
            self.moveto(pos[0], pos[1])
        else:
            pass
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def double_click(self, pos=None):
        self.click(pos)
        time.sleep(0.1)
        self.click(pos)

    def right_click(self):
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0)
        time.sleep(0.01)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0)

    def scroll(self, num):
        mouse_event = ctypes.windll.user32.mouse_event
        if num > 0:
            for i in range(num):
                mouse_event(0x0800, 0, 0, 120, 0)
                time.sleep(0.05)
        else:
            for i in range(num):
                mouse_event(0x0800, 0, 0, -120, 0)
                time.sleep(0.05)

    def get_position(self):
        pos = win32api.GetCursorPos()
        return pos

    def moveto(self, x, y):
        win32api.SetCursorPos((x, y))

    def move_mouse(self, x, y):
        now_pos = self.get_position()
        delta_x = x - now_pos[0]
        delta_y = y - now_pos[1]
        self.move(delta_x, delta_y)


class Keyboard:
    def __init__(self):
        pass

    def keydown(self, key):
        pdi.keyDown(key)

    def keyup(self, key):
        pdi.keyUp(key)

    def press(self, key):
        pdi.press(key)

    def write(self, text):
        keyboard.write(text)

    def add_hotkey(self, key, callback):
        keyboard.add_hotkey(key, callback)

    def remove_hotkey(self, key):
        keyboard.remove_hotkey(key)

    def remove_all_hotkeys(self):
        keyboard.remove_all_hotkeys()

    def is_pressed(self, key):
        return keyboard.is_pressed(key)

    def wait(self, key):
        keyboard.wait(key)

    def wait_for_press(self, key):
        keyboard.wait_for_press(key)

    def wait_for_release(self, key):
        keyboard.wait_for_release(key)

    def release_all(self):
        for i, key in enumerate(KEYBOARD_MAPPING):
            self.keyup(key)
        print('按键释放完毕')


if __name__ == '__main__':
    time.sleep(1)
    keyboard = Keyboard()
    # keyboard.keydown('alt')
    # time.sleep(10)
    # keyboard.keyup('alt')
    keyboard.release_all()

    # for i in range(1000):-
    #     mouse.Relmove('UR')
    # from th_pool import thread_control
    # submit = thread_control.submit
    # a = submit(lambda :mouse.Relmove('UR'), 'MOV',True)
    # time.sleep(3)
    # a.stop()