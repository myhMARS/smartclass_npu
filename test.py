# -*- coding: UTF-8 -*-
# Author: myhMARS
# @Email: 1533512157@qq.com
# @Time : 2024/6/9 下午7:42
from multiprocessing import Process, Manager

def worker_func(shared_dict, key, value):
    shared_dict[key] = value

if __name__ == "__main__":
    manager = Manager()
    shared_dict = manager.dict()

    processes = []
    for i in range(50):
        p = Process(target=worker_func, args=(shared_dict, i, f"value_{i}"))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("Shared dictionary after all processes completed:", shared_dict)
