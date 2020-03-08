# -*- coding: utf-8 -*-
# @Time     : 2020/3/2 19:41
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

# 测试用例的路径拼接
case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestInvest(unittest.TestCase):
    excel = ReadExcel(case_file, "invest")
    cases = excel.read_data()
    request = SendRequest()

    @data(*cases)
    def test_invest(self, case):
        # 测试数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]
        case["data"] = replace_data(case["data"])
        test_data = eval(case["data"])
        headers = eval(conf.get("item_env", "headers_v2"))
        # 判断是否是登录接口，不是登录接口则需要添加token
        if case["interface"] != "login":
            headers["Authorization"] = getattr(CaseData, "token_value")

        # 预期结果
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        # 发起请求
        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
        res = response.json()

        # 判断是否是登录接口，登录接口则提取token和id
        if case["interface"].lower() == "login":
            # 提取用户id保存为类属性
            CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
            token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            # 提取用户token保存为类属性
            CaseData.token_value = token_type + " " + token

        if case["interface"].lower() == "add":
            CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            # self.assertEqual(expected["msg"], res["msg"])
            # 成员断言（包含断言）
            self.assertIn(expected["msg"], res["msg"])
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
