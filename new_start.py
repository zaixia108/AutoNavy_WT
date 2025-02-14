import sys

import cv2
import keyboard
import win32api

from pp_onnx import ppocr
import win32gui, win32con
import time
from toolkit import scn
# from toolkit import img_map
from toolkit import MnK
from toolkit import th_pool
from pilot import pathfinder
from firesystem import fire_control

screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)

print('当前屏幕分辨率为：', screen_width, screen_height)

Ocr = ppocr.ppocr(use_angle_cls=True, use_gpu=True, lang='ch')



def active_window():
    global activate_error
    try:
        hwnd = win32gui.FindWindow('DagorWClass', None)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.5)
    except:
        activate_error += 1
        if activate_error > 5:
            raise Exception('activate_error')
        active_window()


M = MnK.Mouse()
K = MnK.Keyboard()
D = scn.D
time.sleep(1)

submit = th_pool.thread_control.submit

class OcrInGame:
    def __init__(self):
        self.death = False
        self.ocr = Ocr
        self.PATH_FCS_RUNNING = False
        self.rect = win32gui.GetWindowRect(win32gui.FindWindow('DagorWClass', None))
        if self.rect[0] != 0 or self.rect[1] != 0:
            self.rect = (self.rect[0] + 3, self.rect[1] + 32, self.rect[2] - 3, self.rect[3] - 3)

        self.click_words = ['加入战斗', '确认', '领取奖励', '完成', '前往基地', '分配研发', '领取', '否', '返回基地', '使用']

    def start(self):
        global thread_pathfinding, thread_firecontrol
        flag = True
        while flag:
            if self.death:
                self.click_words.remove('加入战斗')
            img = D.now_img
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            result = self.ocr.ocr(img)
            result = result[0]
            print(result)
            for item in result:
                box, text_so = item
                text, score = text_so
                for word in self.click_words:
                    if word in text:
                        x, y = self.postrans(box[0])
                        M.moveto(x, y)
                        M.click()
                        if '基地' in text and '商店' in text:
                            flag = False
                            break
                            # K.press('left')
                            # time.sleep(0.5)
                            # K.press('enter')
                        elif '加入' in text:
                            try:
                                thread_pathfinding.stop()
                                thread_firecontrol.stop()
                            except:
                                pass
                            self.PATH_FCS_RUNNING = False
                            break
                if '被摧毁' in text:
                    if '前进' in text or '后退' in text:
                        pass
                    else:
                        try:
                            thread_pathfinding.stop()
                            thread_firecontrol.stop()
                        except:
                            pass
                        self.PATH_FCS_RUNNING = False
                        self.death = True
                if '研发' in text and '分配' not in text and '载具' not in text:
                    x, y = self.postrans(box[0])
                    M.moveto(x, y)
                    M.click()
                if '前进' in text or 'km' in text:
                    if not self.PATH_FCS_RUNNING:
                        time.sleep(5)
                        print('start pathfinding')
                        print('start fire control system')
                        self.PATH_FCS_RUNNING = True
                        thread_pathfinding = submit(pathfinder, 'pathfinder', True, auto=True, )  # TODO: 填写路径参数
                        # TODO: 初始化炮塔转向
                        FCS = fire_control()
                        thread_firecontrol = submit(FCS.lock_and_fire, 'fire_control', True)
            # if self.death:
            #     K.press('esc')
            time.sleep(3)

    def postrans(self, point):
        x, y = point
        x = int(x + self.rect[0])
        y = int(y + self.rect[1])
        return x, y

    def stop(self, exit=False):
        global thread_pathfinding, thread_firecontrolxx
        self.PATH_FCS_RUNNING = False
        thread_pathfinding.stop()
        thread_firecontrol.stop()
        print('stop')
        if exit:
            sys.exit(0)



if __name__ == '__main__':
    time.sleep(3)
    g = OcrInGame()
    keyboard.add_hotkey('ctrl+q', lambda: g.stop(exit=True))
    while True:
        active_window()
        g.start()
        time.sleep(30)
