#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import time
from enum import Enum, unique
import os
import logging
import urllib3
import codecs
import re
from PIL import Image
import hashlib
import base64

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

v1.3.1 -->
             将一个字符串转换为time.

v1.3.7-->
             新增一个加密工具类

v1.3.8-->
            新增一个分页程序.

@date 2015.6.26 v1.0
@date 2015.8.3 v1.1
@date 2015.8.8 v1.1.0
@date 2015.10.29 v1.3
@date 2016.1.10 v1.3.1
@date 2016.2.3 v1.3.7
@date 2016.2.27 v1.3.8
'''

"""

分页程序. 2016.2.27 add
"""


class Pager(object):
    """

     处理url参数问题:去掉url参数中的page和pagesize参数,以便添加新参数[判断依据:url中包含"?"].

         传入:http://localhost:5000/admin/list?createdate=2016-01-20&price=100&cagegory=123&page=68&pagesize=10
         将返回:http://localhost:5000/admin/list?createdate=2016-01-20&price=100&cagegory=123
         以便于生成新的页码,并保留查询参数.
         若传递:http://localhost:5000/admin/list,则直接返回,不处理.
      @ date 2016.2.27

    """

    def formaturl(self, url):
        urlinfos = url
        if "?" in urlinfos:
            # 从url中提取参数.
            values = url.split("?")[-1]
            itemsdata = {}
            for keyvalue in values.split("&"):
                params = keyvalue.split("=")
                if params[0]:
                    itemsdata[params[0]] = params[1]
            # 提取参数完毕.

            # 参数判断及去掉page和pagesize参数.
            urlargs = []
            index = 1
            for x in itemsdata:
                if x != "page" and x != "pagesize":
                    if index == 1:
                        urlargs.append("?%s=%s" % (x, itemsdata[x]))
                        index = 10
                    else:
                        urlargs.append("&%s=%s" % (x, itemsdata[x]))
            # 参数判断及去掉page和pagesize参数.

            # 去掉url中?后面的所有参数
            url = url[0:url.find("?")]
            # 连接新url
            urlinfos = url + ("".join((urlargs)))
        return urlinfos

    """

    生成代码示例[使用了妹子UI的分页.参照:http://amazeui.org/widgets/pagination]:

    page: 当前页数,从1开始.
    pagesize: 每页里面多少数据,一般为10.
    rowscount: 查询数据库中的总数(一共有多少条数据,不能添加查询条件,直接count即可).
    url: 直接传入带参数的url即可,对于Flask框架,可以直接:request.url
    countshow=Flase:默认不显示(总XXX条,共XX页,当前X页),如需开启,请传递True.

    """

    def repage(self, page, pagesize, rowscount, url, countshow=False):
        # 处理url参数[去掉page和pagesize参数].
        url = self.formaturl(url)
        # 页码
        ipage = int(page)
        # 原始page ,数值不会被改变
        noformatpage = int(page)  # 原始page
        #  页码大小
        ipagesize = int(pagesize)
        # 总数量
        irowscount = int(rowscount)
        # 进行数值限定
        if ipage <= 1:
            ipage = 1
        # 进行分页查询时,需要跳过的数据.
        # 这个ipage和noformatpage是有区别的!!!
        # 例如,当前是第二页,那么下面这个ipage是10,而noformatpage是不变的2.
        ipage = (ipage - 1) * ipagesize
        # 给当前页添加一个css标记
        currentpage = "am-active"  # 当前
        # 不添加标记
        pageclass = ""  # 正常
        # 空包标记,用于替换.
        black = ""

        '''
        格式化数据.
        主要作用:
            大于/小于当前页5个的自动隐藏.
        比如:
            当前是第6页,那么只显示1-11页,并且第6页在中间.
        示例如下:
            1,2,3,4,5,[6],7,8,9,10,11
            第8页的时候:
                3,4,5,6,7,[8],9,10,11,12,13
            以此类推...
        '''

        def formatstyle(item, noformatpage):
            # 标记最大隐藏的.可配置.
            maxhidden = noformatpage + 5
            # 标记最小隐藏的.可配置
            minhidden = noformatpage - 5
            # 为当前页添加css标记.
            if item == noformatpage:
                return liahref % (currentpage, black, url, item, ipagesize, currentpage, item)
            elif (minhidden) <= item <= (maxhidden):
                # 这个地方是控制显示的,只有符合当前页+5或者-5之内的才显示.
                return liahref % (
                    pageclass, black,
                    url, item,
                    ipagesize,
                    pageclass,
                    item)
            else:  # 不满足条件的全都隐藏.
                return liahref % (
                    pageclass, hiddenstyle,
                    url, item,
                    ipagesize,
                    pageclass,
                    item)

        # 隐藏数据.
        hiddenstyle = "display:none;"
        '''
        %1: 添加各种class,在这里就是:标记当前页.
        %2: 设置隐藏/显示(通过css控制)
        %3: url地址,不带参数的url地址.
        %4: 当前页码,从1开始.
        %5: 数据大小.
        %6: 标记当前页.
        %7: 显示的名称.
        '''
        liahref = "<li class='%s' style='%s'><a href='%s?page=%s&pagesize=%s' class='%s' >%s</a></li>"
        if "?" in url:
            liahref = "<li class='%s' style='%s'><a href='%s&page=%s&pagesize=%s' class='%s' >%s</a></li>"
            # 循环生成数据,并且使用formatstyle控制显示或隐藏.
        htmls = [formatstyle((item+1),noformatpage) for item in range(0, irowscount // ipagesize)]
        # 获取总页数
        countpage = len(htmls)
        # 处理余数的情况
        if irowscount % ipagesize != 0:
            # 最后一页.
            lenindex = len(htmls) + 1
            # 赋值给总页数
            countpage = lenindex
            # 新增到最后.
            htmls.append(liahref % (
                currentpage, black, url, lenindex, ipagesize, currentpage,
                lenindex) if lenindex == noformatpage else liahref % (
                pageclass, black, url, lenindex, ipagesize, pageclass, lenindex))
            # 正确代码***********************************************************
        # 参考上面的a,只是去掉了外层的li标记
        ahref = "<a href='%s?page=%s&pagesize=%s' class='%s'>%s</a>"
        if "?" in url:
            ahref = "<a href='%s&page=%s&pagesize=%s' class='%s'>%s</a>"
        # 第一页和上一页
        firsthrefdisabled = "am-disabled"
        # 生成默认禁用数据
        prevhref = "<a href='javascript:void(0)' class='am-disabled' disabled='disabled'>上一页</a>"
        firsthref = "<a href='javascript:void(0)' class='am-disabled' disabled='disabled'>第一页</a>"
        # 只有当大于1的时候第一页和上一页才可以用.
        if noformatpage > 1:
            firsthrefdisabled = black
            prevhref = ahref % (url, (noformatpage - 1), ipagesize, currentpage, '上一页')
        firsthref = ahref % (url, 1, ipagesize, currentpage, '第一页') if 1 == noformatpage else ahref % (
            url, 1, ipagesize, pageclass, '第一页')
        # 新增到最前面
        htmls.insert(0,
                     "<li class='am-pagination-first %s '>%s</li><li class='am-pagination-prev %s'>%s</li>" % (
                         firsthrefdisabled, firsthref, firsthrefdisabled,
                         prevhref))
        # 第一页和上一页END.
        # 下一页和最末页
        lasthrefdisabled = "am-disabled"
        # 生成默认禁用数据
        nexthref = "<a href='javascript:void(0)' class='am-disabled' disabled='disabled'>下一页</a>"
        lastindexhref = "<a href='javascript:void(0)' class='am-disabled' disabled='disabled'>最末页</a>"
        # 只有当小于总数的时候下一页和最末页才可用.
        if noformatpage < (countpage):
            lasthrefdisabled = black
            nexthref = ahref % (url, (noformatpage + 1), ipagesize, currentpage, '下一页')
            lastindexhref = ahref % (url, countpage, ipagesize, currentpage, '最末页')

        htmls.append(
                " <li class='am-pagination-next  %s '>%s</li><li class='am-pagination-last %s '>%s</li>" % (
                    lasthrefdisabled, nexthref, lasthrefdisabled, lastindexhref))
        # 下一页和最末页END.
        # 显示最后的数据.
        if countshow:
            htmls.append("总%s条,共%s页,当前%s页" % (irowscount, (len(htmls) - 2), page))
        return ipage, ipagesize, ''.join(htmls)


"""  新增一个加密工具类  """


class Encryption(object):
    # md5加密
    def md5(self, str):
        str = str.encode("utf8")
        hash = hashlib.md5()
        hash.update(str)
        return hash.hexdigest()

    # sha 加密.
    def sha(self, str, type=1):
        str = str.encode("utf8")
        hash = None
        result = None
        if type == 1:
            hash = hashlib.sha1()
        elif type == 224:
            hash = hashlib.sha224()
        elif type == 256:
            hash = hashlib.sha256()
        elif type == 384:
            hash = hashlib.sha384()
        elif type == 512:
            hash = hashlib.sha512()
        if hash:
            hash.update(str)
            result = hash.hexdigest()
        return result

    # base64"加密",禁止用于密码加密,因为base64不是安全的!!
    def base64(self, str):
        str = str.encode("utf8")
        return base64.encodebytes(str)


class FileUtils(object):
    '''创建文件目录，并返回该目录'''

    def mkdir(self, path):
        # 去除左右两边的空格
        path = path.strip()
        # 去除尾部 \符号
        path = path.rstrip("\\")
        path = self.get_file_path(path)
        if not os.path.exists(path):
            os.makedirs(path)

        return path

    '''获取文件后缀名'''

    def get_file_extension(self, file):
        return os.path.splitext(file)[1]

    '''获取文件的路径'''

    def get_file_path(self, file):
        return os.path.dirname(file)

    '''检查文件是否存在.'''

    def checkfiles(self, path):
        if os.path.exists(path):
            return True
        else:
            return False

    '''获取文件的大小,单位是[kb]'''

    def checkfilesize(self, path):
        if self.checkfiles(path):
            return (os.path.getsize(path)) / 1024.0
        else:
            return 0

    # 获取文件名.
    def get_filename(self, file):
        return os.path.basename(file)

    '''
    #写文件.
    #
    # filepath 文件路径.
    # data 数据.
    # mode 打开文件模式.
    '''

    def writeFile(self, filepath, data, mode="w+", encoding=None):
        with open(filepath, mode, encoding=encoding) as wf:
            wf.write(data)

    '''
    #读文件.
    #
    #filePath 文件路径.
    #mode 打开文件模式.
    #

    '''

    def readFile(self, filePath, mode="r"):
        data = None
        with open(filePath, mode, buffering=-1, encoding=None) as rf:
            data = rf.read()
        return data


# 格式化参数枚举
@unique
class FormatDates(Enum):
    YYMMDDHHMMSS = "%Y%m%d%H%M%S"
    YYMMDD = "%Y%m%d"
    YYMMDDHH = "%Y%m%d%H"
    DD = "%d"
    YYMM = "%Y%m"
    # 有格式.
    YY_MM_DD_HH_MM_SS = "%Y-%m-%d %H:%M:%S"
    YY_MM_DD = "%Y-%m-%d"
    YY_MM_DD_HH = "%Y-%m-%d %H"
    YY_MM = "%Y-%m"


'''


