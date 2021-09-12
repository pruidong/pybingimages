#!/usr/bin/env python3
# -*- coding:utf-8 -*-


__author__ = 'puruidong'

import re
import os
import sys
import io
from UserTools import *
from DaoUtil import *


'''

---------------------------------
>>>>>>>>>>>>>>>>>>>>>>>>>>>>
|   2019.02.05 最后更新
>>>>>>>>>>>>>>>>>>>>>>>>>>>>
---------------------------------


+++++++++++++++++++++++++++++++++++++++++++++++++++

@version 2015.2.1 1.5.0

                    更新内容:
                        1.将抓取Bing首页图片class的代码整合成类,去掉原来不规范的io操作;
                        2.将生成html代码与抓取代码合并成一个文件夹,可用性待验证,主要是为解决在Linux VPS上无法生成HTML页面的问题.
                        3.生成html导致的出错原因是目录问题,现已配置好,应注意目录配置问题!!!


++++++++++++++++++++++++++++++++++++++++++++++++++++++


*****************************************************************
[此注释无效!!]注意:请使用python 2.7版本,切勿使用python 3及以上版本.
*****************************************************************

必须配置root,以使程序可以正常工作.

这是一个下载[微软必应]首页图片的python小程序.

已实现:
    1.按照日期下载到root配置的目录;
    2.下载重复检测[若图片已下载将不再重复下载];
    3.对图片按月分类,图片文件例如:20140723.jpg ;
    4.日志记录:下载成功/重复下载均有日志;
    5.图片下载后,自动清除当天的HTML文件,节省空间;
    6.日志文件最大限制为5M(可在148行代码处修改为其他数字),超过5M前面的记录将被覆盖.
    7.服务器版本无法获取完整url,因此[图片域名前缀]被写成固定ip.
    8.将在第二天下载的时候删除前一天的下载锁.
    9.修复删除前一天的文件锁报错.
    10.创建文件锁,记录日志将检测图片是否已经存在.
    11.判断是否为2号.打包压缩上个月文件夹中的内容.
    12.update mulu.
    13.将图片url写入到json文件中供其他程序读取.
建议:
    1.Linux下可将此文件加入定时任务(推荐凌晨1点),每天自动下载.[定时任务可参考:crontab]
    2.Windows下自行百度定时任务
    3.参考以上两条

2015.1.6 -- 去掉生成json和打包操作


@author puruidong.
@version 2014.8.29 1.0.4
@start_date 2014.7.24
@version 2015.1.16 1.1.0
@version 2015.2.1 1.5.0
----------------------------------
*:上面是python2.7版本的注释,下方是python3+的注释.
@version 2015.7.6 2.0.0  ->此版本改用python3+编写.

注意:urllib3.

[ERROR:无法正常使用,已弃用!!!!需安装Pillow(python2+中的PIL)]

2015.7.6 --在原有代码基础上:
            1.优化抓取速度,不在将html文件保存到本地,从而直接从内存中获取数据,速度更快;
            2.提取公共代码,如抓取,日期处理,文件操作等;
            3.优化及删除部分代码,使代码结构、逻辑更加清晰,明了;
            4.使用全新Python3+版本重写部分代码.

2015.7.7 --除生成更多图片暂时无法使用,其它功能基本可以无错运行.
                    2015.7.10 上面的问题已经解决.

2015.7.10 继续优化部分代码
2015.7.11 測試通過部分代碼,待服務器端測試.
2015.7.29 生成小图无法使用Pillow,暂时解决方案是用Python2.7的PIL生成.

2015.12.23 -- 将图片信息插入到数据库中,并且记录原始URL地址等信息.
2016.1.9 -- 删除生成HTML的部分,并且删除生成小图的部分[图片信息新增到数据库,采用Flask获取].同日启用Flask动态程序处理.

2016.9.21 -- 数据库增加realDate字段,用于记录真实图片日期.

2016.10.10 --
                1.将网页获取方式更换为requests;
                2.去掉函数中的下划线命名;
                3.改变获取日期的方式.

2019.02.05 -- 
                1. 修复URL获取错误的问题;
                2. 保存当天的HTML网页到图片目录,以备图片下载失败时找回当前的数据信息.

2019.03.13 --
                1. 修复url出现&符号无法正确解析的问题.


@version 2015.12.23 3.0
@version 2016.1.9 3.1
@version 2016.9.21 3.2
@version 2016.10.10 3.3
'''

root = "."

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码


class CommonUtil(object):

    """
    将数据新增到数据库.

    source:来源,例如:bing.--> 必选
    imgurl:网络图片地址.--> 必选.
    localimgurl:图片相对路径[相对于root] -->必选
    title:图片描述. --> 可选.

    """
    def insertDB(self,source,imgurl,localimgurl,title):
        if source and imgurl and localimgurl:
            dao = PyDaoUtil("tuimg","content")
            date = DateUtils()
            createDate = date.formatDateToStr(formatv=FormatDates.YY_MM_DD_HH_MM_SS)
            realDate = date.formatDateToStr(formatv=FormatDates.YY_MM_DD)
            insertdata = ({"source":""+source+"","localimgurl":""+localimgurl+"","imgurl":""+imgurl+"","title":""+title+"","createDate":""+createDate+"","realDate":realDate})
            return dao.insertData(insertdata)


