# 该文件处理生成的Log和Report文件过多的情况

import os
from common.handle_path import LOG_DIR, REPORT_DIR


def get_file_list(log_file_path, report_file_path):
    """
    使用lambda表达式, 将文件按照最后修改时间顺序升序排列
    os.path.getmtime() 函数是获取文件最后修改时间
    os.path.getctime() 函数是获取文件最后创建时间
    :param log_file_path: log文件目录路径
    :param report_file_path: report文件目录路径
    :return:
    """
    try:
        # 获取Log和Report文件的路径
        log_dir_list = os.listdir(log_file_path)
        report_dir_list = os.listdir(report_file_path)
        if log_dir_list:
            # 判断目录路径下的文件数量是否超过10个, 可以自定义(根据项目情况)
            if len(log_dir_list) > 10:
                # 使用lambda表达式, 将文件按照最后修改时间顺序升序排列
                log_dir_list = sorted(log_dir_list, key=lambda x: os.path.getmtime(os.path.join(log_file_path, x)))
                report_dir_list = sorted(report_dir_list,
                                         key=lambda x: os.path.getmtime(os.path.join(report_file_path, x)))
                # 获取路径下最早的一个文件并删除
                os.remove(os.path.join(LOG_DIR, log_dir_list[0]))
                os.remove(os.path.join(REPORT_DIR, report_dir_list[0]))
    except Exception as e:
        print("文件路径不存在, 请检查路径是否正确")
