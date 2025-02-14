import os.path
import time

import cv2
import numpy as np
import win32gui

from toolkit import scn
from toolkit import img_map
from toolkit import MnK
from toolkit import th_pool

from pilot import pathfinder
from firesystem import fire_control

from info import info as inf

D = scn.D
# step1: 开始游戏
M = MnK.Mouse()
K = MnK.Keyboard()
once = th_pool.thread_control.once
submit = th_pool.thread_control.submit

thread_pathfinding = 'thread for JPS pathfinding'
thread_firecontrol = 'thread for fire control system'
thread_carsh = 'thread for crash warning'

lower_red = np.array([0, 43, 46])
upper_red = np.array([10, 255, 255])

info = inf()

money = False

SLEEP_TIME = 20


def activate():
    hwnd = win32gui.FindWindow('DagorWClass', None)
    win32gui.SetForegroundWindow(hwnd)


def end():
    global thread_pathfinding, thread_firecontrol, thread_carsh
    try:
        thread_pathfinding.stop()
    except:
        pass
    try:
        thread_firecontrol.stop()
    except:
        pass
    try:
        thread_carsh.stop()
    except:
        pass
    K.keyup("space")
    info.update()
    if info.connected:
        if scn.match_img(D.now_img, img_map.wtlogo, 0.9)[0] == -1:
            K.press("esc")
        time.sleep(0.1)
        K.press("down")
        time.sleep(0.05)
        K.press("up")
        for i in range(6):
            K.press("down")
            time.sleep(0.05)
        K.press("enter")
        time.sleep(0.1)
        K.press("left")
        time.sleep(0.05)
        K.press("enter")
    print('end')


def quit():
    print('----------------------')
    t1 = time.time()
    while scn.match_img(D.now_img, img_map.start, 0.9)[0] == -1:
        activate()
        if time.time() - t1 >= 120:
            print("如此提示持续出现，建议检查战雷设置是否正确(1280*720，窗口化，放缩倍率100%)。")
            raise Exception("LoopException")
        p, v = scn.match_img(D.now_img, img_map.confirm, 0.95)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        p, v = scn.match_img(D.now_img, img_map.confirm1, 0.95)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        p, v = scn.match_img(D.now_img, img_map.confirm2, 0.95)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        p, v = scn.match_img(D.now_img, img_map.improvement, 0.8)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        p, v = scn.match_img(D.now_img, img_map.improvement_, 0.8)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        p, v = scn.match_img(D.now_img, img_map._purchase, 0.8)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
            p, v = scn.match_img(D.now_img, img_map.purchase_confirm, 0.6)
            if p != -1:
                time.sleep(1.0)
            time.sleep(1)
            p, v = scn.match_img(D.now_img, img_map.crew_cancel, 0.8)
            if p != -1:
                M.moveto(p[0], p[1])
                M.click()
        p, v = scn.match_img(D.now_img, img_map.rtlg_no, 0.8)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        if scn.match_img(D.now_img, img_map.research, 0.7)[0] != -1:
            p, v = scn.match_img(D.now_img, img_map.research1, 0.6)
            if p != -1:
                M.moveto(p[0], p[1])
                M.click()
        K.press("esc")
        print('quit')


def start():
    print('----------------------')
    t1 = time.time()
    activate()
    info.update()
    while True:
        if not info.connected:
            if scn.match_img(D.now_img, img_map.join_game, 0.9)[0] == -1:
                pass
            else:
                break
        else:
            break
        if time.time() - t1 >= 540:
            raise Exception("LoopException")
        p, v = scn.match_img(D.now_img, img_map.start, 0.9)
        if p != -1:
            M.moveto(p[0], p[1])
            M.move(0, 3)
            K.press('enter')
            time.sleep(1)
            p, v = scn.match_img(D.now_img, img_map.confirm1, 0.6)
            if p != -1:
                M.moveto(p[0], p[1])
                M.click()
            p, v = scn.match_img(D.now_img, img_map.confirm2, 0.6)
            if p != -1:
                M.moveto(p[0], p[1])
                M.click()
        else:
            p, v = scn.match_img(D.now_img, img_map.confirm1, 0.6)
            if p != -1:
                M.moveto(p[0], p[1])
                M.click()
            p, v = scn.match_img(D.now_img, img_map.confirm2, 0.6)
            if p != -1:
                M.moveto(p[0], p[1])
                M.click()
        p, v = scn.match_img(D.now_img, img_map.wtlogo, 0.6)
        if p != -1:
            K.press("esc")
        if scn.match_img(D.now_img, img_map.cart, 0.8)[0] == -1:
            K.press('esc')
        info.update()
        time.sleep(0.2)
        print('start')