''' 必应图片. '''
class Bingimages(object):
    '''获取图片url地址'''
    def getImageUrl(self,data):
        # 修复获取图片地址,2021.08.24
        pn = re.compile('(?<={"Url":").+?(?=","Wallpaper")')
        msatch = pn.search(str(data)).group(0)
        msatch = msatch.replace("u0026","&")
        if (msatch.strip("\\")).find('http://')==-1:
            return "https://cn.bing.com" + (msatch)
        else:
            return (msatch.strip("\\")[:len(msatch)-1])

    '''获取图片的介绍'''
    def getImageTitle(self,data):
        #获取图片的说明 2015.10.19 add
        # 修复获取图片介绍. 2021.08.24
        retitlediv = re.compile('(?<="Title":").+?(?=")')
        titlesearch = str(retitlediv.findall(data))
        copyright = re.compile('(?<="Copyright":").+?(?=")')
        copyrightstr = str(copyright.findall(data))
        #下面是判断字符串中是否包含title字段.该字段中包含图片说明文字.
        #if "title" in str(titlesearch):
        #    retitle = re.compile('(?<=title=").+?(?=")')
        #    resulttitle=retitle.findall(str(titlesearch))
        #    getimgtitle=''.join(resulttitle)
        titlesearch=titlesearch.replace("'","")
        titlesearch=titlesearch.replace("[","")
        titlesearch=titlesearch.replace("]","")
        copyrightstr=copyrightstr.replace("'","")
        copyrightstr=copyrightstr.replace("[","")
        copyrightstr=copyrightstr.replace("]","")
        # print(type(titlesearch))
        return titlesearch+" ("+copyrightstr+")"
        # 获取图片的说明 2015.10.19 end.

    #获取网络数据.
    # *: 2016-10-10 修改.返回的是对象,需要根据所需获取.
    def getPageData(self,sites):
        n=NetWorkUtils()
        return n.requestsGet(url=sites)

class MainClass(object):

    def main(self,path,filedate,log,bi,fileutil,root,month):
        filenames=fileutil.getFileName(__file__)
        '''检查是否已经下载过当天的文件'''
        if os.path.exists(path + filedate + ".lock"):
            messages = "repeat downloads images wanning:downloads image failure."
            log.logw(value=messages,dlineno=os.linesep,dfilename=filenames,LEVEL=30)
            sys.exit(0)

        ''' 获取网页源码  '''
        htmldata=bi.getPageData(sites=url).text
        '''获取图片url'''
        imgurl =bi.getImageUrl(data=htmldata)
        imgurl = imgurl.replace("\\","").replace("\"","").replace(" ","")
        ''' 获取图片的介绍 '''
        imgtitle = bi.getImageTitle(data=htmldata)
        '''获取图片后缀'''
        imgpath = fileutil.getFileExtension(imgurl)
        #print(imgurl+"12123")
        #sys.exit(0)
        '''保存图片到本地'''
        fileutil.mkdir(path)
        filepath=path+filedate + imgpath
        htmldatapath=path+filedate+".txt"
        fileutil.writeFile(filepath=htmldatapath,data=str(htmldata))
        print(bi.getPageData(sites=imgurl))
        fileutil.writeFile(filepath=filepath,data=bi.getPageData(sites=imgurl).content,mode='wb')

        ''' 新增相应数据到数据库 '''
        common = CommonUtil()
        localimgurl = filepath.replace(root,"")
        insertresult = common.insertDB("bing",imgurl,localimgurl,imgtitle)
        insertdbmsg = ""
        if insertresult:
            insertdbmsg =  "image insert db success.imgurl:"+imgurl+",localimgurl:"+localimgurl
        else:
            insertdbmsg =  "image insert db error.imgurl:"+imgurl+",localimgurl:"+localimgurl
        log.logw(value=insertdbmsg,dlineno=os.linesep,dfilename=filenames)
        ''' 新增相应数据到数据库END. '''

        #从下载完成的大图,生成小图
        '''检测图片是否成功下载记录'''
        if os.path.exists(path + filedate + imgpath):
            messages =  "downloads image success."
        else:
            messages =  "images not save."
        log.logw(value=messages,dlineno=os.linesep,dfilename=filenames)
        '''必须图片存在才能创建已经下载过的[锁]文件.'''

        if os.path.exists(path + filedate + imgpath) and fileutil.checkfilesize(path + filedate + imgpath):
            prefiledate = date.getNowDate(format=FormatDates.YYMMDD,days=-1)
            if os.path.exists(path+ prefiledate +".lock"):
                os.remove(path+ prefiledate +".lock")
            if not os.path.exists(path + filedate + ".lock"):
                with open(path + filedate + ".lock", 'w') as fobj:
                    filewrite = fobj.write("1")


if __name__ == '__main__':
    bi=Bingimages()
    date=DateUtils()
    filedate = date.formatDateToStr(formatv=FormatDates.YYMMDD) # 获取当前日期
    nowdate = date.formatDateToStr(formatv=FormatDates.YY_MM_DD_HH_MM_SS)
    nowmonth = date.formatDateToStr(formatv=FormatDates.YYMM)
    path = root + nowmonth + "/"  # 路径
    logpath=path+"downloads.log"
    #--
    log=LogUtils(logpath)
    bi=Bingimages()

    fileutil  = FileUtils()


    '''下载配置'''
    url = "http://cn.bing.com"

    main = MainClass()
    main.main(path=path,filedate=filedate,log=log,bi=bi,fileutil=fileutil,root=root,month=nowmonth)
