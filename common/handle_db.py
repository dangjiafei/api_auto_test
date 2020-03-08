# 该文件处理数据库中查询等操作

import pymysql
from common.handle_config import conf


class DB(object):

    def __init__(self):
        # 连接数据库
        self.conn = pymysql.connect(host=conf.get("mysql", "host"),
                                    port=conf.getint("mysql", "port"),
                                    user=conf.get("mysql", "user"),
                                    password=conf.get("mysql", "password"),
                                    charset=conf.get("mysql", "charset"),
                                    # 通过设置游标类型，可以控制查询出来的数据类型
                                    cursorclass=pymysql.cursors.DictCursor,
                                    )
        # 创建游标对象
        self.cur = self.conn.cursor()

    def find_one(self, sql):
        """获取查询出来的第一条数据"""
        # 因为数据库有事务隔离性，所以查询之前先提交一次事务，保证数据的统一性
        self.conn.commit()
        self.cur.execute(sql)
        data = self.cur.fetchone()
        return data

    def find_all(self, sql):
        """获取查询出来的所有数据"""
        self.conn.commit()
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def find_count(self, sql):
        """返回查询数据的条数"""
        self.conn.commit()
        return self.cur.execute(sql)

    def close(self):
        """关闭游标，断开连接"""
        self.cur.close()
        self.conn.close()
