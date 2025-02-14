import json
import math
import random
import time

import cv2

from toolkit.map import get_point, download_map
from toolkit.process_path import pathfinding, get_next_point
from toolkit.joystick import JSK
from toolkit.MnK import Mouse, Keyboard

import simple_pid

mouse = Mouse()
keyboard = Keyboard()

PID_X = simple_pid.PID(0.5, 0.1, 0.1, setpoint=0)
PID_X.output_limits = (-100, 100)


PID_mouse = simple_pid.PID(3, 1, 1, setpoint=0)
PID_mouse.output_limits = (-50, 50)


# TODO: 考虑根据速度输入pid，获取输出的预测距离点，速度计算采用初始位置和当前位置的距离差，以及时间差
TRY_TIMES = 0

j = JSK()
j.reset()


def pathfinder(auto=False):
    # print(f"auto: {auto}")
    global TRY_TIMES
    # Step 1: Get the player's position
    # pos, deg = get_point(onlyplayer=True)
    pos, zone_list, enemy_list = get_point()
    pos = (int(pos[0][0] * 128), int(pos[0][1] * 128))
    download_map()
    # Step 2: Get the path
    img = cv2.imread('src/origin_map.png')
    if auto:
        final_pos = random.choice(zone_list)
        # print(f"Final Pos: {final_pos}")
        final_pos = (int(final_pos[0] * 128), int(final_pos[1] * 128))
        path = pathfinding(img, show_img=False, start_point=pos, end_point=final_pos)
        if path is None:
            TRY_TIMES += 1
            time.sleep(1)
            if TRY_TIMES > 15:
                # print('Cannot find the path')
                # TODO: 重新获取路径，或任意选择一个可以行进的目标点
                return None
            pathfinder(auto=True)
    else:
        path = pathfinding(img, show_img=True, human=True, start_point=pos)
    # Step 3: Get the next point
    i = 0
    while True:
        t1 = time.time()
        i += 1
        pos, deg = get_point(onlyplayer=True)
        opos = pos
        pos = (int(pos[0] * 128), int(pos[1] * 128))
        if i % 300 == 0:
            # print('Getting new path')
            with open('path.json', 'r') as f:
                data = json.load(f)
                end_point = data['end_point']
            path = pathfinding(img, show_img=True, start_point=pos, end_point=end_point)
        next_point = get_next_point(path, pos)
        if next_point is None:
            # print('FINISHED')
            break
        line = (pos, next_point)
        vec_line = (line[1][0] - line[0][0], line[1][1] - line[0][1])
        tdeg = math.degrees(math.atan2(vec_line[0], -vec_line[1]))
        if tdeg < 0:
            tdeg += 360
        if tdeg > 360:
            tdeg -= 360
        # TODO: new change
        # diff = (tdeg - deg) % 360
        # if diff > 180:
        #     delta = diff - 360
        # else:
        #     delta = diff

        ###########################
        # if abs(delta) < 8:
        #     j.reset()
        # else:
        #     if abs(delta) > 170:
        #         f = -1 if delta > 0 else 1
        #         j.axis_x(100*f)
        #     else:
        #         output = -PID_X(delta)
        #         j.axis_qe(output)
        #         print(f"Output: {output}")

        #TODO: better change
        PID_X.setpoint = tdeg
        output = -PID_X(deg)
        j.axis_qe(output)

        while time.time() - t1 < 0.09:
            time.sleep(0.01)
        # t2 = time.time()
        # dt = t2 - t1
        # npos= get_point(onlyplayer=True)[0]
        # opos = (int(opos[0] * 100), int(opos[1] * 100))
        # npos = (int(npos[0] * 100), int(npos[1] * 100))
        # delta = math.sqrt((npos[0] - opos[0]) ** 2 + (npos[1] - opos[1]) ** 2)/dt


if __name__ == '__main__':
    pathfinder()