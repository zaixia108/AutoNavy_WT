import math
from ctypes import Structure, c_long, c_ulong
import colorsys
from typing import TypeVar, Union, Tuple
import requests

Point = TypeVar('Point', Tuple[int, int], int)
c_group = TypeVar('c_group', Tuple[int, int, int], int)


def rgb_check(group: c_group) -> str:
    hsv = colorsys.rgb_to_hsv(group[0], group[1], group[2])
    hsv = (hsv[0] * 180, hsv[1] * 225, hsv[2] * 225)
    h = hsv[0]
    if 0 <= h <= 10 or 156 <= h <= 180:
        return 'red'
    elif 35 <= h <= 77:
        return 'green'
    elif 100 <= h <= 124:
        return 'blue'


# 下载http://127.0.0.1:8111/map.img?gen=2
# ip = "192.168.31.100"
ip = "127.0.0.1"


def download_map():
    url = f'http://{ip}:8111/map.img?gen=2'
    r = requests.get(url)
    name = 'src/origin_map.png'
    with open(name, 'wb') as f:
        f.write(r.content)
    print('下载完成')
    return_name = 'origin_map.png'
    return return_name


def get_point(onlyplayer=False):
    # try:
    if onlyplayer:
        url = f"http://{ip}:8111/map_obj.json"
        response = requests.get(url).json()
        player = []
        for _ in response:
            if _['icon'] == 'Player':
                x = _['x']
                y = _['y']
                dx = _['dx']
                dy = _['dy']
                player = [x, y]
                d = math.atan2(dx, -dy)
                d = math.degrees(d)
                if d < 0:
                    d += 360
                if d > 360:
                    d -= 360
                # d = math.atan2(dy, dx)
                # d = math.degrees(d)
                # print('人物角度{}'.format(d))
        return player, d
    else:
        url = f"http://{ip}:8111/map_obj.json"
        response = requests.get(url).json()
        player = []
        for _ in response:
            if _['icon'] == 'Player':
                x = _['x']
                y = _['y']
                dx = _['dx']
                dy = _['dy']
                player.append([x, y, dx, dy])
        enemy_list = []
        for _ in response:
            if _['type'] == 'ground_model':
                if rgb_check(_['color[]']) == 'red':
                    x = _['x']
                    y = _['y']
                    enemy_list.append([x, y])
        zone_point = []
        for _ in response:
            if _['icon'] == 'capture_zone':
                if _['color[]'] != [23, 77, 255]:
                    x = _['x']
                    y = _['y']
                    zone_point.append([x, y])
        return player, zone_point, enemy_list


if __name__ == '__main__':
    get_point()
    # download_map()
