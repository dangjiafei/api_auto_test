# 该文件处理配置文件的读取和写入

import os
from configparser import ConfigParser
from common.handle_path import CONF_DIR


class HandleConfig(ConfigParser):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.read(filename, encoding="utf-8")

    def write_data(self, section, options, value):
        """写入数据的方法"""
        self.set(section, options, value)
        self.write(fp=open(self.filename, "w"))


conf = HandleConfig(os.path.join(CONF_DIR, "config.ini"))
