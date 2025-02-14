import time
import pyvjoy as js

# 轴1 = 滚转
# 轴2 = 俯仰
# 轴3 = 偏航
# 轴4 =
# 轴5 = 油门


# b1 = 襟翼
# b2 = 减速板
# b3 = 起落架
# b4 = 刹车
# b5 = 阻尼器

_max = 32768


class JSK:
    """
    模拟遥杆控制

    操作方法：
    1. 实例化一个Joystick对象
    2. 调用Joystick对象的方法，模拟遥杆控制：
        axis_x(num)：模拟x轴
        axis_y(num)：模拟y轴
        axis_qe(num)：模拟q/e轴
        axis_throttle(num)：模拟油门轴
        button(num, state)：模拟按钮
        button_list：1——襟翼，2——减速板，3——起落架，4——刹车，5——阻尼器
    3. 调用Joystick对象的属性，获取遥杆状态：
        x_axis：x轴状态
        y_axis：y轴状态
        qe_axis：q/e轴状态
        throttle_axis：油门轴状态
        button_list：按钮状态
    4. reset()：重置遥杆状态
    """

    def __init__(self):
        self.button_list = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False,
            7: False,
            8: False,
        }
        self.x_axis = 0
        self.y_axis = 0
        self.qe_axis = 0
        self.throttle_axis = 0

    # 模拟xbox手柄控制
    def axis_x(self, num):
        if abs(num) > 100:
            if num > 0:
                num = 100
            else:
                num = -100
        base = 16384
        change = int(16384 * (num / 100))
        final = base + change
        j = js.VJoyDevice(1)
        j.set_axis(js.HID_USAGE_X, final)

        self.x_axis = final // _max * 100

    def axis_y(self, num):
        if abs(num) > 100:
            if num > 0:
                num = 100
            else:
                num = -100
        base = 16384
        change = int(16384 * (num / 100))
        final = base + change
        j = js.VJoyDevice(1)
        j.set_axis(js.HID_USAGE_Y, final)

        self.y_axis = final // _max * 100

    def axis_qe(self, num):
        if abs(num) > 100:
            if num > 0:
                num = 100
            else:
                num = -100
        base = 16384
        change = int(16384 * (num / 100))
        final = base + change
        j = js.VJoyDevice(1)
        j.set_axis(js.HID_USAGE_Z, final)

        self.qe_axis = final // _max * 100

    def axis_throttle(self, num):
        if num > 100:
            num = 100
        elif num < 0:
            num = 0
        change = int(_max * (num / 100))
        j = js.VJoyDevice(1)
        j.set_axis(js.HID_USAGE_RY, change)

        self.throttle_axis = change // _max * 100

    def press_button(self, button_id):
        j = js.VJoyDevice(1)
        j.set_button(button_id, 1)
        self.button_list[button_id] = True
        time.sleep(0.1)
        j.set_button(button_id, 0)
        self.button_list[button_id] = False

    def button_down(self, button_id):
        j = js.VJoyDevice(1)
        j.set_button(button_id, 1)
        self.button_list[button_id] = True

    def button_up(self, button_id):
        j = js.VJoyDevice(1)
        j.set_button(button_id, 0)
        self.button_list[button_id] = False

    def switch_flap(self, state):
        now_state = self.button_list[1]
        if state != now_state:
            self.press_button(1)

    def switch_airbrake(self, state):
        now_state = self.button_list[1]
        if state != now_state:
            self.press_button(2)

    def switch_gear(self, state):
        now_state = self.button_list[1]
        if state != now_state:
            self.press_button(3)

    def switch_brake(self, state):
        now_state = self.button_list[1]
        if state != now_state and state is True:
            self.button_down(4)
        elif state != now_state and state is False:
            self.button_up(4)
        else:
            pass

    def switch_damper(self, state):  # , num: int = 2):
        now_state = self.button_list[1]
        if state != now_state:
            self.press_button(5)

    def reset(self):
        self.axis_x(0)
        self.axis_y(0)
        self.axis_qe(0)
        self.axis_throttle(0)
        for i in range(1, 9):
            self.button_up(i)
        self.switch_airbrake(False)
        self.switch_brake(False)
        self.switch_damper(False)
        self.switch_flap(False)
        self.switch_gear(False)

if __name__ == '__main__':
    j = JSK()
    j.reset()
    time.sleep(3)
    j.axis_x(100)
    time.sleep(1)
    j.axis_x(-100)
    time.sleep(1)
    j.axis_x(0)
    time.sleep(1)

#     s = sim_Jsk()
#     s.reset()
#     _max = 100
#     s.setup(280, 280)
#     for i in range(5):
#         s.set_pos_percent(0, _max)
#         time.sleep(0.1)
#         s.set_pos_percent(0, -_max)
#         time.sleep(0.1)
#         s.set_pos_percent(_max, 0)
#         time.sleep(0.1)
#         s.set_pos_percent(-_max, 0)
#         time.sleep(0.1)
#     s.reset()

    # time.sleep(3)
    # j.switch_brake(True)
    # time.sleep(1)
    # j.switch_brake(False)
    # pass
