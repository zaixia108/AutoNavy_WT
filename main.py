import os.path
import time

import cv2
import keyboard

from toolkit import scn
from toolkit import img_map
from toolkit import MnK
from toolkit import th_pool

from pilot import pathfinder
from firesystem import fire_control

D = scn.D
# step1: 开始游戏
M = MnK.Mouse()
K = MnK.Keyboard()
once = th_pool.thread_control.once
submit = th_pool.thread_control.submit

thread_pathfinding = 'thread for JPS pathfinding'
thread_firecontrol = 'thread for fire control system'

money = False

SLEEP_TIME = 20


def start():
    while True:
        waiting = scn.match_img(D.now_img, img_map.waiting, 0.8)[0]
        if waiting == -1:
            start = scn.match_img(D.now_img, img_map.start, 0.8)[0]
            if start != -1:
                M.moveto(start[0], start[1])
                M.click()
                time.sleep(0.5)
                continue
            # else:
            #     K.press('esc')
            #     time.sleep(0.5)
            #     continue
        else:
            time.sleep(1)
        # cv2.imshow('waiting', D.now_img)
        # cv2.imshow('start', img_map.join_game)
        # cv2.waitKey(1000)
        p, v = scn.match_img(D.now_img, img_map.join_game, 0.8)
        if p != -1:
            break
        K.press('esc')
        print('waiting for join game')
        continue
    print('join game')
    while True:
        img = D.now_img
        # p, v = scn.match_img(img, img_map.join_game, 0.8)
        # if p != -1:
        #     time.sleep(SLEEP_TIME)
        #     M.moveto(p[0], p[1])
        #     M.click()
        #     break
        # else:
        time.sleep(1)
        K.press('enter')
        p, v = scn.match_img(img, img_map.confirm1, 0.8)
        if p != -1:
            M.moveto(p[0], p[1])

            M.click()
        p, v = scn.match_img(img, img_map.confirm2, 0.8)
        if p != -1:
            M.moveto(p[0], p[1])
            M.click()
        time.sleep(3)
        p, v = scn.match_img(img, img_map.fire, 0.8)
        if p != -1:
            break
        print('waiting for deploy')


def main_running():
    global thread_pathfinding, thread_firecontrol
    # TODO: 等待进入战局
    thread_pathfinding = submit(pathfinder, 'pathfinder', True, auto=True, )  # TODO: 填写路径参数
    # TODO: 初始化炮塔转向
    FCS = fire_control()
    thread_firecontrol = submit(FCS.lock_and_fire, 'fire_control', True)
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


def end():
    global thread_pathfinding, thread_firecontrol
    try:
        thread_pathfinding.stop()
        thread_firecontrol.stop()
    except:
        pass
    while True:
        confirm0 = scn.match_img(D.now_img, img_map.confirm, 0.8)[0]
        if confirm0 != -1:
            M.moveto(confirm0[0], confirm0[1])
            M.click()
        confirm1 = scn.match_img(D.now_img, img_map.confirm1, 0.8)[0]
        if confirm1 != -1:
            M.moveto(confirm1[0], confirm1[1])
            M.click()
        confirm2 = scn.match_img(D.now_img, img_map.confirm2, 0.8)[0]
        if confirm2 != -1:
            M.moveto(confirm2[0], confirm2[1])
            M.click()
        improvement = scn.match_img(D.now_img, img_map.improvement, 0.8)[0]
        if improvement != -1:
            M.moveto(improvement[0], improvement[1])
            M.click()
        improvement_ = scn.match_img(D.now_img, img_map.improvement_, 0.8)[0]
        if improvement_ != -1:
            M.moveto(improvement_[0], improvement_[1])
            M.click()
        _purchase = scn.match_img(D.now_img, img_map._purchase, 0.8)[0]
        if _purchase != -1:
            if money:
                K.press('esc')
            else:
                M.moveto(_purchase[0], _purchase[1])
                M.click()
        purchase_confirm = scn.match_img(D.now_img, img_map.purchase_confirm, 0.8)[0]
        if purchase_confirm != -1:
            M.moveto(purchase_confirm[0], purchase_confirm[1])
            M.click()
        crew_cancel = scn.match_img(D.now_img, img_map.crew_cancel, 0.8)[0]
        if crew_cancel != -1:
            M.moveto(crew_cancel[0], crew_cancel[1])
            M.click()
        rtlg_no = scn.match_img(D.now_img, img_map.rtlg_no, 0.8)[0]
        if rtlg_no != -1:
            M.moveto(rtlg_no[0], rtlg_no[1])
            M.click()
        research = scn.match_img(D.now_img, img_map.research, 0.8)[0]
        if research != -1:
            research1 = scn.match_img(D.now_img, img_map.research1, 0.8)[0]
            if research1 != -1:
                M.moveto(research1[0], research1[1])
                M.click()
        close = scn.match_img(D.now_img, img_map.close, 0.8)[0]
        if close != -1:
            M.moveto(close[0], close[1])
            M.click()
        box = scn.match_img(D.now_img, img_map.box, 0.8)[0]
        if box != -1:
            M.moveto(box[0], box[1])
            M.click()
        K.press('esc')
        menu = scn.match_img(D.now_img, img_map.start, 0.8)[0]
        if menu != -1:
            break


if __name__ == '__main__':
    if os.path.exists('skip1'):
        pass
    else:
        time.sleep(3)
        start()
    if os.path.exists('skip2'):
        pass
    else:
        time.sleep(1)
        main_running()
    if os.path.exists('skip3'):
        pass
    else:
        time.sleep(1)
        end()
