import configparser
import threading
import time
from copy import deepcopy

import cv2
import numpy as np
from PIL import ImageGrab

from apis import Api
from model_utils import plot_one_box
from run_model.face_model import FaceRecognition
from export_html_report import generate_html_report

config = configparser.ConfigParser()
config.read("config.ini")
COLORS = {}
for action in config.options("colors"):
    COLORS[action] = eval(config.get("colors", action))

thread_lock_video = threading.Lock()

thread_exit = False

screen = ImageGrab.grab()
SCREEN_SIZE = screen.size


def format_box_location(box):
    """
    :param box: tuple, (xmin,ymin,xmax,ymax)
    :return: tuple, (xmin,ymin,width,height)
    """
    return box[0], box[1], box[2] - box[0], box[3] - box[1]


def calculate_iou(box1, box2):
    iou = 0
    xmin1, ymin1, xmax1, ymax1 = box1
    xmin2, ymin2, xmax2, ymax2 = box2

    # 计算交集的左上角和右下角坐标
    xi1 = max(xmin1, xmin2)
    xi2 = min(xmax1, xmax2)
    yi1 = max(ymin1, ymin2)
    yi2 = min(ymax1, ymax2)

    inter_width = max(0, xi2 - xi1)
    inter_height = max(0, yi2 - yi1)

    union_area = inter_width * inter_height

    area = (xmax2 - xmin2) * (ymax2 - ymin2)
    if area != 0:
        iou = (union_area / area) * 100 if union_area != 0 else 0
    return iou


class Action(object):
    def __init__(self, class_id, action_type, xmin, ymin, xmax, ymax, timestamp):
        self.class_id = class_id
        self.action_type = action_type
        self.date = 0
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.timestamp = timestamp


def find_max_overlap_index(actionbox, boxes):
    index = -1
    max_iou = 60
    ious = []
    box_location = (actionbox['xmin'], actionbox['ymin'], actionbox['xmax'], actionbox['ymax'])
    for i in range(len(boxes)):
        iou = calculate_iou(box_location, boxes[i])
        ious.append(iou)
        if iou > max_iou:
            max_iou = iou
            index = i
    return index


class VideoProcess(threading.Thread):

    def __init__(self, camera_id, video_size):
        super(VideoProcess, self).__init__()
        self.camera_id = camera_id
        self.video_size = video_size
        self.ready = False
        self.face_frame = np.zeros((video_size[0], video_size[1], 3), dtype=np.uint8)
        self.first_frame = np.zeros((video_size[0], video_size[1], 3), dtype=np.uint8)

        self.frame = np.zeros((video_size[0], video_size[1], 3), dtype=np.uint8)
        self.timestamp = 0
        self.daemon = True

    def get_frame(self):
        return deepcopy(self.frame)

    def get_timestamp(self):
        return int(self.timestamp)

    def get_fps(self):
        cap = cv2.VideoCapture(self.camera_id)
        return cap.get(cv2.CAP_PROP_FPS)

    def get_face_frame(self):
        while 1:
            if self.ready:
                return deepcopy(self.face_frame)
            time.sleep(0.1)

    def run(self):
        global thread_exit
        cap = cv2.VideoCapture(self.camera_id)
        print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        ret, frame = cap.read()
        self.face_frame = cv2.resize(frame, self.video_size)
        ret, frame = cap.read()
        self.first_frame = cv2.resize(frame, self.video_size)
        self.ready = True
        while not thread_exit:
            ret, frame = cap.read()
            if ret:
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
                frame = cv2.resize(frame, self.video_size)
                thread_lock_video.acquire()
                self.frame = frame
                self.timestamp = timestamp
                thread_lock_video.release()
            else:
                thread_exit = True
            time.sleep(1 / fps)
        cap.release()


def main():
    global thread_exit
    camera_id = './test_video2.mp4'
    video = cv2.VideoCapture(camera_id)

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_size = (width, height)
    # video_size = (1920, 1080)
    model = Api()
    video_thread = VideoProcess(camera_id, video_size)  # 视频流线程
    video_thread.start()
    while not thread_exit:
        thread_lock_video.acquire()
        frame = video_thread.get_frame()
        timestamp = video_thread.get_timestamp()
        thread_lock_video.release()
        action_boxes = model.process_frame(frame, video_size)

        for action_box in action_boxes:
            action_type = action_box['name']
            action = Action(
                camera_id,
                action_type,
                action_box['xmin'],
                action_box['ymin'],
                action_box['xmax'],
                action_box['ymax'],
                timestamp
            )
            frame = plot_one_box([action.xmin, action.ymin, action.xmax, action.ymax],
                                 frame,
                                 label=f'{action.action_type}',
                                 color=COLORS[action.action_type])
        out_win = "smartclass"
        cv2.namedWindow(out_win, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(out_win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('smartclass', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            thread_exit = True

    cv2.destroyAllWindows()
    video_thread.join()


if __name__ == "__main__":
    main()
