import configparser
import time

import cv2

import model_utils
from run_model.gpu_model import ONNX_Model

config = configparser.ConfigParser()
config.read("config.ini")
IMG_SIZE = config.getint("global", "image_size")
COLORS = {}
for action in config.options("colors"):
    COLORS[action] = eval(config.get("colors", action))

SHOW_COST = False


def cost(fun):
    def warpper(*arg, **karg):
        a = time.time()
        res = fun(*arg, **karg)
        if SHOW_COST:
            print(fun.__name__, time.time() - a)
        return res

    return warpper


class Api:
    def __init__(self):
        self.behavior_detection_model = ONNX_Model()
        print('action init done')

    @cost
    def behavior_detection(self, image):
        results = self.behavior_detection_model.get_label(image)
        return results

    def process_frame(self, frame, video_format):
        action_boxes = self.behavior_detection(cv2.resize(frame, (IMG_SIZE, IMG_SIZE)))
        for box in action_boxes:
            box['xmin'], box['ymin'] = model_utils.resize_pos(box['xmin'], box['ymin'], (640, 640), video_format)
            box['xmax'], box['ymax'] = model_utils.resize_pos(box['xmax'], box['ymax'], (640, 640), video_format)

        return action_boxes


