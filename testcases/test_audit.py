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
from common.handle_db import DB

# 测试用例的路径拼接
case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestAudit(unittest.TestCase):
    excel = ReadExcel(case_file, "audit")
    cases = excel.read_data()
    request = SendRequest()
    db = DB()

    @classmethod
    def setUpClass(cls) -> None:
        """进行登录"""
        url = conf.get("item_env", "url") + "/member/login"
        test_data = {"mobile_phone": conf.get("test_data", "admin_phone"), "pwd": conf.get("test_data", "admin_pwd")}
        headers = eval(conf.get("item_env", "headers_v2"))
        # 发起请求
        response = cls.request.send(url=url, method="post", json=test_data, headers=headers)
        res = response.json()
        token = jsonpath.jsonpath(res, "$..token")[0]
        token_type = jsonpath.jsonpath(res, "$..token_type")[0]
        CaseData.admin_token_value = token_type + " " + token
        CaseData.admin_member_id = str(jsonpath.jsonpath(res, "$..id")[0])

    def setUp(self) -> None:
        """进行加标"""
        url = conf.get("item_env", "url") + "/loan/add"
        headers = eval(conf.get("item_env", "headers_v2"))
        headers["Authorization"] = getattr(CaseData, "admin_token_value")
        test_data = {"member_id": getattr(CaseData, "admin_member_id"),
                     "title": "借钱实现财富自由",
                     "amount": 2000,
                     "loan_rate": 12.0,
                     "loan_term": 3,
                     "loan_date_type": 1,
                     "bidding_days": 5
                     }
        # 发送请求，添加项目
        response = self.request.send(url=url, method="post", json=test_data, headers=headers)
        res = response.json()
        # 提取审核需要用到的项目ID
        CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])

    @data(*cases)
    def test_audit(self, case):
        # 测试数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]
        case["data"] = replace_data(case["data"])
        test_data = eval(case["data"])
        headers = eval(conf.get("item_env", "headers_v2"))
        headers["Authorization"] = getattr(CaseData, "admin_token_value")
        # 预期结果
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        # 发起请求
        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
        res = response.json()

        # 判断是否为审核通过的用例，并且审核通过
        if res["code"] == 0 and case["title"] == "审核通过":
            CaseData.pass_loan_id = test_data["loan_id"]

        # 断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 判断是否需要sql校验
            if case["check_sql"]:
                sql = replace_data(case["check_sql"])
                status = self.db.find_one(sql)["status"]
                # 判断数据库中的标状态字段是否和预期一样
                self.assertEqual(expected["status"], status)

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
