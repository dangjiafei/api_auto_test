# 该文件处理webservice接口的请求

# 需要安装 pip install suds-jurko

import suds
from suds import client


class WebserviceRequest:

    @staticmethod
    def webservice_send(url, method, *args, **kwargs):
        """
        :param url: webservice接口的地址
        :param method: webservice接口的请求方法
        :param args: 请求的参数
        :param kwargs:
        :return:
        """
        # 创建客户端对象
        cli = client.Client(url=url)
        # 根据参数构造请求方法
        request_method = eval("cli.service.{}".format(method))
        try:
            # 发送请求
            res = request_method(*args, **kwargs)
        except suds.WebFault as e:
            return dict(e.fault)
        else:
            return dict(res)
