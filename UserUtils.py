#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime,timedelta
import time
from enum import Enum, unique
import os
import logging
import urllib3
import codecs
import re
from PIL import  Image

__author__ = 'puruidong'

'''
工具类.


@python version >= 3.4

*:PIL在Python3+中改名为:Pillow[参考:http://pillow.readthedocs.org/en/latest/installation.html#windows-installation]

v1.1 -->
            1.修复写文件无法新增;
            2.修复读取文件未正确返回;
v1.2 -->
            1.修改HTML待转移字符的替换规则[修改后为,所有均转换为空]
            2.新增一个替换HTML标签的方法.
            3.为写文件设置默认编码为utf-8.
v1.3 -->
            1.增加判断文件大小的函数;
            2.增加获取时间戳的函数;
            3.注释及文字简体化(之前由于输入法问题,导致部分文字为繁体.)


@date 2015.6.26 v1.0
@date 2015.8.3 v1.1
@date 2015.8.8 v1.1.0
@date 2015.10.29 v1.3
'''


class FileUtils(object):
    '''创建文件目录，并返回该目录'''
    def mkdir(self,path):
        #去除左右两边的空格
        path = path.strip()
        # 去除尾部 \符号
        path = path.rstrip("\\")
        path = self.get_file_path(path)
        if not os.path.exists(path):
            os.makedirs(path)

        return path

    '''获取文件后缀名'''
    def get_file_extension(self,file):
        return os.path.splitext(file)[1]

    '''获取文件的路径'''
    def get_file_path(self,file):
        return os.path.dirname(file)

    '''检查文件是否存在.'''
    def checkfiles(self,path):
        if os.path.exists(path):
            return True
        else:
            return False

    '''获取文件的大小,单位是[kb]'''
    def checkfilesize(self,path):
        if self.checkfiles(path):
            return (os.path.getsize(path))/1024.0
        else:
            return 0


    #获取文件名.
    def get_filename(self,file):
        return os.path.basename(file)

    '''
    #写文件.
    #
    # filepath 文件路径.
    # data 数据.
    # mode 打开文件模式.
    '''
    def writeFile(self,filepath,data,mode="w+",encoding=None):
        with open(filepath,mode,encoding=encoding) as wf:
            wf.write(data)

    '''
    #读文件.
    #
    #filePath 文件路径.
    #mode 打开文件模式.
    #

    '''
    def readFile(self,filePath,mode="r"):
        data=None
        with open(filePath,mode,buffering=-1,encoding=None) as rf:
            data=rf.read()
        return data

#格式化参数枚举
@unique
class FormatDates(Enum):
    YYMMDDHHMMSS="%Y%m%d%H%M%S"
    YYMMDD="%Y%m%d"
    YYMMDDHH="%Y%m%d%H"
    DD="%d"
    YYMM="%Y%m"
    #有格式.
    YY_MM_DD_HH_MM_SS="%Y-%m-%d %H:%M:%S"
    YY_MM_DD="%Y-%m-%d"
    YY_MM_DD_HH="%Y-%m-%d %H"
    YY_MM="%Y-%m"


'''


'''

#无法正常运行!!!
class ImageUtilsPython3(object):
    #根据传入的文件参数,进行缩小化图片处理,待测试.
    def formatImage(self,filepathname,newfilesavepath):
        img=Image.open(filepathname)
        smallimg=img.resize((96,54))
        f=FileUtils()
        f.mkdir(newfilesavepath)
        smallimg.save(newfilesavepath,"JPEG")


