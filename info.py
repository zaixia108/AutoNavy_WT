import requests
import math
url_map_object = "http://127.0.0.1:8111/map_obj.json"
url_map_info = "http://127.0.0.1:8111/map_info.json"


class info:
    def __init__(self):
        self.player = None
        self.mapinfo = None
        self.enemy = []
        self.connected = False

    def update(self):
        try:
            self.map_object = requests.get(url_map_object, timeout=300).json()
            self.map_info = requests.get(url_map_info, timeout=300).json()
            self.connected = self.map_info["valid"]
            print(f'debug  connect {self.connected}')
        except Exception:
            self.connected = False
        self.analyse()

    def analyse(self):
        if not self.connected:
            return
        try:
            self.get_map_info()
        except Exception:
            self.mapinfo = None
        try:
            self.get_player()
        except Exception:
            self.player = None
        try:
            self.get_enemy()
        except Exception:
            self.enemy = []

    def get_player(self):
        for _ in self.map_object:
            if _["icon"] == "Player":
                self.player = {
                    "pos": [_["x"], _["y"]],
                    "dx": _["dx"],
                    "dy": _["dy"],
                }

    def get_map_info(self):
        self.mapinfo = {
            'scale': int(self.map_info['map_max'][0]-self.map_info['map_min'][0]),
            'step': self.map_info['grid_steps'][0],
        }

    def get_enemy(self):
        self.enemy = []
        for _ in self.map_object:
            if _["icon"] == "Ship" and _["color[]"] in [
                [250, 12, 0],
                [240, 12, 0],
            ]:
                data = {
                    "pos": [_["x"], _["y"]],
                    "dis": math.sqrt(
                        ((_["x"] - self.player["pos"][0]) ** 2
                         + (_["y"] - self.player["pos"][1]) ** 2) * self.mapinfo["scale"] ** 2
                    )
                }
                self.enemy.append(data)
        self.enemy = sorted(self.enemy, key=lambda x: x["dis"])
