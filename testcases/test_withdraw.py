# -*- coding: utf-8 -*-
# @Time     : 2020/2/26 11:09
# @Author   : Dang_Jiafei
# @Email    : 18840341320@163.com
import os
import jsonpath
import unittest
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from common.handle_log import log
from common.handle_request import SendRequest
from common.handle_db import DB
from decimal import Decimal

# 测试用例的路径拼接
case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestWithdraw(unittest.TestCase):
    excel = ReadExcel(case_file, "withdraw")
    cases = excel.read_data()
    request = SendRequest()
    db = DB()

    @data(*cases)
    def test_withdraw(self, case):
        # 测试数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]
        case["data"] = case["data"].replace("#phone#", conf.get("test_data", "phone"))
        case["data"] = case["data"].replace("#pwd#", conf.get("test_data", "pwd"))
        headers = eval(conf.get("item_env", "headers_v2"))

        # 判断是否是取现接口，取现接口则加上请求头token
        if case["interface"].lower() == "withdraw":
            # 在headers中加入token鉴权
            headers["Authorization"] = self.token_value
            case["data"] = case["data"].replace("#member_id#", str(self.member_id))

        test_data = eval(case["data"])
        row = case["case_id"] + 1
        # 预期结果
        expected = eval(case["expected"])

        # 判断是否需要进行sql校验
        if case["check_sql"]:
            sql = case["check_sql"].format(conf.get("test_data", "phone"))
            start_money = self.db.find_one(sql)["leave_amount"]

        # 发起请求
        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
        res = response.json()

        # 判断是否是登录接口，登录接口则提取token和id
        if case["interface"].lower() == "login":
            # 提取用户id保存为类属性
            TestWithdraw.member_id = jsonpath.jsonpath(res, "$..id")[0]
            token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            # 提取用户token保存为类属性
            TestWithdraw.token_value = token_type + " " + token

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])

            # 判断是否需要进行sql校验
            if case["check_sql"]:
                sql = case["check_sql"].format(conf.get("test_data", "phone"))
                end_money = self.db.find_one(sql)["leave_amount"]
                self.assertEqual(Decimal(str(test_data["amount"])), start_money - end_money)

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
