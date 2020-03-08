# -*- coding: utf-8 -*-
# @Time     : 2020/3/5 13:42
# @Author   : Dang_Jiafei
# @Email    : 18840341320@163.com


import os
import unittest
import jsonpath
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from common.handle_request import SendRequest
from common.handle_log import log
from common.handle_replace_data import CaseData, replace_data

case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestInfo(unittest.TestCase):
    excel = ReadExcel(case_file, "info")
    cases = excel.read_data()
    request = SendRequest()

    @classmethod
    def setUpClass(cls):
        # 准备登录的数据
        url = conf.get("item_env", "url") + "/member/login"
        test_data = {
            "mobile_phone": conf.get("test_data", "phone"),
            "pwd": conf.get("test_data", "pwd")
        }
        headers = eval(conf.get("item_env", "headers_v2"))
        # 发送请求，进行登录
        response = cls.request.send(url=url, method="post", json=test_data, headers=headers)
        res = response.json()
        # 提取token,保存为类属性
        token = jsonpath.jsonpath(res, "$..token")[0]
        token_type = jsonpath.jsonpath(res, "$..token_type")[0]
        # 将提取到的token设为类属性
        CaseData.token_value = token_type + " " + token
        # 提取用户的id保存为类属性
        CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])

    @data(*cases)
    def test_info(self, case):
        # 准备用例数据
        url = conf.get("item_env", "url") + replace_data(case["url"])
        method = case["method"]

        headers = eval(conf.get("item_env", "headers_v2"))
        # 在请求头中加入setUpClass中提取出来的token
        headers["Authorization"] = getattr(CaseData, "token_value")

        expected = eval(case["expected"])
        row = case["case_id"] + 1

        response = self.request.send(url=url, method=method, headers=headers)
        res = response.json()

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
        except AssertionError as e:
            print("预期结果：", expected)
            print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例:{}, 执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例:{}, 执行通过".format(case["title"]))
