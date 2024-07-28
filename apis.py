# NOTE: 准备重构

import configparser
import time

import cv2
from PIL import ImageGrab
from rich.progress import track

import model_utils
from run_model.gpu_model import ONNX_Model
# from run_model.face_model import FaceRecognition
from model_utils import plot_one_box

screen = ImageGrab.grab()
SCREEN_SIZE = screen.size

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
    def __init__(self, face: bool, action: bool):
        self.face = face
        self.action = action
        if action:
            self.behavior_detection_model = ONNX_Model()
            print('action init done')
        # if face:
        #     self.face_model = FaceRecognition()
        # self.localtion_cache = []

    @cost
    def behavior_detection(self, image):
        results = self.behavior_detection_model.get_label(image)
        return results

    # @cost
    # def face_detection(self, image):
    #     results = self.face_model.get_faces(image)
    #     return results

    def process_frame(self, frame):
        action_boxes = []
        # face_boxes = []
        frame = cv2.resize(frame, SCREEN_SIZE)

        if self.action:
            action_boxes = self.behavior_detection(cv2.resize(frame, (640, 640)))
            for box in action_boxes:
                box['xmin'], box['ymin'] = model_utils.resize_pos(box['xmin'], box['ymin'], (640, 640), SCREEN_SIZE)
                box['xmax'], box['ymax'] = model_utils.resize_pos(box['xmax'], box['ymax'], (640, 640), SCREEN_SIZE)
                center = (box['xmin'] + box['ymin']) / 2, (box['xmax'] + box['ymax']) / 2
                detect_img = frame[box['ymin']:box['ymax'], box['xmin']:box['xmax']].copy()

        # if self.face and action_boxes:
        #     face_boxes = []
        #     for box in action_boxes:
        #         detect_img = frame[box['ymin']:box['ymax'], box['xmin']:box['xmax']].copy()
        #         face_box = self.face_detection(detect_img)
        #         for f_box in face_box:
        #             print('action box', box)
        #             print(f_box)
        #             f_box['xmin'] += box['xmin']
        #             f_box['ymin'] += box['ymin']
        #             f_box['xmax'] += box['xmin']
        #             f_box['ymax'] += box['ymin']
        #             face_boxes.append(f_box)

        for action_box in action_boxes:
            frame = plot_one_box([action_box['xmin'], action_box['ymin'], action_box['xmax'], action_box['ymax']],
                                 frame,
                                 label=action_box['name'],
                                 color=COLORS[action_box['name']])
        # for face_box in face_boxes:
        #     frame = plot_one_box([face_box['xmin'], face_box['ymin'], face_box['xmax'], face_box['ymax']],
        #                          frame,
        #                          label=face_box['name'])
        return frame

    # def show_image(self, frame):
    #     frame = cv2.resize(frame, SCREEN_SIZE)
    #     cv2.namedWindow("smartclass_core", cv2.WINDOW_NORMAL)
    #     cv2.setWindowProperty("smartclass_core", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    #     cv2.imshow('smartclass_core', frame)
    #     cv2.waitKey(1)
    #     return frame
    #
    # def use_video_files(self, filepath, show=True, save_path=None):
    #     cap = cv2.VideoCapture(filepath)
    #     width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #     if save_path:
    #         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #         fps = cap.get(cv2.CAP_PROP_FPS)
    #         out = cv2.VideoWriter(save_path, fourcc, fps, SCREEN_SIZE)
    #         print('init')
    #
    #     frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    #
    #     for _ in track(range(int(frame_count))):
    #         ret, frame = cap.read()
    #         if _ % 15 in [i for i in range(5)]:
    #             frame = self.process_frame(frame)
    #         if show:
    #             img = self.show_image(frame)
    #         if save_path:
    #             out.write(img)
    #
    #     cap.release()
    #     if save_path:
    #         out.release()
    #
    #     cap.release()
    #     if save_path:
    #         out.release()
    #
    # def use_video_streaming(self, streampath=0):
    #     cap = cv2.VideoCapture(streampath)
    #     i = 1
    #     while True:
    #         ret, frame = cap.read()
    #         if ret:
    #             if i % 15 in [i for i in range(5)]:
    #                 frame = self.process_frame(frame)
    #             self.show_image(frame)
    #             i += 1
    #         else:
    #             break
    #     cap.release()
