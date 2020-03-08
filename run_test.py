import os
import datetime
import unittest
from library.HTMLTestRunnerNew import HTMLTestRunner
from common.handle_path import REPORT_DIR, CASE_DIR
from common.handle_email import SendEmail
from testcases import test_main_stream
from BeautifulReport import BeautifulReport

# 第一步：创建套件
suite = unittest.TestSuite()

# 第二步：加载用例
loader = unittest.TestLoader()
suite.addTest(loader.discover(CASE_DIR))

# 主流程测试用例（冒烟测试）
# suite.addTest(loader.loadTestsFromModule(test_main_stream))

# 时间
date = datetime.datetime.now().strftime("%m_%d_%H_%M_")

# 第三步：执行用例
# runner = HTMLTestRunner(stream=open(os.path.join(REPORT_DIR, date + "report.html"), "wb"),
#                         title="接口自动化测试报告",
#                         description="------",
#                         tester="党佳飞"
#                         )
# runner.run(suite)

# 用BeautifulReport执行, 生成可视化报告
br = BeautifulReport(suite)
br.report("接口自动化测试报告", filename=date + "report.html", report_dir=REPORT_DIR)

# 用例执行后, 发送邮件
# SendEmail.send_email(os.path.join(REPORT_DIR, "report.html"))
