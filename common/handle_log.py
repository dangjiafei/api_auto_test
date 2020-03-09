# 该文件处理Log在控制台和文件的记录

import os
import datetime
import logging
from common.handle_config import conf
from common.handle_path import LOG_DIR


class HandleLog(object):

    @staticmethod
    def create_logger():
        date = datetime.datetime.now().strftime("%m_%d_%H_%M_")
        # 创建收集器，设置收集器的等级
        my_log = logging.getLogger(conf.get("log", "name"))
        my_log.setLevel(conf.get("log", "level"))
        # 创建输出到控制台的渠道，设置等级
        sh = logging.StreamHandler()
        sh.setLevel(conf.get("log", "sh_level"))
        my_log.addHandler(sh)
        # 创建输出到文件的渠道，设置等级
        fh = logging.FileHandler(filename=os.path.join(LOG_DIR, date + "log.log"), encoding="utf-8")
        fh.setLevel(conf.get("log", "fh_level"))
        my_log.addHandler(fh)
        # 设置日志输出格式
        output_format = '%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s: %(message)s'
        fm = logging.Formatter(output_format)
        sh.setFormatter(fm)
        fh.setFormatter(fm)
        return my_log


log = HandleLog.create_logger()
