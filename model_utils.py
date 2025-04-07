import threading
import datetime
import time

import cv2

from database.db_manager import DBManager


def resize_pos(x1, y1, src_size, tar_size):
    w1 = src_size[0]
    h1 = src_size[1]
    w2 = tar_size[0]
    h2 = tar_size[1]
    y2 = (h2 / h1) * y1
    x2 = (w2 / w1) * x1
    return int(x2), int(y2)


def convert_coordinates(xmin, ymin, xmax, ymax):
    x = xmin
    y = ymin
    width = xmax - xmin
    height = ymax - ymin
    return x, y, width, height


class Colors:
    def __init__(self):
        color_hex = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                     '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb('#' + c) for c in color_hex]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))


def plot_one_box(x, im, color=(128, 128, 128), label=None, line_thickness=3):
    tl = line_thickness or round(0.002 * (im.shape[0] + im.shape[1]) / 2) + 1  # line/font thickness
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(im, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(im, c1, c2, color, -1, cv2.LINE_AA)
        cv2.putText(im, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    return im


class FaceTracker(object):
    def __init__(self):
        self.names = []
        self.trackers = []
        self.boxes = []

    def create_tracker(self, frame, name, box):
        tracker = cv2.legacy.MultiTracker.create()
        tracker.add(cv2.legacy.TrackerKCF.create(), frame, box)
        self.names.append(name)
        self.boxes.append(box)
        self.trackers.append(tracker)

    def update(self, frame):
        pre_boxes = self.boxes.copy()
        boxes = []

        for index in range(len(self.trackers)):
            tracker = self.trackers[index]
            success, box = tracker.update(frame)
            if success:
                boxes.append(box)
            else:
                pre_box = convert_coordinates(*pre_boxes[index])
                boxes.append([pre_box])
                self.tracker_keep(frame, index, pre_box)

        self.boxes = []
        for box in boxes:
            newbox = box[0]
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            self.boxes.append(p1 + p2)

            # cv2.rectangle(frame, p1, p2, (200, 0, 0), thickness=3)
        return frame

    def tracker_keep(self, frame, index, box):
        tracker = cv2.legacy.MultiTracker.create()
        tracker.add(cv2.legacy.TrackerKCF.create(), frame, box)
        self.trackers[index] = tracker


class ActionManager(threading.Thread):
    def __init__(self, action_queue, manager_thread_lock):
        super(ActionManager, self).__init__()
        self.action_store = []
        self.video_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.action_queue = action_queue
        self.manager_thread_lock = manager_thread_lock
        self.thread_exit = False
        self.db = DBManager()

    def save(self, action):
        action.date = self.video_time
        self.action_store.append([
            action.name,
            action.class_id,
            action.date,
            action.action_type,
            action.timestamp,
            action.xmin,
            action.ymin,
            action.xmax,
            action.ymax,
        ])

    def db_save(self):
        self.db.insert_action(self.action_store)

    def exit(self, camera_id, duration):
        self.db.insert_class(camera_id, self.video_time, duration)
        with self.manager_thread_lock:
            self.thread_exit = True

    def run(self):
        while True:
            action = None
            with self.manager_thread_lock:
                if self.thread_exit and not self.action_queue:
                    break
                if self.action_queue:
                    action = self.action_queue.pop()
            if action:
                self.save(action)
            else:
                time.sleep(1)
        self.db_save()
