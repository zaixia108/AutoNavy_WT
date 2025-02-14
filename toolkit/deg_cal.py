import ctypes
import math
import time

import cv2
import numpy as np
import dxcam
import win32gui
from toolkit import scn



D = scn.D


def get_deg():
    try:
        # 加载图像
        image = D.get_latest_frame()
        image = image[545:615, 85:145]
        # cv2.imshow('Result', image)
        # cv2.waitKey(1)
        # continue

        # 转换为 HSV 颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 定义颜色范围
        lower_color = np.array([35, 43, 46])
        upper_color = np.array([77, 255, 255])

        center = (image.shape[1] // 2, image.shape[0] // 2)
        # print("center:", center)

        """
        可以筛选炮塔的淡绿色
        lower_color = np.array([60, 100, 50])
        upper_color = np.array([80, 255, 255])
        """

        # 创建掩码
        mask = cv2.inRange(hsv, lower_color, upper_color)

        # 应用形态学操作
        kernel = np.ones((1, 1), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # 提取瞄准线
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 绘制瞄准线
        for contour in contours:
            cv2.drawContours(image, [contour], -1, (0, 0, 255), 1)

        # 找到最大的contour
        max_contour = max(contours, key=cv2.contourArea)
        num = 1
        for i in range(1, 10):
            approx = cv2.approxPolyDP(max_contour, cv2.arcLength(max_contour, True) * (num - i / 10), True)
            # print("近似的顶点数:", len(approx))
            # 计算与 y 轴的夹角
            point_list = []
            if len(approx) == 3:
                # 找出离中心点最近的一个顶点
                min_distance = 999999
                for v in approx:
                    point_list.append((v[0][0], v[0][1]))
                    distance = np.sqrt((v[0][0] - center[0]) ** 2 + (v[0][1] - center[1]) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        vc = (v[0][0], v[0][1])
                point_list.remove(vc)

                # TODO: 测试偏差
                vc = (center[0], vc[1])

                v1 = point_list[0]
                v2 = point_list[1]
                # 另外两个点计算中点
                ct = ((v1[0] + v2[0]) // 2, (v1[1] + v2[1]) // 2)



                ax_y = [center[0], 0]
                # 计算 线段 ax_y vc 和 ct vc 的夹角
                vect_y = [ax_y[0] - vc[0], ax_y[1] - vc[1]]
                vect_ct = [ct[0] - vc[0], ct[1] - vc[1]]
                # 计算两个向量的角度
                # angle_radians = np.arccos(np.dot(vect_y, vect_ct) / (np.linalg.norm(vect_y) * np.linalg.norm(vect_ct)))
                # angle_degrees = np.degrees(angle_radians)
                # return angle_degrees
                angle_radians = math.atan2(vect_ct[1], vect_ct[0])
                angle_degrees = math.degrees(angle_radians) + 90
                if angle_degrees < 0:
                    angle_degrees += 360
                if angle_degrees > 360:
                    angle_degrees -= 360
                if angle_degrees > 180:
                    angle_degrees -= 360
                return angle_degrees
                # print(f"角度: {angle_degrees:.2f}")
                # cv2.line(image, vc, ct, (255, 255, 0), 2)
                # cv2.imshow('Result', image)
                # cv2.waitKey(1)
                # cv2.destroyAllWindows()
        for i in range(1, 10):
            approx = cv2.approxPolyDP(max_contour, cv2.arcLength(max_contour, True) * (num - i / 10), True)
            # print("近似的顶点数:", len(approx))
            # 计算与 y 轴的夹角
            point_list = []
            if len(approx) == 2:
                min_distance = 999999
                for v in approx:
                    point_list.append((v[0][0], v[0][1]))
                    distance = np.sqrt((v[0][0] - center[0]) ** 2 + (v[0][1] - center[1]) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        vc = (v[0][0], v[0][1])
                point_list.remove(vc)
                v1 = point_list[0]
                ct = ((v1[0] + vc[0]) // 2, (v1[1] + vc[1]) // 2)
                ic = (center[0], center[1]+10)

                # cv2.line(image, ic, ct, (0, 255, 255), 2)

                ax_y = [center[0], 0]
                # 计算 线段 ax_y vc 和 ct vc 的夹角
                vect_y = [ax_y[0] - vc[0], ax_y[1] - vc[1]]
                vect_ct = [ct[0] - ic[0], ct[1] - ic[1]]
                # 计算两个向量的角度
                angle_radians = math.atan2(vect_ct[1], vect_ct[0])
                angle_degrees = math.degrees(angle_radians) + 90
                if angle_degrees < 0:
                    angle_degrees += 360
                if angle_degrees > 360:
                    angle_degrees -= 360
                if angle_degrees > 180:
                    angle_degrees -= 360
                return angle_degrees
                # print(f"角度: {angle_degrees:.2f}")
                # cv2.imshow('Result', image)
                # cv2.waitKey(1)
    except ValueError:
        return None


if __name__ == '__main__':
    while True:
        t1 = time.time()
        a = get_deg()
        t2 = time.time()
        print(a)
        print(t2 - t1)