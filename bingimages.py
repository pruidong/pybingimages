#!/usr/bin/env python3
# -*- coding:utf-8 -*-


__author__ = 'puruidong'

import os
import sys
from UserUtils import *


'''
+++++++++++++++++++++++++++++++++++++++++++++++++++

@version 2015.7.6 2.0.0  ->此版本改用python3+编写.

注意:urllib3.

2015.7.6 --在原有代码基础上:
            1.优化抓取速度,不在将html文件保存到本地,从而直接从内存中获取数据,速度更快;
            2.提取公共代码,如抓取,日期处理,文件操作等;
            3.优化及删除部分代码,使代码结构、逻辑更加清晰明了;
            4.使用全新Python3+版本重写部分代码.


使用方法：
    1.先实现一下38行的函数.[或者email找我];
    2.配置34行的root路径.
    3.运行.

'''

#先配置下面的root路径.
root = ""


class Bingimages(object):
    '''获取图片url地址'''
    def get_imageurl(self,data):
        print("防止被修改方法,大家可自行实现此部分方法.")
        pass

    #获取网络数据.
    def get_webpagedata(self,sites):
        n=NetWorkUtils()
        return n.network(site=sites)


class MainClass(object):

    def main(self,path,filedate,log,bi,fileutil,root,month):
        filenames=fileutil.get_filename(__file__)
        '''检查是否已经下载过当天的文件'''
        if os.path.exists(path + filedate + ".lock"):
            messages = "repeat downloads images wanning:downloads image failure."
            log.logw(value=messages,dlineno=os.linesep,dfilename=filenames,LEVEL=30)
            sys.exit(0)

        '''获取图片url'''
        htmldata=bi.get_webpagedata(sites=url)
        imgurl =bi.get_imageurl(data=htmldata)
        '''获取图片后缀'''
        imgpath = fileutil.get_file_extension(imgurl)
        '''保存图片到本地'''
        fileutil.mkdir(path)
        filepath=path+filedate + imgpath
        fileutil.writeFile(filepath=filepath,data=bi.get_webpagedata(sites=imgurl),mode='wb')
        '''检测图片是否成功下载记录'''
        if os.path.exists(path + filedate + imgpath):
            messages =  "downloads image success."
        else:
            messages =  "images not save."
        log.logw(value=messages,dlineno=os.linesep,dfilename=filenames)
        if os.path.exists(root + "index.html"):
            os.remove(root + 'index.html')

        if os.path.exists(root + "bingimagemore.html"):
            os.remove(root + 'bingimagemore.html')

        '''必须图片存在才能创建已经下载过的[锁]文件.'''

        if os.path.exists(path + filedate + imgpath):
            if not os.path.exists(path + filedate + ".lock"):
                with open(path + filedate + ".lock", 'w') as fobj:
                    filewrite = fobj.write("1")

                if os.path.exists(root + "index.html"):
                    os.remove(root + 'index.html')

                if os.path.exists(root + "bingimagemore.html"):
                    os.remove(root + 'bingimagemore.html')


if __name__ == '__main__':
    date=DateUtils()
    filedate = date.getNowDate(format=FormatDates.YYMMDD) # 获取当前日期
    nowdate = date.getNowDate(format=FormatDates.YY_MM_DD_HH_MM_SS)
    nowmonth = date.getNowDate(format=FormatDates.YYMM)
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