def join():
    print('----------------------')
    t1 = time.time()
    activate()
    info.update()
    while scn.match_img(D.now_img, img_map.join_game, 0.9)[0] == -1:
        if time.time() - t1 >= 540:
            raise Exception("LoopException")
        p, v = scn.match_img(D.now_img, img_map.confirm1, 0.6)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        p, v = scn.match_img(D.now_img, img_map.confirm2, 0.6)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        info.update()
        if info.connected:
            break
    time.sleep(SLEEP_TIME)
    K.press("enter")
    p, v = scn.match_img(D.now_img, img_map.confirm1, 0.6)
    if p != -1:
        M.moveto(p[0], p[1])
        M.click()
    p, v = scn.match_img(D.now_img, img_map.confirm2, 0.6)
    if p != -1:
        M.moveto(p[0], p[1])
        M.click()
    print('join')


def init():
    t1 = time.time()
    while info.player is None:
        if time.time() - t1 >= 30:
            raise Exception("LoopException")
        info.update()
        time.sleep(1)
    time.sleep(15)
    K.press('s')
    K.press('s')
    K.press('s')


def crash():
    bg = D.now_img
    bg = bg[0: bg.shape[0], bg.shape[1] // 3: bg.shape[1] // 3 * 2]
    hsv = cv2.cvtColor(bg, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_red, upper_red)
    a, b = scn.match_img(img_map.crash_warning, mask, 0.2)
    c, d = scn.match_img_ltrb(img_map.crashed, mask, 0.3)
    if a != -1 or c != -1:
        K.keydown('s')
        time.sleep(3)
        K.keyup('s')
        time.sleep(60)
        K.keydown('w')
        time.sleep(5)
        K.keyup('w')
        K.press('s')
        K.press('s')
        K.press('s')
        time.sleep(10)


def main_running():
    global thread_pathfinding, thread_firecontrol, thread_carsh
    # TODO: 等待进入战局
    thread_pathfinding = submit(pathfinder, 'pathfinder', True, auto=True, )  # TODO: 填写路径参数
    # TODO: 初始化炮塔转向
    FCS = fire_control()
    thread_firecontrol = submit(FCS.lock_and_fire, 'fire_control', True)
    thread_carsh = submit(crash, 'crash', True)
    while True:
        end_pos = scn.match_img(D.now_img, img_map.back, 0.8)[0]
        if end_pos != -1:
            print('back to base')
            M.moveto(end_pos[0], end_pos[1])
            M.click()
            break
        elif scn.match_img(D.now_img, img_map.base, 0.8)[0] != -1:
            print('in base')
            break
        elif scn.match_img(D.now_img, img_map.start, 0.8)[0] != -1:
            if scn.match_img(D.now_img, img_map.cart, 0.8)[0] != -1:
                print('cart')
                break
        elif scn.match_img(D.now_img, img_map.data, 0.7)[0] != -1:
            print('data')
            K.press("esc")
            time.sleep(0.5)
            K.press("down")
            time.sleep(0.1)
            K.press("up")
            for i in range(6):
                K.press("down")
                time.sleep(0.1)
            K.press("enter")
            time.sleep(0.1)
            K.press("left")
            time.sleep(0.1)
            K.press("enter")
            time.sleep(2)
            break
        time.sleep(1)


def main():
    activate()
    while True:
        end()
        quit()
        start()
        join()
        init()
        main_running()


if __name__ == '__main__':
    main()
    # time.sleep(3)
    # main_running()
