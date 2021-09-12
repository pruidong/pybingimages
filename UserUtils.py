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
import warnings

__author__ = 'puruidong'

'''

---------------------------------
>>>>>>>>>>>>>>>>>>>>>>>>>>>>
|   2017.5.16 最后更新
>>>>>>>>>>>>>>>>>>>>>>>>>>>>
---------------------------------

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

v1.3.1 -->
             将一个字符串转换为time.

v1.3.2 -->
              1.新增[adjustDateTime]函数,专门用于时间调整.
              2.新增[formatDateToStr]函数,将datetime实例格式化为时间字符串.
              3.将getNowDate函数的[datetime.now()]替换为从参数传入.
              4.修复[parseStrToTime]函数,现已经可以正常将字符串转换为datetime.
              5.修复[getNowDate]函数,并且让其调用内部其余函数实现.


v1.4   -->[预计划]:
            1.提供另外的网络数据获取方式(requests);[---ok]
            2.提供另外的文本获取方式(BeautifulSoup);[---经评估,无法统一对获取后的网页做处理,因此放弃实现]
            3.修复时间获取的方式(使用更好的方式);[---ok]
            4.修复时间戳获取方式;[---ok]
            5.修复时间差计算方式.[---ok]
v1.4.1  -->:
            1.更改字符串的格式化方式(从%更新为{0}.format).

v1.4.2  -->:
            1. 获取文件后缀名时,处理出现&出现的问题.

@date 2015.6.26 v1.0
@date 2015.8.3 v1.1
@date 2015.8.8 v1.1.0
@date 2015.10.29 v1.3
@date 2016.1.10 v1.3.1
@date 2016.06.20 v1.3.2
@version 2016.8.7 v1.4 -- 预计划开始.
@version 2016.10.10 v1.4
@version 2017.5.16 v1.4.1
@version 2019.3.13 v1.4.2

'''


