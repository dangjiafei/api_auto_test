# 该文件处理mock数据的返回
from unittest import mock


class MockResponse:

    @staticmethod
    def mock_request(mock_method, request_data, url, method, response_data):
        """
        :param mock_method: 请求的方法名
        :param request_data: 请求的参数
        :param url: 请求的url
        :param method: 请求的方式
        :param response_data: 响应的数据
        :return: 响应的数据
        """
        mock_method = mock.Mock(return_value=response_data)
        res = mock_method(url=url, method=method, request_data=request_data)
        return res


mo = MockResponse()
