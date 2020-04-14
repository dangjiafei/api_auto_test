# 冒烟测试用例
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
from common.handle_replace_data import replace_data, CaseData

case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
@unittest.skip("跳过冒烟测试用例")
class TestMainStream(unittest.TestCase):
    excel = ReadExcel(case_file, "main_stream")
    cases = excel.read_data()
    request = SendRequest()

    @data(*cases)
    def test_main_stream(self, case):
        # 准备用例数据
        url = conf.get("item_env", "url") + replace_data(case["url"])
        method = case["method"]

        if case["interface"] == "register":
            # 注册接口，则随机生成一个管理员手机号码和普通用户手机号码
            CaseData.admin_phone_num = self.phone_number()
            CaseData.user_phone_num = self.phone_number()

        test_data = eval(replace_data(case["data"]))
        headers = eval(conf.get("item_env", "headers_v2"))

        # 判断是否是登录接口，不是登录接口则需要添加token
        if case["interface"] != "login" and case["interface"] != "register":
            headers["Authorization"] = getattr(CaseData, "token_value")

        expected = eval(case["expected"])
        row = case["case_id"] + 1

        print("请求参数：", test_data)

        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
        res = response.json()

        print("预期结果", expected)
        print("实际结果", res)

        # 发送请求后，判断是否是登陆接口
        if case["interface"].lower() == "login":
            # 提取用户id保存为类属性
            CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
            token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]

            # 提取token,保存为类属性
            CaseData.token_value = token_type + " " + token

        # 判断是否是加标的用例，如果是的则请求标id
        if case["interface"] == "add":
            CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])

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

    # 随机生成手机号码
    @classmethod
    def phone_number(cls):
        phone = "139"
        num = random.randint(100000000, 999999999)
        phone = phone + str(num)[1:]
        return phone
