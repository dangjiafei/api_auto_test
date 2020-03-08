# 该文件处理Excel中测试用例参数化的替换

import re
from common.handle_config import conf


class CaseData:
    """这个类专门用来保存，执行项目过程中提取出来给其他用例用的数据"""
    pass


def replace_data(data):
    """
    :param data: 该参数为Excel里面读取出来的data值
    :return:
    """
    rule = r"#(.+?)#"
    # 根据是否匹配到要替换的数据，来决定要不要进入循环
    while re.search(rule, data):
        # 匹配一个需要替换的内容
        res = re.search(rule, data)
        # 获取需要替换的字段
        key = res.group(1)
        try:
            value = conf.get("test_data", key)
        except Exception:
            value = str(getattr(CaseData, key))
        finally:
            data = re.sub(rule, value, data, 1)
    return data


def replace_data_2(excel_data):
    """
    :param excel_data: 该参数为Excel里面读取出来的data值
    :return:
    """
    rule = r"#(.+?)#"
    # 根据是否匹配到要替换的数据，来决定要不要进入循环
    while re.search(rule, excel_data):
        # 匹配一个需要替换的内容
        res = re.search(rule, excel_data)
        data = res.group()
        # 获取需要替换的字段
        key = res.group(1)
        try:
            excel_data = excel_data.replace(data, conf.get("test_data", key))
        except Exception:
            excel_data = excel_data.replace(data, str(getattr(CaseData, key)))
    return excel_data