class FileUtils(object):
    '''创建文件目录，并返回该目录'''
    def mkdir(self,path):
        #去除左右两边的空格
        path = path.strip()
        # 去除尾部 \符号
        path = path.rstrip("\\")
        path = self.getFilePath(path)
        if not os.path.exists(path):
            os.makedirs(path)

        return path

    '''获取文件后缀名'''
    def getFileExtension(self,file):
        fileExtension=os.path.splitext(file)[1]
        if(fileExtension.find("&")!=-1):
            return fileExtension[0:fileExtension.find("&")]
        return fileExtension

    '''获取文件的路径'''
    def getFilePath(self,file):
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
    def getFileName(self,file):
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
        result = result.replace('\\n','').replace('\\\n','').replace(' ','')
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
        #value=str(value)
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


    -- 2016.06.20 将[datetime.now()]替换为从参数传入.

    '''
    def getNowDate(self,inputDateTime=datetime.now(),format=FormatDates.YYMMDDHHMMSS,days=0,hours=0,minutes=0, weeks=0):
        warnings.simplefilter("always")
        warnings.warn("getNowDate 即将被弃用,请尽快更换为:[formatDateToStr]函数", DeprecationWarning)
        if isinstance(format,FormatDates):
            if days==0 and hours==0 and minutes==0 and weeks==0:
                return self.formatDateToStr(dateTimeValue=inputDateTime,formatv=format)
            else:
                return self.formatDateToStr(dateTimeValue = self.adjustDateTime(dateTimeValue=inputDateTime,days=days,hours=hours,minutes=minutes, weeks=weeks),formatv=format)
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

    '''
    将一个字符串转换为datetime.

    v: 2016.1.10 新增.
    v: 2016.06.20 修改format参数为枚举.
    '''
    def parseStrToTime(self,value, formatv=FormatDates.YY_MM_DD):
        return datetime.strptime(value, formatv.value)

    '''
    格式化时间.

    v 2016.03.20 新增.
    '''
    def formatDateToStr(self,dateTimeValue=datetime.now(),formatv=FormatDates.YY_MM_DD):
        return dateTimeValue.strftime(formatv.value)

    '''
    调整时间

    !!! 此函数与getNowDate最大不同在于:
            1.支持更多调整类型;
            2.第一个参数必须为datetime实例;
            3.函数内不在提供格式化功能.


    --下面的参数设置偏移。(可以用于获取昨天，前天，下個月，下一小時等.)
    #days 天数:>0为增加
                      <0为減少
    #minutes 分钟.用法同上
    #hours 小时.用法同上
    #weeks 周=7天.用法同上
    #seconds 秒
    #microseconds 微秒
    #milliseconds 毫秒

    v 1.3.2 2016.06.20 新增.

    '''
    def adjustDateTime(self,dateTimeValue=datetime.now(),days=0,hours=0,minutes=0, weeks=0,seconds=0, microseconds=0, milliseconds=0):
        if isinstance(dateTimeValue,datetime):
            return dateTimeValue+timedelta(days=0,hours=0,minutes=0, weeks=0,seconds=0, microseconds=0, milliseconds=0)
        else:
            raise TypeError("[dateTimeValue]必须是datetime实例,若需获取,请参考[parseStrToTime]函数.")



#网络操作.
class NetWorkUtils(object):
    '''
    #通用抓取网页.
    #method 抓取方式,默认GET.
    #site 站点地址.默认百度.
    #headers 头信息.默认无.
    '''
    def network(self,headers=None,methods="GET",site="http://www.baidu.com"):
        http=urllib3.PoolManager()
        r=http.request(methods,site,headers=headers)
        return r.data

    '''

    检查requests是否存在.

    version:v1.4

    '''
    def _checkExistsRequests(self):
        try:
            import requests
        except:
            raise ImportError("要使用Requests,必须先安装,安装使用: pip install requests[当前版本:2.9.1]")

    '''

    检查url是否存在.

    version:v1.4

    '''
    def _checkURLNull(self,url):
        if url:
            return True
        return False

    '''

    使用requests进行网络数据获取.

    此函数直接调用requests库的函数,需要传入指定参数.

    本函数返回内容
        （此处需依赖chekResponseStatus参数的值，该参数若为True，则下面的规则有效；反之，无论是否请求成功都返回Response对象[请注意使用]）：
                    成功--:
                            只返回Response对象.
                    失败--:
                            返回一个字符串,以@分隔,例如：404@错误提示消息...

    requests 参考地址:http://cn.python-requests.org/zh_CN/latest/index.html
    返回响应内容:http://cn.python-requests.org/zh_CN/latest/api.html#requests.Response
    响应常用[r是返回对象]:
        r.text[获取响应的text格式]
        r.content[获取响应的二进制格式]
        r.json()[获取响应的json格式]
        r.raw[原始响应内容]

    -------------------------------------------------------------------

    method: method for the new Request object. [请求方式:GET,POST,PUT，DELETE，HEAD , OPTIONS ]
    url: URL for the new Request object. [地址:请求地址,网页地址]
    chekResponseStatus:[如修改此参数,请先了解其会影响函数返回的内容]
                    默认为True,会执行响应状态检查.反之直接返回响应,不对其状态进行检查.

    kwargs解释[均为可选]:
        params: (optional) Dictionary or bytes to be sent in the query string for the Request.[参数:随请求传递的参数.]
        data:  (optional) Dictionary, bytes, or file-like object to send in the body of the Request.[参数:POST方式传递的参数.]
        json: (optional) json data to send in the body of the Request.[参数:将json数据POST发送.]
        headers:  (optional) Dictionary of HTTP Headers to send with the Request.[请求:发送请求时的请求头数据]
        cookies:  (optional) Dict or CookieJar object to send with the Request.[请求:发送请求时发送cookie数据]
        files: (optional) Dictionary of 'name': file-like-objects (or {'name': file-tuple})
                for multipart encoding upload. file-tuple can be a 2-tuple ('filename', fileobj),
                 3-tuple ('filename', fileobj, 'content_type') or a 4-tuple ('filename', fileobj, 'content_type', custom_headers),
                 where 'content-type' is a string defining the content type of the given file and custom_headers
                 a dict-like object containing additional headers to add for the file.
                 [请求:太复杂了,自己看文档吧.]
        auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.[请求:身份验证.]
        timeout (float or tuple):  (optional) How long to wait for the server to send data before giving up,
                as a float, or a (connect timeout, read timeout) tuple.
                [请求:超时时间,如果只传递一个参数则只表示连接服务器的响应超时时间;
                        如果传递tuple,则第一个数字与传一个参数的效果一样,
                        第二个数字则表示已经连接服务器之后,服务器下载数据的超时时间.]
        allow_redirects (bool):  (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
                [请求后:默认情况下，除了 HEAD, Requests 会自动处理所有重定向。如果设置为False则禁用重定向处理.]
        proxies:  (optional) Dictionary mapping protocol to the URL of the proxy.[请求:使用代理发送请求.]
        verify:  (optional) whether the SSL cert will be verified. A CA_BUNDLE path can also be provided. Defaults to True.[请求:开启SSL证书验证.默认为True]
        stream:  (optional) if False, the response content will be immediately downloaded.[请求后:如果是False,该请求的内容在实际使用的时候才下载.]
        cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
                [请求:你也可以指定一个本地证书用作客户端证书，可以是单个文件（包含密钥和证书）或一个包含两个文件路径的元组.
                        本地证书的私有 key 必须是解密状态。目前，Requests 不支持使用加密的 key。]

    version:v1.4

    '''
    def rrequests(self,method, url,chekResponseStatus=True, **kwargs):
        if self._checkURLNull(url):
            self._checkExistsRequests()
            import requests
            request=requests.request(method,url,**kwargs)
            if chekResponseStatus:
                if request.status_code == requests.codes.ok:
                    return request
                else:
                    if 400 <= request.status_code < 500:
                        http_error_msg = 'Client Error: {0} for url: {1}'.format(request.reason, url)
                    elif 500 <= request.status_code < 600:
                        http_error_msg = 'Server Error: {0},{1} for url: {2}'.format(request.status_code, request.reason, url)
                    return '{0}@{1}'.format(request.status_code,http_error_msg)
            else:
                return request
        else:
            raise ValueError("URL不能为空!请先检查!!")

    '''

    使用get方式发送请求.

    关于参数,请参考rrequests函数.

    version:v1.4

    '''
    def requestsGet(self,url,chekResponseStatus=True,**kwargs):
        if self._checkURLNull(url):
            self._checkExistsRequests()
            return self.rrequests('get',url,chekResponseStatus=chekResponseStatus,**kwargs)
        else:
            raise ValueError("URL不能为空!请先检查!!")

    '''

    使用post方式发送请求.

    关于参数,请参考rrequests函数.

    version:v1.4

    '''
    def requestsPost(self,url,chekResponseStatus=True,**kwargs):
        if self._checkURLNull(url):
            self._checkExistsRequests()
            return self.rrequests('post',url,chekResponseStatus=chekResponseStatus,**kwargs)
        else:
            raise ValueError("URL不能为空!请先检查!!")


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
        print([(date.getNowDate(format=FormatDates.YYMMDD.value,days=i)) for i in range(0,numbs,ns)])


if __name__ == '__main__':
    t=TestDemo()
    #t.logingos(numbs=100)
    t.testInputNt()
    # datesss = DateUtils()2016-06-27T12:11:14.20.18.11
    # strs = "2016-07-30 17:06:12"
    # timeinfo = datetime.strptime(strs,(FormatDates.YY_MM_DD_HH_MM_SS.value))
    # print((timeinfo+timedelta(days=5,hours=8)))
    # print((timeinfo+timedelta(days=45)))
    # print((datesss.parseStrToTime(datesss.getNowDate(),(FormatDates.YYMMDDHHMMSS)))+timedelta(days=5,hours=8))
    # print(datesss.adjustDateTime(days=5,hours=8,minutes=10,seconds=55,milliseconds=20,microseconds=20))
    # print(datesss.getNowDate(days=5,hours=8,minutes=10,format=FormatDates.YY_MM_DD_HH_MM_SS))
    #print("warnings--> update .2016.06.20 v 1.3.2")
