# 该文件处理需要通过rsa加密方式鉴权的接口
import rsa
import base64
from time import time

# 需要安装rsa模块, pip install rsa


class HandleSign:
    server_pub = """
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQENQujkLfZfc5Tu9Z1LprzedE
    O3F7gs+7bzrgPsMl29LX8UoPYvIG8C604CprBQ4FkfnJpnhWu2lvUB0WZyLq6sBr
    tuPorOc42+gLnFfyhJAwdZB6SqWfDg7bW+jNe5Ki1DtU7z8uF6Gx+blEMGo8Dg+S
    kKlZFc8Br7SHtbL2tQIDAQAB
    -----END PUBLIC KEY-----
    """

    @classmethod
    def to_encrypt(cls, msg, pub_key=None):
        """
        非对称加密
        :param msg: 待加密字符串或者字节
        :param pub_key: 公钥
        :return: 密文
        """
        if isinstance(msg, str):  # 如果msg为字符串, 则转化为字节类型
            msg = msg.encode('utf-8')
        elif isinstance(msg, bytes):  # 如果msg为字节类型, 则无需处理
            pass
        else:  # 否则抛出异常
            raise TypeError('msg必须为字符串或者字节类型!')

        if not pub_key:  # 如果pub_key为空, 则使用全局公钥
            pub_key = cls.server_pub.encode("utf-8")
        elif isinstance(pub_key, str):  # 如果pub_key为字符串, 则转化为字节类型
            pub_key = pub_key.encode('utf-8')
        elif isinstance(pub_key, bytes):  # 如果msg为字节类型, 则无需处理
            pass
        else:  # 否则抛出异常
            raise TypeError('pub_key必须为None、字符串或者字节类型!')

        public_key_obj = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key)  # 创建 PublicKey 对象

        cryto_msg = rsa.encrypt(msg, public_key_obj)  # 生成加密文本
        cipher_base64 = base64.b64encode(cryto_msg)  # 将加密文本转化为 base64 编码

        return cipher_base64.decode()  # 将字节类型的 base64 编码转化为字符串类型

    @classmethod
    def generate_sign(cls, token_value, timestamp=None):
        """
        生成sign
        :param timestamp: 当前秒级时间戳, 为int类型
        :param token_value: token, 为str类型
        :return: 时间戳和sign组成的字典
        """
        timestamp = timestamp or int(time())  # 获取当前的时间戳
        prefix_50_token = token_value[:50]  # 获取token前50位
        message = prefix_50_token + str(timestamp)  # 将token前50位与时间戳字符串进行拼接
        sign = cls.to_encrypt(message)  # 使用rsa加密生成sign

        return {"timestamp": timestamp, "sign": sign}


if __name__ == '__main__':
    token = "eyJhbGciOiJIUzUxMiJ9.eyJtZW1iZXJfaWQiOjI2NSwiZXhwIjoxNTc0NjY3MjMzfQ.ftrNcidmk_zxwl0" \
            "wzdhE5_39bsGlILoSSoTCy043fjhbjhCFG4FwCnOj4iy5svbDlSbgCJM3qRa1zsXJLJmH4A"

    cryto_info = HandleSign.generate_sign(token)
    print(cryto_info)
