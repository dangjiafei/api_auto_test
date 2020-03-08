# 该文件处理接口的请求

import requests


class SendRequest(object):

    def __init__(self):
        self.session = requests.session()

    """cookies+session鉴权的请求类封装"""
    def send(self, url, method, headers=None, params=None, json=None, data=None, files=None):
        if method == "get":
            response = self.session.get(url=url, params=params, headers=headers)
        elif method == "post":
            response = self.session.post(url=url, json=json, data=data, files=files, headers=headers)
        elif method == "patch":
            response = self.session.patch(url=url, json=json, data=data, headers=headers)
        return response
