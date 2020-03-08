# 该文件处理email邮件的发送
import smtplib
from email.mime.text import MIMEText
from common.handle_config import conf
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class SendEmail:

    @staticmethod
    def send_email(file_name):
        """
        :param file_name: 文件路径
        :return:
        """
        # 连接邮箱的smtp服务器, 并登录
        smtp = smtplib.SMTP_SSL(host=conf.get("email", "host"), port=conf.getint("email", "port"))
        smtp.login(user=conf.get("email", "user"), password=conf.get("email", "pwd"))

        # 创建一封多组件的邮件
        msg = MIMEMultipart()
        with open(file_name, "rb") as f:
            content = f.read()

        # 创建邮件文本内容
        text_msg = MIMEText("注：附件的HTML报告,请下载后查看", _subtype="plain", _charset="utf8")

        # 将文本内容添加到多组件的邮箱中
        msg.attach(text_msg)

        # 创建邮件附件
        report_file = MIMEApplication(content)
        report_file.add_header('content-disposition', 'attachment', filename='report.html')

        # 将文件添加到多组件的邮箱中
        msg.attach(report_file)

        msg['Subject'] = '接口自动化测试报告'  # 标题
        msg['From'] = conf.get("email", "from_addr")  # 发件人
        msg['To'] = conf.get("email", "to_addr")  # 收件人

        # 发送邮件, to_addrs可以传入一个列表，将邮件发送给多个人
        smtp.send_message(msg, from_addr=conf.get("email", "from_addr"), to_addrs=conf.get("email", "to_addr"))
