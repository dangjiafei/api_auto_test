# -*- coding: utf-8 -*-
# @Time     : 2020/3/1 20:02
# @Author   : Dang_Jiafei
# @Email    : 18840341320@163.com
import os
import unittest
import jsonpath
from common.handle_log import log
from common.handle_excel import ReadExcel
from common.handle_path import DATA_DIR
from library.ddt import data, ddt
from common.handle_request import SendRequest
from common.handle_config import conf
from common.handle_replace_data import CaseData, replace_data

# 测试用例的路径拼接
file_path = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestAdd(unittest.TestCase):
    excel = ReadExcel(file_path, "add")
    cases = excel.read_data()
    request = SendRequest()

    @classmethod
    def setUpClass(cls):
        """管理员账户登录"""
        url = conf.get("item_env", "url") + "/member/login"
        param_data = {
            "mobile_phone": conf.get("test_data", "admin_phone"),
            "pwd": conf.get("test_data", "admin_pwd")
        }
        headers = eval(conf.get("item_env", "headers_v2"))
        response = cls.request.send(url=url, method="post", json=param_data, headers=headers)
        res = response.json()
        token = jsonpath.jsonpath(res, "$...token")[0]
        token_type = jsonpath.jsonpath(res, "$...token_type")[0]
        member_id = jsonpath.jsonpath(res, "$..id")[0]
        # 将提取的数据保存到CaseData的属性中
        CaseData.admin_token_value = token_type + " " + token
        CaseData.admin_member_id = member_id

    @data(*cases)
    def test_add(self, case):
        # 测试数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]
        test_data = eval(replace_data(case["data"]))
        headers = eval(conf.get("item_env", "headers_v2"))
        headers["Authorization"] = getattr(CaseData, "admin_token_value")
        row = case["case_id"] + 1
        # 预期结果
        expected = eval(case["expected"])

        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
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
