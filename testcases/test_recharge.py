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
from common.handle_replace_data import CaseData
from common.handle_sign import HandleSign
from decimal import Decimal

# 测试用例的路径拼接
case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestRecharge(unittest.TestCase):
    excel = ReadExcel(case_file, "recharge")
    cases = excel.read_data()
    request = SendRequest()
    db = DB()

    @classmethod
    def setUpClass(cls):
        """进行充值之前, 需要登录"""
        url = conf.get("item_env", "url") + "/member/login"
        test_data = {"mobile_phone": conf.get("test_data", "phone"), "pwd": conf.get("test_data", "pwd")}
        headers = eval(conf.get("item_env", "headers_v2"))
        # 发起请求
        response = cls.request.send(url=url, method="post", json=test_data, headers=headers)
        res = response.json()
        token = jsonpath.jsonpath(res, "$..token")[0]
        token_type = jsonpath.jsonpath(res, "$..token_type")[0]

        CaseData.token = token
        CaseData.token_value = token_type + " " + token
        CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])

    @data(*cases)
    def test_recharge(self, case):
        # 测试数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]

        # 动态修改member_id
        case["data"] = case["data"].replace("#member_id#", getattr(CaseData, "member_id"))
        test_data = eval(case["data"])

        # 在请求体中加入时间戳和签名
        sign_info = HandleSign.generate_sign(getattr(CaseData, "token"))
        test_data.update(sign_info)

        # 在headers中加入token鉴权
        headers = eval(conf.get("item_env", "headers_v3"))
        headers["Authorization"] = getattr(CaseData, "token_value")

        # 行号
        row = case["case_id"] + 1

        # 发送请求之前，获取用户的余额
        if case["check_sql"]:
            sql = conf.get("my_sql", "recharge_sql")
            start_money = self.db.find_one(sql)["leave_amount"]

        # 发起请求
        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
        res = response.json()

        # 预期结果
        expected = eval(case["expected"])

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])

            # 判断是否需要进行sql校验
            if case["check_sql"]:
                # 发送请求之后，获取用户的余额
                sql = conf.get("my_sql", "recharge_sql")
                end_money = self.db.find_one(sql)["leave_amount"]
                self.assertEqual(Decimal(str(test_data["amount"])), (end_money - start_money))

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
