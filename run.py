import threading
import time
from copy import deepcopy

import cv2
import numpy as np
from PIL import ImageGrab

from model_utils import FaceTracker, resize_pos, plot_one_box
from apis import Api
from run_model.face_model import FaceRecognition

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


class VideoProcess(threading.Thread):

    def __init__(self, camera_id, img_height, img_width):
        super(VideoProcess, self).__init__()
        self.camera_id = camera_id
        self.img_height = img_height
        self.img_width = img_width
        self.ready = False
        self.face_frame = np.zeros((img_height, img_width, 3), dtype=np.uint8)
        self.frame = np.zeros((img_height, img_width, 3), dtype=np.uint8)
        self.daemon = True

    def get_frame(self):
        return deepcopy(self.frame)

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
        self.face_frame = frame
        self.ready = True
        while not thread_exit:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (self.img_width, self.img_height))
                thread_lock_video.acquire()
                self.frame = frame
                thread_lock_video.release()
            else:
                thread_exit = True
            time.sleep(1 / fps)
        cap.release()


# class FaceDetector(multiprocessing.Process):
#     def __init__(self, img_list, locations_list, lock, run_flag):
#         super(FaceDetector, self).__init__()
#         self.model = FaceRecognition()
#         self.img_cache: multiprocessing.Queue = img_list
#         self.locations = locations_list
#         self.lock = lock
#         self.run_flag = run_flag
#         self.y_offset = 160
#
#     def get_locations(self):
#         return self.locations
#
#     def get_center(self, name, update):
#         x, y = self.locations[name]
#         x = x + update[0] / 2
#         y = y + update[1] / 2
#         return int(x), int(y)
#
#     def run(self):
#         while True:
#             if not self.run_flag.value:
#                 break
#             if not self.img_cache.empty():
#                 image = self.img_cache.get()
#                 faces = self.model.get_faces(image)
#                 for face in faces:
#                     self.locations.append(face)
#                 # if faces is not None:
#                 #     for face in faces:
#                 #         center_x = face['xmax']
#                 #         center_y = face['ymax']
#                 #         with self.lock:
#                 #             if self.locations.get(face['name']) is None:
#                 #                 self.locations[face['name']] = (center_x, center_y)
#                 #             else:
#                 #                 self.locations[face['name']] = (center_x, center_y)
#                 #                 # self.locations[face['name']] = self.get_center(face['name'], (center_x, center_y))


def main():
    global thread_exit

    camera_id = './test_video1.mp4'
    img_height = 1920
    img_width = 1080
    model = Api(face=False, action=True)
    video_thread = VideoProcess(camera_id, img_height, img_width)
    # faceDetector = FaceRecognition()
    # faceTracker = FaceTracker()
    video_thread.start()
    # thread_lock_video.acquire()
    # frame = video_thread.get_face_frame()
    # thread_lock_video.release()
    # faces = faceDetector.get_faces(frame)
    # frame = cv2.resize(frame, SCREEN_SIZE)
    # for box in faces:
    #     box['xmin'], box['ymin'] = resize_pos(box['xmin'], box['ymin'], (1920, 1080), SCREEN_SIZE)
    #     box['xmax'], box['ymax'] = resize_pos(box['xmax'], box['ymax'], (1920, 1080), SCREEN_SIZE)
    #     # frame = plot_one_box(
    #     #     [box['xmin'], box['ymin'], box['xmax'], box['ymax']],
    #     #     frame,
    #     #     label=box['name'],
    #     #     color=(255, 0, 0))
    #     box_location = format_box_location((box['xmin'], box['ymin'], box['xmax'], box['ymax']))
    #     faceTracker.create_tracker(frame, box['name'], box_location)
    #
    #     cv2.imshow('face', frame)

    # out_win = 'face'
    # cv2.namedWindow(out_win, cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty(out_win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # cv2.imshow('face', frame)
    # cv2.waitKey(0)
    # manager = multiprocessing.Manager()
    # thread_lock_face = manager.Lock()
    # locations_list = manager.list()
    # detect_face_flag = manager.Value(ctypes.c_bool, True)

    while not thread_exit:
        thread_lock_video.acquire()
        frame = video_thread.get_frame()
        thread_lock_video.release()
        out_win = "smartclass"
        cv2.namedWindow(out_win, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(out_win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        frame = model.process_frame(frame)
        # frame = faceTracker.update(frame)
        # with thread_lock_face:
        #     for bbox in locations_list:
        #         box = bbox.copy()
        #         box['xmin'], box['ymin'] = resize_pos(box['xmin'], box['ymin'], (1920, 1080), SCREEN_SIZE)
        #         box['xmax'], box['ymax'] = resize_pos(box['xmax'], box['ymax'], (1920, 1080), SCREEN_SIZE)
        #         # frame = model_utils.plot_one_box(
        #         #     [box['xmin'], box['ymin'], box['xmax'], box['ymax']],
        #         #     frame,
        #         #     label=box['name'],
        #         #     color=(255, 0, 0))
        #         print(box['xmin'], box['ymin'], (box['xmax'] - box['xmin']), (box['ymax'] - box['ymin']))
        cv2.imshow('smartclass', cv2.resize(frame, (img_height, img_width)))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            thread_exit = True

    cv2.destroyAllWindows()

    # thread_lock_face.acquire()
    # detect_face_flag.value = False
    # thread_lock_face.release()
    video_thread.join()

    # for i in range(len(face_processes)):
    #     if face_processes[i].is_alive():
    #         face_processes[i].terminate()
    # for process in face_processes:
    #     process.join()
    #
    #     print(len(face_processes))

    print('all process done')
    # with thread_lock_face:
    #     print(locations_list)


if __name__ == "__main__":
    main()