'''


# 无法正常运行!!!
class ImageUtilsPython3(object):
    # 根据传入的文件参数,进行缩小化图片处理,待测试.
    def formatImage(self, filepathname, newfilesavepath):
        img = Image.open(filepathname)
        smallimg = img.resize((96, 54))
        f = FileUtils()
        f.mkdir(newfilesavepath)
        smallimg.save(newfilesavepath, "JPEG")


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

    def replaceAllHtmlTag(self, htmlstr):
        htmlregex = re.compile(r'<[^>]+>', re.S)
        result = htmlregex.sub('', htmlstr)
        return result

    # 替换html标签.所有待转移的都转换为空.
    def replaceCharEntity(self, htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '', '60': '',
                         'gt': '', '62': '',
                         'amp': '', '38': '',
                         'quot': '', '34': ''}

        re_charEntity = re.compile('&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如>
            key = sz.group('name')  # 去除&;后entity,如>为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr


# 日志
class LogUtils(object):
    '''
    CRITICAL	50
    ERROR	40
    WARNING	30
    INFO	20
    DEBUG	10

    '''

    _logpath = ""

    def __init__(self, logpathsfi):
        self._logpath = logpathsfi

    # kw为{"dfilename":xx,"dlineno":xx}
    def logw(self, value, FORMAT="[%(levelname)s]  %(asctime)-15s   %(dfilename)s %(dlineno)s  [message]:%(message)s",
             LEVEL=20, *, dfilename="NOFILENAME", dlineno=-1):
        # value=str(value)
        logging.basicConfig(level=0, filename=self._logpath, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        a = {"dfilename": dfilename, "dlineno": dlineno}
        logging.log(level=LEVEL, msg=value, extra=a)


# 获取时间.
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

    def getNowDate(self, format=FormatDates.YYMMDDHHMMSS, days=0, minutes=0, hours=0, weeks=0):
        if isinstance(format, FormatDates):
            return (datetime.now() + timedelta(days=days, minutes=minutes, hours=hours, weeks=weeks)).strftime(
                    format.value)
        else:
            raise TypeError("格式化类型必须是FormatDates")

    '''
    日期往前推或者往后推!此函数仅能使用日期.

    numbs>0时,日期往后推numbs天.
    numbs<0时,日期往前推numbs天.
    '''

    def getLastDate(self, numbs, format=FormatDates.YYMMDD):
        ns = 1 if numbs > 0 else -1
        return [(self.getNowDate(format=FormatDates.YYMMDD, days=i)) for i in range(0, numbs, ns)]

    '''
    返回字符串格式的时间戳.

    v: 2015.10.19 修复上一个版本返回的方式.已测可用于其它语言.
    '''

    def getTimestamp(self):
        return str(int(time.mktime(datetime.now().timetuple())) * 1000)

    '''
    将一个字符串转换为time.

    v: 2016.1.10 新增.
    '''

    def parseStrToTime(value, format='%Y-%m-%d'):
        t = time.strptime(value, '%Y-%m-%d %H:%M:%S')
        return time.strftime(format, t)


# 网络操作.
class NetWorkUtils(object):
    ''''''
    # 通用抓取网页.
    # method 抓取方式,默认GET.
    # site 站点地址.默认百度.
    # headers 头信息.默认无.
    ''''''

    def network(self, headers=None, methods="GET", site="http://www.baidu.com"):
        http = urllib3.PoolManager()
        r = http.request(methods, site, headers=headers)
        return r.data


        # def testMobileQsbk(self):


class TestDemo(object):
    def logingos(self, numbs=10):
        date = DateUtils()
        # if numbs>0:
        #     rdate = [(date.getNowDate(format=FormatDates.YYMMDD,days=i)) for i in range(0,numbs,1)]
        #     print(rdate)
        #     return
        # elif numbs<0:
        ns = 1 if numbs > 0 else -1
        print([(date.getNowDate(format=FormatDates.YYMMDD, days=i)) for i in range(0, numbs, ns)])

    def testInputNt(self):
        try:
            url = "http://www.baidu.com"
            n = NetWorkUtils()
            data = n.network(site=url)
            print(data)
            n.writeFile("./test.html", data, mode="w+")
        except Exception as e:
            print("逗比,不要乱输入!")
            raise e


if __name__ == '__main__':
    # t=TestDemo()
    # t.logingos(numbs=100)

    strs = "20150502"
    print((datetime.strptime(strs, "%Y%m%d")))
