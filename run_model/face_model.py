import os
import pickle
import time

import cv2
import face_recognition
import numpy as np

SHOW_COST = True


def cost(fun):
    def warpper(*arg, **karg):
        a = time.time()
        res = fun(*arg, **karg)
        if SHOW_COST:
            print(fun.__name__, time.time() - a)
        return res

    return warpper


class FaceRecognition:
    def __init__(self):
        self.face_lib_path = './facelib/pkl'
        self.face_lib_label = []
        self.face_lib_encoding = []
        self.load_face_lib()
        print('facelib init done')

    def save_face(self, image_path, name):
        image = cv2.imread(image_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        with open(f'./facelib/pkl/{os.path.splitext(name)[0]}.pkl', 'wb') as file:
            pickle.dump(face_encoding, file)

    def load_face_lib(self):
        for face_encoding_f in os.listdir(self.face_lib_path):
            with open(f'./facelib/pkl/{os.path.splitext(face_encoding_f)[0]}.pkl', 'rb') as file:
                face_encoding = pickle.load(file)
            self.face_lib_encoding.append(face_encoding)
            self.face_lib_label.append(os.path.splitext(face_encoding_f)[0])

    # @cost
    def get_faces(self, image: np.array) -> list[dict]:
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            return []
        compare_face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
        face_labels = self.get_labels(compare_face_encodings)
        res = []
        for face_location, face_label in zip(face_locations, face_labels):
            tmp = {}
            ymin, xmax, ymax, xmin = face_location
            tmp['ymin'] = ymin
            tmp['xmin'] = xmin
            tmp['ymax'] = ymax
            tmp['xmax'] = xmax
            tmp['name'] = face_label
            res.append(tmp.copy())
        return res

    def get_labels(self, compare_faces_encodings):
        face_label = []
        for compare_face_encoding in compare_faces_encodings:
            match = face_recognition.compare_faces(self.face_lib_encoding, compare_face_encoding, tolerance=0.3)
            if any(match):
                face_label.append(self.face_lib_label[match.index(True)])
        return face_label

# if __name__ == '__main__':
#     obj = FaceRecognition()
#     for img_path in os.listdir('../facelib/img'):
#         obj.save_face(os.path.join('../facelib/img', img_path),img_path)