class HTMLUtils(object):


    '''
    替换HTML内容里面的HTML标签，注意内容中不能包含<或者>符号.

    使用示例.
    htmlregex=re.compile('<[\s\S]*?>')
    datas='<p class="web_size" id="title-15083947" style="WORD-BREAK: break-all;">发个小时候的！”</p>'
    result=htmlregex.sub('',datas)
    print(result)
    下面的方式也可以替换.
    dr =re.compile(r'<[^>]+>',re.S)
    jsons =re.sub(dr,'',newx)
    '''
    def replaceAllHtmlTag(self,htmlstr):
        htmlregex=re.compile(r'<[^>]+>',re.S)
        result=htmlregex.sub('',htmlstr)
        return result

    #替换html标签.所有待转移的都转换为空.
    def replaceCharEntity(self, htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '', '60': '',
                         'gt': '', '62': '',
                         'amp': '', '38': '',
                         'quot': '', '34': ''}

        re_charEntity = re.compile('&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  #entity全称，如>
            key = sz.group('name')  #去除&;后entity,如>为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr



#日志
class LogUtils(object):

    '''
    CRITICAL	50
    ERROR	40
    WARNING	30
    INFO	20
    DEBUG	10

    '''

    _logpath=""

    def __init__(self,logpathsfi):
        self._logpath=logpathsfi

    #kw为{"dfilename":xx,"dlineno":xx}
    def logw(self,value,FORMAT="[%(levelname)s]  %(asctime)-15s   %(dfilename)s %(dlineno)s  [message]:%(message)s",LEVEL=20,*,dfilename="NOFILENAME",dlineno=-1):
        value=str(value)
        logging.basicConfig(level=0,filename=self._logpath,format=FORMAT,datefmt="%Y-%m-%d %H:%M:%S")
        a={"dfilename":dfilename,"dlineno":dlineno}
        logging.log(level=LEVEL,msg=value,extra=a)


#获取时间.
class DateUtils(object):

    '''
    获取时间.

    #format 格式化样式。

    --下面的参数设置偏移。(可以用于获取昨天，前天，下個月，下一小時等.)
    #days 天数:>0为增加
                      <0为減少
    #minutes 分钟.用法同上
    #hours 小时.用法同上
    #weeks 周=7天.用法同上

    '''
    def getNowDate(self,format=FormatDates.YYMMDDHHMMSS,days=0, minutes=0, hours=0, weeks=0):
        if isinstance(format,FormatDates):
            return  (datetime.now()+timedelta(days=days,minutes=minutes,hours=hours,weeks=weeks)).strftime(format.value)
        else:
            raise TypeError("格式化类型必须是FormatDates")

    '''
    日期往前推或者往后推!此函数仅能使用日期.

    numbs>0时,日期往后推numbs天.
    numbs<0时,日期往前推numbs天.
    '''
    def getLastDate(self,numbs,format=FormatDates.YYMMDD):
        ns = 1 if numbs>0 else -1
        return [(self.getNowDate(format=FormatDates.YYMMDD,days=i)) for i in range(0,numbs,ns)]

    '''
    返回字符串格式的时间戳.

    v: 2015.10.19 修复上一个版本返回的方式.已测可用于其它语言.
    '''
    def getTimestamp(self):
        return str(int(time.mktime(datetime.now().timetuple()))*1000)



#网络操作.
class NetWorkUtils(object):
    ''''''
    #通用抓取网页.
    #method 抓取方式,默认GET.
    #site 站点地址.默认百度.
    #headers 头信息.默认无.
    ''''''
    def network(self,headers=None,methods="GET",site="http://www.baidu.com"):
        http=urllib3.PoolManager()
        r=http.request(methods,site,headers=headers)
        return r.data


    # def testMobileQsbk(self):
class TestDemo(object):
    def logingos(self,numbs=10):
        date=DateUtils()
        # if numbs>0:
        #     rdate = [(date.getNowDate(format=FormatDates.YYMMDD,days=i)) for i in range(0,numbs,1)]
        #     print(rdate)
        #     return
        # elif numbs<0:
        ns = 1 if numbs>0 else -1
        print([(date.getNowDate(format=FormatDates.YYMMDD,days=i)) for i in range(0,numbs,ns)])

    def testInputNt(self):
        try:
            url="http://www.baidu.com"
            n=NetWorkUtils()
            data=n.network(site=url)
            print(data)
            n.writeFile("./test.html",data,mode="w+")
        except Exception as e:
            print("逗比,不要乱输入!")
            raise e


if __name__ == '__main__':
    # t=TestDemo()
    # t.logingos(numbs=100)

    strs = "20150502"
    print((datetime.strptime(strs,"%Y%m%d")))
