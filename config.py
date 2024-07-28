# -*- coding: UTF-8 -*-
# Author: myhMARS
# @Email: 1533512157@qq.com
# @Time : 2024/5/27 下午8:59
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')


class MysqlConfig:
    def __init__(self):
        self.host: str = CONFIG.get('mysql', 'host')
        self.user: str = CONFIG.get('mysql', 'user')
        self.pwd: str = CONFIG.get('mysql', 'pwd')
        self.db: str = CONFIG.get('mysql', 'db')
        self.port: int = CONFIG.getint('mysql', 'port')


class ModelConfig:
    def __init__(self):
        self.model_path: str = CONFIG.get('model', 'model_path')
        self.iou: float = CONFIG.getfloat('model', 'iou')
        self.conf: float = CONFIG.getfloat('model', 'conf')
