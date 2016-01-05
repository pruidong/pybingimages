#!/usr/bin/env python3
# !-*-coding=utf-8-*-

"""

Python 连接MongoDB.

目前实现:
    增删改查(大部分已经实例运行过).
    对于聚合函数的实现并没有细化(没有提供相关示例).
    官方提供了更多的方法,目前只集成了常用的部分函数(其余可以去官方网站参考).

依赖:
    Python3+
    MongoDB3+
    pymongo3+

参考:
MongoDB官方文档:
        https://docs.mongodb.org/getting-started/python/

pymongo下载提示页面:
        https://pypi.python.org/pypi/pymongo/


相关运行信息:
        运行平台:Linux
        MongoDB版本:3.03
        Python版本:Python 3.4.3
        pymongo(Python连接MongoDB的驱动)版本:3.2

author : prd
version : 0.9 2015.12.11
              2015.12.18 修复几个问题:
                                修改原有的获取数据库名称方式不正确.
                                修改原有获取数据库集合方式的问题.
              2015.12.28 修复一个问题:
                                在查询时,进行分页之前的方式,无法进行正常分页.
                                之前的错误原因(现在已经修复):满足其一条件将不再往下执行,现在已修改方式.
                                举例:
                                    错误的:
                                        if page:
                                            pass
                                        if pageSize:
                                            pass
                                        if page and pageSize:
                                            pass
                                    # 若传递page和pageSize也无法正常获取数据.因为判断完第一个将不再继续执行.

                                    正确的:
                                        if page and pageSize:
                                            pass
                                        if page:
                                            pass
                                        if pageSize:
                                            pass
              2016.1.6 更新:
                                 优化查询方式,简化原有代码结构.此处使用了find()方法.原有方式不再使用.但兼容原有数据.
                                并增加一项功能:设定返回列,或排除返回列.
                                更多细节:http://api.mongodb.org/python/current/api/pymongo/collection.html?highlight=find#pymongo.collection.Collection.find




email : pruidong#gmail.com

"""
import pymongo


class PyDaoUtil(object):
    dbname = None
    collection = None

    def __init__(self, dbname, collection):
        self.dbname = dbname
        self.collection = collection

    """ 返回MongoDB客户端对象. """

    def getClient(self):
        return pymongo.MongoClient("localhost", 27017)

    """ 返回MongoDB的一个数据库 """

    def getDB(self):
        client = self.getClient()
        # 修改原有的获取数据库名称方式不正确. TODO 2015.12.18
        dbdatabase = client['%s' % (self.dbname)]
        return dbdatabase

    """
    添加数据

    可新增单条或者多条.

    单条:json对象,
    多条:json数组.

     """

    def insertData(self, bsonData):
        if self.dbname:
            db = self.getDB()
            collections = self.collection
            if isinstance(bsonData, list):
                # 修改原有获取数据库集合方式的问题. TODO 2015.12.18 get_collection(collections)
                result = db.get_collection(collections).insert_many(bsonData)
                return result.inserted_ids
            return db.get_collection(collections).insert_one(bsonData).inserted_id
        else:
            return None

    """
    删除数据!!!!

    关键字参数:
    oneDeleteFilter->单条删除
    manyDeleteFilter->多条删除

    """

    def deleteData(self, **kwargs):
        if self.dbname:
            collections = self.collection
            db = self.getDB()

            def deleteOne(self, oneDeleteFilter=None):  # 单个删除
                result = db.get_collection(collections).delete_one(oneDeleteFilter)
                return result.deleted_count

            def deleteMany(self, manyDeleteFilter=None):  # 全部删除
                result = db.get_collection(collections).delete_many(manyDeleteFilter)
                return result.deleted_count

            onedel = kwargs.get("oneDeleteFilter", "")
            manydel = kwargs.get("manyDeleteFilter", "")
            if onedel:
                return deleteOne(self, **kwargs)
            elif manydel:
                return deleteMany(self, **kwargs)

    """
    更新数据

    oldData:过滤原有数据,

    关键字参数:

    oneUpdate->单条更新
    manyUpdate->多条更新(如果过滤条件结果存在多条)

    """

    def updateData(self, oldData=None, **kwargs):
        if self.dbname:
            collections = self.collection
            db = self.getDB()

            def updateOne(self, oneOldData=None, oneUpdate=None):  # 单个更新
                result = db.get_collection(collections).update_one(oneOldData, oneUpdate)
                return result.matched_count

            def updateMany(self, manyOldData, manyUpdate=None):  # 全部更新
                result = db.get_collection(collections).update_many(manyOldData, manyUpdate)
                return result.matched_count

            if oldData:
                oneup = kwargs.get("oneUpdate", "")
                manyup = kwargs.get("manyUpdate", "")
                if oneup:
                    return updateOne(self, oldData, **kwargs)
                elif manyup:
                    return updateMany(self, oldData, **kwargs)

    """
    查询数据

    关键字参数:

    dataLimit - > 限定最多返回多少条.
    dataSkip  - > 跳过多少条.
    dataQuery - > 查询限定条件
    dataSortQuery -> 排序条件
    dataProjection ->  返回指定的列或者排除指定的列

    ----------------------------------------------------------------

    oneDataQuery -> 查询单条条件 -- 弃用!!!!

    """

    def findAll(self, **kwargs):
        if self.dbname:
            collections = self.collection
            db = self.getDB()

            def findAllDataQuery(self, dataLimit=None, dataSkip=0, dataQuery=None, dataSortQuery=None,
                                 dataProjection=None):
                '''
                TODO :
                    2016.1.6 更新:
                         优化查询方式,简化原有代码结构.此处使用了find()方法.原有方式不再使用.但兼容原有数据.
                         并增加一项功能:设定返回列,或排除返回列.
                         更多细节:http://api.mongodb.org/python/current/api/pymongo/collection.html?highlight=find#pymongo.collection.Collection.find
                '''
                return db.get_collection(collections).find(filter=dataQuery, projection=dataProjection, skip=dataSkip,
                                                           limit=dataLimit, sort=dataSortQuery)

            return findAllDataQuery(self, **kwargs)

    """
    聚合函数.

    具体参考:
    https://docs.mongodb.org/manual/meta/aggregation-quick-reference/

    """

    def aggregation(self, aggreg):
        if self.dbname:
            collections = self.collection
            db = self.getDB()
            return db.get_collection(collections).aggregate(aggreg)

    """
    统计数据库中的数量,

    关键字参数参考:
    http://api.mongodb.org/python/current/api
    /pymongo/collection.html
    ?_ga=1.21101243.1811534224.1449817089#pymongo.collection.Collection.count

    """

    def countData(self, countQuery=None, **kwargs):
        if self.dbname:
            collections = self.collection
            db = self.getDB()
            if countQuery and kwargs:
                return db.get_collection(collections).count(countQuery, kwargs)
            elif countQuery:
                return db.get_collection(collections).count(countQuery)
            elif kwargs:
                return db.get_collection(collections).count(filter=None, **kwargs)
            else:
                return db.get_collection(collections).count()

    """ 删除集合中所有数据!!!!谨慎调用!!!! """

    def dropAllData(self, dataPassword=None):
        if self.dbname:
            collections = self.collection
            db = self.getDB()
            if dataPassword and isinstance(dataPassword, list):
                db.get_collection(collections).drop()


