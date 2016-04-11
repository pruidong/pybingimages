#!/usr/bin/env python3
#! -*-coding=utf-8-*-

import sqlite3

'''


专注操作SQLite3.


-- SQLite3,方便.

@version 2016.4.10
@author prd.

@version --> 0.1 初始.

'''
class SQLite3Tools(object):

    # 获取数据库
    def getDB(self):
        if not self.dbconn: # 如果还未赋值,则直接给一个
            self.dbconn = sqlite3.connect(self.dbFileName)
            return sqlite3.connect(self.dbFileName)
        else: # 已经赋值则直接返回.
            return self.dbconn

    # 关闭数据库连接.
    def closeDB(self):
        self.dbconn.close()
        self.dbconn = None

    # 工具入口函数getDB()
    def main(self,dbFileName):
        self.dbFileName = dbFileName
        self.dbconn = None

    # 执行:创建表
    def createTable(self,sql):
        self.getDB().execute(sql)
        self.closeDB()

    '''
    执行:插入数据

    @sql :可以为list类型(其中每个项均为str格式的sql语句)
          也可以为str类型.
    '''
    def insert(self,sql):
        if isinstance(sql,list):
            for xsqlitem in sql:
                self.getDB().execute(xsqlitem)
        else:
            print(self.getDB())
            self.getDB().execute(sql)
        print(self.getDB())
        self.getDB().commit()
        print(self.getDB())
        self.closeDB()

    # 执行:查询数据
    def select(self,sql):
        cursor = self.getDB().execute(sql)
        resultDict = cursor
        self.closeDB()
        return resultDict

    # 执行:更新或删除.
    def updateOrDelete(self,sql):
        print(self.getDB())
        self.getDB().execute(sql)
        print(self.getDB())
        self.getDB().commit()
        print(self.getDB())
        result = self.getDB().total_changes
        print(result)
        self.closeDB()
        return result

if __name__ == '__main__':
    print("仅用作演示,供参考.~")
    # 先获取实例
    # tools = SQLite3Tools()

    # 传入数据库文件路径.
    # tools.main("test.db")

    # 创建表.
    # tools.createTable('''
    # CREATE TABLE COMPANY
    #        (ID INT PRIMARY KEY     NOT NULL,
    #        NAME           TEXT    NOT NULL,
    #        AGE            INT     NOT NULL,
    #        ADDRESS        CHAR(50),
    #        SALARY         REAL);
    # 		''')
    # 创建表.END.

    # 单条插入.
    #sqllist = "INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (1, 'Paul', 32, 'California', 20000.00 )"
    #tools.insert(sqllist)
    # END.

    # 多条插入.
    # sqllist = ["INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (2, 'Allen', 25, 'Texas', 15000.00 )",\
    # 	"INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)    VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )",\
    # 	"INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)   VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )"]
    # tools.insert(sqllist)
    # END.

    # 查询
    # sqlselect = '''SELECT id, name, address, salary  from COMPANY'''
    # for x in tools.select(sqlselect):
    # 	print(x)
    # 查询END.

    # 更新
    # updatesql = "UPDATE COMPANY set NAME = 'wzretffgf' where ID=1 ;"
    # tools.updateOrDelete(updatesql)
    # 更新END.

    # 删除
    # updatesql = "DELETE FROM COMPANY  where ID=1 ;"
    # tools.updateOrDelete(updatesql)
    # 删除END.

    # 查询
    # sqlselect = '''SELECT id, name, address, salary  from COMPANY'''
    # for x in tools.select(sqlselect):
    # 	print(x)
    # 查询END.