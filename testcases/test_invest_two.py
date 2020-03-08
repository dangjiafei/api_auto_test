import os
import unittest
import jsonpath
from decimal import Decimal
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from common.handle_request import SendRequest
from common.handle_log import log
from common.handle_db import DB
from common.handle_replace_data import replace_data, CaseData

"""
投资接口：
1、需要有标：管理员登录，加标、审核，
2、用户登录
3、投资用例的执行

# 关于投资的sql校验语句
1、用户表、校验用户余额是否发生变化，变化金额等于所投金额（根据用户id去查member表）
SELECT * FROM futureloan.member WHERE id={}
2、根据用户id和标id去投资表中查用户的投资记录，（invest里面查用户对应的标是否新增一条记录）
SELECT * FROM futureloan.invest WHERE member_id={} and loan_di={}
3、根据用户id去流水表中查询流水记录（查询用户投资之后是否多了一条记录）
SELECT * FROM future.financelog WHERE pay_member_id={}
4、在刚好投满的情况下，可以根据投资记录的id，去回款计划表中查询是否，生成回款计划。
SELECT * FROM future.repayment WHERE invest_id={}

"""
case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestInvestTwo(unittest.TestCase):
    excel = ReadExcel(case_file, "invest_two")
    cases = excel.read_data()
    request = SendRequest()
    db = DB()

    @data(*cases)
    def test_invest_two(self, case):
        # 准备用例数据
        url = conf.get("item_env", "url") + case["url"]
        method = case["method"]
        case["data"] = replace_data(case["data"])
        test_data = eval(case["data"])
        headers = eval(conf.get("item_env", "headers_v2"))
        # 判断是否是登录接口，不是登录接口则需要添加token
        if case["interface"] != "login":
            headers["Authorization"] = getattr(CaseData, "token_value")

        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 获取需要sql校验的数据：
        if case["check_sql"]:
            sql1 = "SELECT * FROM futureloan.member where id={}".format(CaseData.member_id)
            sql2 = "SELECT * FROM futureloan.invest WHERE member_id={} and loan_id={}".format(CaseData.member_id,
                                                                                              CaseData.loan_id)
            sql3 = "SELECT * FROM futureloan.financelog WHERE pay_member_id={}".format(CaseData.member_id)
            # 获取开始的用户余额
            start_amount = self.db.find_one(sql1)["leave_amount"]
            # 获取开始的投资记录条数
            start_invest = self.db.find_count(sql2)
            # 获取用户开始的流水记录条数
            start_fin = self.db.find_count(sql3)

        # 第二步：发送请求，获取结果
        response = self.request.send(url=url, method=method, json=test_data, headers=headers)
        res = response.json()

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
            self.assertIn(expected["msg"], res["msg"])
            # 判断是否需要进行数据库校验
            if case["check_sql"]:
                sql1 = "SELECT * FROM futureloan.member where id={}".format(CaseData.member_id)
                sql2 = "SELECT * FROM futureloan.invest WHERE member_id={} and loan_id={}".format(CaseData.member_id,
                                                                                                  CaseData.loan_id)
                sql3 = "SELECT * FROM futureloan.financelog WHERE pay_member_id={}".format(CaseData.member_id)
                # 获取投资后的用户余额
                end_amount = self.db.find_one(sql1)["leave_amount"]
                self.assertEqual(start_amount - end_amount, Decimal(str(test_data["amount"])))
                # 获取投资后投资记录条数
                end_invest = self.db.find_count(sql2)
                self.assertEqual(end_invest - start_invest, 1)
                # 获取用户投资后的流水记录条数
                end_fin = self.db.find_count(sql3)
                self.assertEqual(end_fin - start_fin, 1)
                # 在这里可以再判断是否是满标的投资用例，如果是满标的用例，再去校验该标的每一条投资记录有没有生成对应的回款计划表
                if "满标" in case["title"]:
                    # 获取当前标所有的投资记录id
                    sql4 = "SELECT id FROM futureloan.invest WHERE loan_id={}".format(CaseData.loan_id)
                    invest_ids = self.db.find_all(sql4)
                    # 遍历该标所有的投资记录，id
                    for invest in invest_ids:
                        sql5 = "SELECT * FROM futureloan.repayment WHERE invest_id={}".format(invest["id"])
                        # 获取当前这条投资记录，生成对应的回款
                        count = self.db.find_count(sql5)
                        # 断言查询到的条数的布尔值是否为True(0的布尔值是Flase,只要不是0条，这个断言就会通过)
                        self.assertTrue(count)
        except AssertionError as e:
            print("预期结果：", expected)
            print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{}，执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))
