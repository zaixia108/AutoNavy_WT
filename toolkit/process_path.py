import json
import os
import random
import cv2
from toolkit.way_search import Jps, MapGrid, Point
import numpy as np
import time

import matplotlib.pyplot as plt

from scipy.spatial import KDTree


def get_next_point(path, point):
    # 生成树
    if path is None:
        return None
    if point not in path:
        path.append(point)
    tree = KDTree(np.array(path))
    check_point = point
    for i in range(1, 10):
        try:
            distances, indices = tree.query(check_point, k=11-i)
            ret = path[indices[10-i]]
            break
        except:
            continue

    return ret


def process_img(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (70, 23, 27), (134, 255, 255))
    mask = cv2.bitwise_not(mask)
    img = cv2.bitwise_and(img, img, mask=mask)
    ret, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV)
    binary = cv2.resize(binary, (0, 0), fx=0.25, fy=0.25)
    binary = np.array(binary)
    binary = cv2.bitwise_not(binary)
    size = binary.shape[0]
    scale = 128 / size
    binary = cv2.resize(binary, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    # 膨胀
    kernel = np.ones((5, 5), np.uint8)
    binary = cv2.dilate(binary, kernel)
    # 保存图片
    binary = cv2.bitwise_not(binary)
    return binary


def pathfinding(original_img, show_img=False, start_point=None, end_point=None, human=False):
    img = process_img(original_img)
    # img = original_img
    size = np.shape(img)
    height = size[0]
    width = size[1]
    print("height: %d, width: %d" % (height, width))
    show_image = cv2.resize(original_img, (height, width))

    map = MapGrid(height, width)
    for h in range(height):
        for w in range(width):
            if (img[h, w] == (0, 0, 0)).all():
                map.set_grid(w, h, "obstacle")
    if start_point is None and end_point is None and not human:
        start_point = Point(random.randint(0, width - 1), random.randint(0, height - 1))
        end_point = Point(random.randint(0, width - 1), random.randint(0, height - 1))
    elif human:
        # plt选地点
        plt.imshow(show_image)
        plt.axis('off')
        if start_point:
            start_point = Point(int(start_point[0]), int(start_point[1]))
        else:
            print("Please click the start point")
            # 点击获取坐标
            start_point = plt.ginput(1)
            print(start_point)
            start_point = Point(int(start_point[0][0]), int(start_point[0][1]))
        print("Please click the end point")
        end_point = plt.ginput(1)
        print(end_point)
        end_point = Point(int(end_point[0][0]), int(end_point[0][1]))
    else:
        start_point = Point(start_point[0], start_point[1])
        end_point = Point(end_point[0], end_point[1])

    map.set_grid(start_point.x, start_point.y, "origin")
    map.set_grid(end_point.x, end_point.y, "goal")
    t1 = time.time()
    solver = Jps(start_point, end_point, map)
    # 求解路径
    explored, path, jump = solver.Process()
    if not path:
        print('No path found')
        return None
    path = [(int(p[0]), int(p[1])) for p in path]
    jump = [(int(j[0]), int(j[1])) for j in jump]
    all_path = []
    for i in range(len(path)):
        all_path.append(path[i])
    for i in range(len(jump)):
        all_path.append(jump[i])
    all_path = list(set(all_path))

    t2 = time.time()
    time_ms = int((t2 - t1) * 1000)
    print("Time: %d ms" % time_ms)
    if show_img:
        for i in range(len(all_path)):
            show_image[all_path[i][1], all_path[i][0]] = [0, 0, 255]
            cv2.circle(show_image, (start_point.x, start_point.y), 1, (0, 255, 255), -1)
            cv2.circle(show_image, (end_point.x, end_point.y), 1, (255, 255, 0), -1)
        show_image = cv2.resize(show_image, (512, 512), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("show_image", show_image)
        cv2.waitKey(1)
    with open('../path.json', 'w') as f:
        data = {
            'start_point': [start_point.x, start_point.y],
            'end_point': [end_point.x, end_point.y],
            'path': all_path
        }
        json.dump(data, f, indent=4)
    return all_path


if __name__ == '__main__':
    import map

    pos, deg = map.get_point(onlyplayer=True)
    pos = (int(pos[0] * 128), int(pos[1] * 128))
    img = cv2.imread('temp/origin_map/origin_map.png')
    a = pathfinding(img, show_img=True, human=True, start_point=pos)
    b = get_next_point(a, pos)
    print(b)
    cv2.destroyAllWindows()
