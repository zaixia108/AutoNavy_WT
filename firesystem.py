import ctypes
import math
import os
import random
import sys
import time

import cv2
import numpy as np
import win32con

from toolkit import scn
from simple_pid import PID
from toolkit import map
from toolkit import deg_cal
from toolkit import MnK
from toolkit import img_map

from debug import TimeDebug

debug = TimeDebug()
mark = debug.mark

PID_mouse_x = PID(0.6, 0, 0.02, setpoint=0)
PID_mouse_x.output_limits = (-30, 30)
PID_mouse_y = PID(0.6, 0, 0.02, setpoint=0)
PID_mouse_y.output_limits = (-30, 30)

aim = cv2.imread('src/cir.png', cv2.IMREAD_UNCHANGED)
mouse = MnK.Mouse()
keyboard = MnK.Keyboard()

D = scn.D
time.sleep(1)




class fire_control:

    def __init__(self):
        self.lock_on = False
        self.zoom = False
        self.exzoom = False
        self.lock = False
        # print(D.check_grab_state())
        time.sleep(1)
        image = D.now_img
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        ammo = image[660:690, 480:520]
        cv2.imshow('ammo', ammo)
        self.ammo = ammo

    def set_zoom(self, state):
        if state == 0:
            if self.zoom and not self.exzoom:
                keyboard.press('shift')
                self.zoom = False
            elif not self.zoom and self.exzoom:
                mouse.right_click()
                self.exzoom = False
            elif self.zoom and self.exzoom:
                mouse.right_click()
                self.exzoom = False
                keyboard.press('shift')
                self.zoom = False
            elif not self.zoom and not self.exzoom:
                pass
        elif state == 1:
            if not self.zoom and not self.exzoom:
                keyboard.press('shift')
                self.zoom = True
            elif not self.zoom and self.exzoom:
                keyboard.press('shift')
                self.zoom = True
                mouse.right_click()
                self.exzoom = False
            elif self.zoom and not self.exzoom:
                pass
            elif self.zoom and self.exzoom:
                mouse.right_click()
                self.exzoom = False
        elif state == 2:
            if not self.exzoom and not self.zoom:
                keyboard.press('shift')
                self.zoom = True
                mouse.right_click()
                self.exzoom = True
            elif not self.exzoom and self.zoom:
                mouse.right_click()
                self.exzoom = True
            elif self.exzoom and not self.zoom:
                keyboard.press('shift')
                self.zoom = True
            elif self.exzoom and self.zoom:
                pass

    def lock_and_fire(self):
        PID_mouse_x.setpoint = 0
        img = D.now_img
        ammo = self.ammo
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array([33, 109, 149])
        upper = np.array([137, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        mask = mask[200:510, 370:910]
        res = scn.match_img_ltrb(mask, aim, 0.3)[0]
        if res != -1:
            lt = res[0][0] + 370, res[0][1] + 200
            rb = res[1][0] + 370, res[1][1] + 200
            self.lock = True
        else:
            lt = 0, 0
            rb = 0, 0
            # TODO: 找识别不到目标时的处理方法
            background = img[380:420, 890:960]
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 255, 46])
            background = cv2.cvtColor(background, cv2.COLOR_BGR2HSV)
            mask_black = cv2.inRange(background, lower_black, upper_black)
            pos, val = scn.match_img_ltrb(img_map.lock, mask_black, 0.3)
            if pos != -1:
                self.lock = True
            else:
                self.lock = False
                result = self.serach()
                if result is None:
                    time.sleep(0.01)
                    self.lock_and_fire()
                    keyboard.press('x')
                self.lock_and_fire()
        tcenter = (lt[0] + rb[0]) // 2, (lt[1] + rb[1]) // 2
        if tcenter[0] == 0 and tcenter[1] == 0:
            pass
        else:
            icenter = (img.shape[1] // 2, img.shape[0] // 2)
            dx = tcenter[0] - icenter[0]
            dy = tcenter[1] - icenter[1]
            if abs(dx) <= 2 and abs(dy) <= 2:
                new_ammo = img[660:690, 480:520]
                a = scn.match_img_ltrb(ammo, new_ammo, 0.9)[0]
                if a != -1:
                    self.lock_on = True
                    self.fire()
                pass
            else:
                out_x = -round(PID_mouse_x(dx))
                out_y = -round(PID_mouse_y(dy))
                ctypes.windll.user32.mouse_event(0x0001, out_x, out_y, 0, 0)
            self.lock = False
            self.lock_on = False

    def serach(self):
        player, _, enemy = map.get_point()
        player = player[0]
        d_player = math.atan2(player[2], -player[3])
        d_player = math.degrees(d_player)
        if d_player < 0:
            d_player += 360
        if d_player > 360:
            d_player -= 360
        self.set_zoom(1)
        pos_p = player[0], player[1]
        target = self.get_target(pos_p, enemy)
        if target is None:
            return None
        vect_line = (target[0] - pos_p[0], target[1] - pos_p[1])
        tdeg = math.degrees(math.atan2(vect_line[0], -vect_line[1]))
        if tdeg < 0:
            tdeg += 360
        if tdeg > 360:
            tdeg -= 360
        tower_deg = deg_cal.get_deg()
        try:
            now_deg = d_player + tower_deg
        except:
            now_deg = d_player
        # if tdeg > 180:
        #     tdeg -= 360
        # delta = now_deg - tdeg
        #
        # TODO: 临时修改
        ############################
        # diff = (tdeg - now_deg) % 360
        # print(diff)
        # if diff > 180:
        #     delta = diff - 360
        # else:
        #     delta = diff
        # # if abs(delta) < 20:
        # #     keyboard.press('capslock')
        # #     keyboard.press('x')
        # # keyboard.press('x')
        # # ctypes 按下x
        # ctypes.windll.user32.keybd_event(0x58, 0, 0, 0)
        # # else:
        # try:
        #     output = int(PID_mouse_x(delta))
        # except ValueError:
        #     output = 0
        ################################

        PID_mouse_x.setpoint = tdeg
        delta = now_deg - tdeg
        if abs(delta) < 30:
            ctypes.windll.user32.keybd_event(0x58, 0, 0, 0)
        try:
            output = int(PID_mouse_x(now_deg))
        except ValueError:
            output = 0

        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_MOVE, output, 0, 0, 0)
        # time.sleep(0.03)
        return target

    def get_target(self, player, enemy_list):
        p_ex = player[0] * 1000, player[1] * 1000
        dis_list = []
        for enemy in enemy_list:
            e_ex = enemy[0] * 1000, enemy[1] * 1000
            distance = math.sqrt((p_ex[0] - e_ex[0]) ** 2 + (p_ex[1] - e_ex[1]) ** 2)
            data = {
                'distance': distance,
                'enemy': enemy
            }
            dis_list.append(data)
        dis_list = sorted(dis_list, key=lambda x: x['distance'])
        if len(dis_list) == 0:
            return None
        return dis_list[0]['enemy']

    def fire(self):
        x = random.randint(-10, 10)
        y = random.randint(0, 10)
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.5)
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.lock_on = False


def stop():
    sys.exit(0)


if __name__ == '__main__':
    fire = fire_control()
    keyboard.add_hotkey('F7', stop)
    time.sleep(1)
    while True:
        fire.lock_and_fire()
