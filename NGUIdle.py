from enum import Enum
from enum import auto
import win32gui
# import win32con
# import win32api
import json
from pygame import rect
# mss_import should be imported before pyautogui as it changes the DPI Awareness to something we don't want
from mss_import import sct
import pyautogui
import numpy as np
import util
import re
import logging


def to_rect(current_rect):
    if isinstance(current_rect, tuple):
        return rect.Rect(
            current_rect[0],
            current_rect[1],
            current_rect[2] - current_rect[0],
            current_rect[3] - current_rect[1])
    elif isinstance(current_rect, dict):
        return rect.Rect(
            current_rect['left'],
            current_rect['top'],
            current_rect['width'],
            current_rect['height'])


def to_dict(current_rect: rect.Rect) -> dict:
    return {
        'left': current_rect.left,
        'top':  current_rect.top,
        'width': current_rect.width,
        'height': current_rect.height
    }


class NGUIdle:
    class Menus(Enum):
        BasicTraining = auto()
        FightBoss = auto()
        MoneyPit = auto()
        Adventure = auto()
        Inventory = auto()
        Augmentation = auto()
        AdvTraining = auto()
        TimeMachine = auto()
        BloodMagic = auto()
        Wandoos = auto()
        NGU = auto()
        Yggdrasil = auto()
        GoldDiggers = auto()
        Beards = auto()
        Questing = auto()
        Hacks = auto()
        Wishes = auto()
        Cards = auto()
        Cooking = auto()

    def __init__(self) -> None:
        self.NGUIdle = win32gui.FindWindow(None, "NGU Idle")
        self.window_screen_rect = to_rect(win32gui.GetWindowRect(self.NGUIdle))

        self.client_rect = to_rect(win32gui.GetClientRect(self.NGUIdle))
        top_left = win32gui.ClientToScreen(self.NGUIdle, (self.client_rect.left, self.client_rect.top))
        bottom_right = win32gui.ClientToScreen(self.NGUIdle, (self.client_rect.right, self.client_rect.bottom))
        self.client_area_screen_rect = to_rect(top_left + bottom_right)

        logging.debug(f"window              : {self.window_screen_rect.x}, {self.window_screen_rect.y}, {self.window_screen_rect.width}x{self.window_screen_rect.height}")
        logging.debug(f"client_area         : {self.client_rect.x}, {self.client_rect.y}, {self.client_rect.width}x{self.client_rect.height}")
        logging.debug(f"client_area_screen  : {self.client_area_screen_rect.x}, {self.client_area_screen_rect.y}, {self.client_area_screen_rect.width}x{self.client_area_screen_rect.height}")

        self.previous_mouse_position = None
        self.load_configuration()

        self.cooking = NGUIdle.Cooking(self)

    def load_configuration(self):
        with open("NGUIdle.json") as config_file:
            self.config = json.load(config_file)

    def scale_config(self, config_rect: rect.Rect):
        config_resolution = (
            self.config['General']['Resolution']['width'],
            self.config['General']['Resolution']['height']
        )
        config_rect.update(
            config_rect.left * self.client_rect.width / config_resolution[0],
            config_rect.top * self.client_rect.height / config_resolution[1],
            config_rect.width * self.client_rect.width / config_resolution[0],
            config_rect.height * self.client_rect.height / config_resolution[1],
        )
        return config_rect

    def get_menu_position(self, menu_item: Menus) -> rect.Rect:
        menu_rect = to_rect(self.config['Menus'][menu_item.name])
        menu_rect = self.scale_config(menu_rect)
        return menu_rect

    def set_focus(self):
        win32gui.SetFocus(self.NGUIdle)

    def select_menu(self, menu_item: Menus):
        menu_position = self.get_menu_position(menu_item)
        self.click(menu_position.centerx, menu_position.centery)

    # def click(self, x, y):
    #     # win32gui.SendMessage(self.NGUIdle, win32con.WM_MOUSEACTIVATE, self.NGUIdle, )
    #     win32gui.SendMessage(self.NGUIdle, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x, y))
    #     win32gui.SendMessage(
    #         self.NGUIdle,
    #         win32con.WM_LBUTTONDOWN,
    #         win32con.MK_LBUTTON,
    #         win32api.MAKELONG(x, y))
    #     win32gui.SendMessage(
    #         self.NGUIdle,
    #         win32con.WM_LBUTTONUP,
    #         0,
    #         win32api.MAKELONG(x, y))

    def click(self, x, y, clicks=1):
        x = self.client_area_screen_rect.left + x
        y = self.client_area_screen_rect.top + y
        if self.previous_mouse_position is not None and self.previous_mouse_position != pyautogui.position():
            raise StopIteration("Mouse has moved since last click, we will prevent having to fight over control of the mouse")
        # pyautogui.click(x, y, clicks)     # too fast, clicks do not all register properly
        for i in range(clicks):
            pyautogui.click(x, y)
        self.previous_mouse_position = (x, y)

    def capture_region(self, client_area: rect.Rect) -> np.array:
        top_left = win32gui.ClientToScreen(self.NGUIdle, (client_area.left, client_area.top))
        bottom_right = win32gui.ClientToScreen(self.NGUIdle, (client_area.right, client_area.bottom))
        client_area_screen_rect = to_rect(top_left + bottom_right)
        return np.array(sct.grab(to_dict(client_area_screen_rect)))

    class Cooking:
        def __init__(self, ngu: 'NGUIdle') -> None:
            self.ngu = ngu
            self.grid_x = self.ngu.config['Cooking']["IngredientsGrid"]['grid_x']
            self.grid_y = self.ngu.config['Cooking']["IngredientsGrid"]['grid_y']
            self.nb_value_per_ingredient = self.ngu.config['Cooking']['nb_value_per_ingredient']
            self.nb_ingredients = self.grid_x * self.grid_y
            for i in range(self.nb_ingredients):
                if not self.is_ingredient_valid(i):
                    self.nb_ingredients = i
                    break
            logging.info(f"nb ingredients: {self.nb_ingredients}")
            self.values = np.zeros(self.get_nb_ingredients(), np.int32)

        def index1d(self, index) -> int:
            if np.isscalar(index):
                return index
            return index[1] * self.grid_x + index[0]

        def index2d(self, index) -> tuple[int, int]:
            if np.isscalar(index):
                return ((int)(index % self.grid_x), (int)(index / self.grid_x))
            return index

        def get_nb_ingredients(self) -> int:
            return self.nb_ingredients

        def get_ingredients(self):
            return self.values

        def is_ingredient_valid(self, index) -> bool:
            if index < 6:
                return True

            # screen grab the plus sign and look for the content to identify if the button is there
            plus_rect = self.get_plus_rect(index)
            plus_rect_img = self.ngu.capture_region(plus_rect)
            plus_rect_img = np.reshape(
                plus_rect_img, (plus_rect_img.shape[0] * plus_rect_img.shape[1], plus_rect_img.shape[2]))
            std = np.std(plus_rect_img, axis=0)

            return np.any(std > 0)

        def get_plus_rect(self, index):
            grid = self.ngu.config['Cooking']["IngredientsGrid"]
            index2d = self.index2d(index)
            plus_rect = to_rect(grid['Plus'])
            plus_rect = plus_rect.move(index2d[0] * grid['offset_x'], index2d[1] * grid['offset_y'])
            plus_rect = self.ngu.scale_config(plus_rect)
            return plus_rect

        def get_minus_rect(self, index):
            grid = self.ngu.config['Cooking']["IngredientsGrid"]
            index2d = self.index2d(index)
            minus_rect = to_rect(grid['Minus'])
            minus_rect = minus_rect.move(index2d[0] * grid['offset_x'], index2d[1] * grid['offset_y'])
            minus_rect = self.ngu.scale_config(minus_rect)
            return minus_rect

        def click_plus(self, index, clicks=1):
            plus_rect = self.get_plus_rect(index)
            self.ngu.click(plus_rect.centerx, plus_rect.centery, clicks)

        def click_minus(self, index, clicks=1):
            minus_rect = self.get_minus_rect(index)
            self.ngu.click(minus_rect.centerx, minus_rect.centery, clicks)

        def reset_to_0(self):
            for ingredient in range(self.get_nb_ingredients()):
                self.click_minus(ingredient, self.nb_value_per_ingredient)
            self.values.fill(0)

        def set_all_ingredients_to(self, value):
            for ingredient in range(self.get_nb_ingredients()):
                self.set_ingredient_value(ingredient, value)

        def set_ingredient_value(self, ingredient_index, value):
            value = np.clip(value, 0, self.nb_value_per_ingredient-1)
            ingredient_index = self.index1d(ingredient_index)
            if (self.values[ingredient_index] > value):
                self.click_minus(ingredient_index, self.values[ingredient_index] - value)
            elif (self.values[ingredient_index] < value):
                self.click_plus(ingredient_index, value - self.values[ingredient_index])
            self.values[ingredient_index] = value

        def get_meal_efficiency(self):
            meal_efficiency_rect = self.ngu.scale_config(to_rect(self.ngu.config['Cooking']["MealEfficiency"]))
            meal_efficiency_img = self.ngu.capture_region(meal_efficiency_rect)
            whitelist = "0123456789+,%"
            text = util.to_text(meal_efficiency_img, whitelist=whitelist)
            # Get best result
            text = text.sort_values("conf", ascending=False).iloc[0].text
            try:
                value = self.get_percentage_value(text, guess_errors=False)
            except ValueError:
                value = self.get_percentage_value(text, guess_errors=True)
                logging.warning(f"get_meal_efficiency: {text} is being interpreted as {value}")

            # self.save_meal_efficiency_result(meal_efficiency_img, value)

            if (value > 100):
                breakpoint()
            return value, meal_efficiency_img

        def save_meal_efficiency_result(self, img, value):
            from PIL import Image
            import os
            im = Image.fromarray(img)
            folder = "result"
            if not os.path.exists(folder):
                os.makedirs(folder)
            filename = folder + "/meal_efficiency_" + "_".join(str(x) for x in self.values) + " - " + str(value) + ".png"
            im.save(filename)

        def get_percentage_value(self, text, guess_errors=True):
            text = text.replace(',', '.')   # Replace , decimal with .
            # The number must end with %
            match = re.match(r"\+?((0\.\d+)|([1-9]\d*\.\d*)|([1-9]\d{0,2}))%$", text)    # perfect match
            if match and float(match.group(1)) > 100:
                match = None
            if not match:
                # special case: 100
                match = re.match(r"\+?(100)$", text)
            if not match and guess_errors:
                # The % character  may have been interpreted as 9, 8 or 6 or 0 by the OCR library. we will skip the last digit then
                # match = re.match(r"\+?(\d+\.?\d*)[0689]$", text)
                match = re.match(r"\+?(\d{1,2}\.\d{1,2})\d$", text)
            if not match and guess_errors:
                # Missing the . after 0
                match = re.match(r"\+?0(\d{1,3})%?$", text)
                if match:
                    value = float(match.group(1))
                    value = value / (10**len(match.group(1)))
                    return value
            if not match and guess_errors:
                # Missing the . or %
                match = re.match(r"\+?(\d{1,4})%?$", text)
                if match:
                    value = float(match.group(1))
                    value = value / 100 if value >= 1000 else value / 100
                    return value
            if not match and guess_errors:
                # Missing the %
                match = re.match(r"\+?(\d{1,2}\.\d{1,2})%?$", text)

            if not match:
                raise ValueError(f"Invalid percentage value: {text}")
            text = match.group(1)
            return float(text)