if __name__ == '__main__':
    # dao = PyDaoUtil("test", "my_collection")
    # # 新增数据.
    # dao.insertData(
    #     {
    #         "title": "MongoDB Overview",
    #         "description": "MongoDB is no sql database",
    #         "by": "百度一下你就知道",
    #         "url": "http://www.baidu.com",
    #         "tags": [
    #             "mongodb",
    #             "database",
    #             "NoSQL"
    #         ],
    #         "likes": 100
    #     })#单个新增.

    # print(dao.insertData([{"a": "67"}, {"a": "67"}, {"x": "5"}]))  # 批量新增.

    # 新增数据.END.

    # 查询数据

    # print(dao.findAll())
    # print(dao.findAll(dataLimit=2, dataSkip=1))
    # print(dao.findAll(dataSkip=1))
    # print(dao.findAll(dataLimit=2))
    # print(dao.findAll(oneDataQuery={"x": "67"}))
    # print(dao.findAll(dataSortQuery=[("x", "55")]))
    # print(dao.findAll(dataQuery={"x": "55"}, dataSortQuery=[("x", "55")]))

    # 查询数据END.

    # 删除数据

    # print(dao.deleteData(manyDeleteFilter={"a": "10000"}))
    # print(dao.deleteData(oneDeleteFilter={"a": "10000"}))


    # 删除数据END.

    # 更新数据

    # print(dao.insertData([{"a": "67"}, {"a": "67"}, {"x": "5"}]))  # 批量新增.
    # print(dao.updateData(oldData={"x": "5"}, oneUpdate={'$set': {"x": "300"}}))
    # print(dao.updateData(oldData={"a": "67"}, manyUpdate={'$set': {"a": "10000"}}))

    # 更新数据END.

    # 清除所有数据[不限定条件,直接删除]
    """

    警告:会删除所有数据,请谨慎调用!!!!!!!!!!!!!!!!!!


    """
    # 清除所有数据END.
    # dao.dropAllData(dataPassword=[123])
    # 查询显示所有数据.
    # print(dao.insertData([{"测试": "测试"}, {"a": "67"}, {"x": "5"}]))

    # print(dao.findAll())
    # 获得数据库中一共有多少条数据.
    # print(dao.countData())
    # print(dao.countData(countQuery={"a":"10000"}))
