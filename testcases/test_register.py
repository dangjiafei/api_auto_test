# -*- coding: utf-8 -*-
# @Time     : 2020/2/22 14:02
# @Author   : Dang_Jiafei
# @Email    : 18840341320@163.com
import os
import random
import unittest
import jsonpath
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from common.handle_request import SendRequest
from common.handle_log import log
from common.handle_db import DB

# 测试用例的路径拼接
case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestRegister(unittest.TestCase):
    excel = ReadExcel(case_file, "register")
    cases = excel.read_data()
    request = SendRequest()
    db = DB()

    @data(*cases)
    def test_register(self, case):
        # 测试数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]

        # 替换excel里面的手机号码
        phone_num = self.phone_number()
        case["data"] = case["data"].replace("#phone#", phone_num)

        test_data = eval(case["data"])
        headers = eval(conf.get("item_env", "headers_v1"))

        # 预期结果
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        # 发起请求
        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
        res = response.json()

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])

            # 注册成功之后，查询数据库进行验证
            if case["check_sql"]:
                user_id = jsonpath.jsonpath(res, "$..id")[0]
                sql = "SELECT mobile_phone FROM futureloan.member WHERE id={}".format(user_id)
                user_phone = self.db.find_one(sql)["mobile_phone"]
                self.assertEqual(phone_num, user_phone)

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

    # 随机生成手机号码
    @classmethod
    def phone_number(cls):
        phone = "158"
        num = random.randint(100000000, 999999999)
        phone = phone + str(num)[1:]
        return phone
