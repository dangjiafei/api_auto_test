import os
import unittest
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from common.handle_request import SendRequest
from common.handle_log import log

# 测试用例的路径拼接
case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestLogin(unittest.TestCase):
    excel = ReadExcel(case_file, "login")
    cases = excel.read_data()
    request = SendRequest()

    @data(*cases)
    def test_login(self, case):
        # 测试数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]
        test_data = eval(case["data"])
        headers = eval(conf.get("item_env", "headers_v1"))

        # 预期结果
        expected = eval(case["expected"])

        # 行号
        row = case["case_id"] + 1

        # 发起请求
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
