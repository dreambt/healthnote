# -*- coding: utf-8 -*-
from os import environ

SAEPY_LOG_VERSION = '0.0.3'
APP_NAME = environ.get("APP_NAME", "")

if 'SERVER_SOFTWARE' in environ:
    debug = False
else:
    debug = True

## 下面需要修改(部署之前修改有效), 部署后可以在后台修改

SITE_TITLE = u"CloudPrint"
SITE_TITLE2 = u"绿色便捷的打印新时代"
SITE_SUB_TITLE = u"CloudPrint"  #副标题
KEYWORDS = u"CloudPrint,云,打印,山东财经大学,创业,绿色,环保,省时"
SITE_DECR = u"CloudPrint 是一个 ********"
ADMIN_NAME = u"baitao.ji"
NOTICE_MAIL = u"dreambt@126.com"

###配置邮件发送信息，提醒邮件用的，必须正确填写，建议用 Gmail
MAIL_FROM = 'postmaster@sdyspj.sendcloud.org'
MAIL_KEY = 'DSvK6ViH'
MAIL_SMTP = 'smtpcloud.sohu.com'
MAIL_PORT = 25
# 收集报错信息用的邮箱
MAIL_TO = 'dev@cms4p.sendcloud.org'

ADMIN_USER_NUM = 15
ADMIN_TYPE_NUM = 15

# 放在网页底部的统计代码
ANALYTICS_CODE = """"""
ADSENSE_CODE1 = """"""
ADSENSE_CODE2 = """"""

# 缓存相关
PAGE_CACHE_TIME = 3600 * 24  # 默认页面缓存时间

# 后台界面设置

MAX_IDLE_TIME = 10  # 数据库最大空闲时间 SAE文档说是30 其实更小，设为5，没问题就不要改了

NUM_SHARDS = 0  # 分片计数器的个数,人少的话用0就可以了，如果由0扩展到比如3，可能程序需要稍微修改一下
if NUM_SHARDS > 0:
    SHARD_COUNT_SUPPORT = True  # 是否支持分片计数器
else:
    SHARD_COUNT_SUPPORT = False

####除了修改上面的设置，你还需要开通下面几项服务：
# 1 初始化 Mysql
# 2 建立一个名为 attachment 的 Storage
# 3 启用Memcache，初始化大小为1M的 mc，大小可以调，日后文章多了，PV多了可增加
# 4 创建一个 名为 default 的 Task Queue
# 详见 http://saepy.sinaapp.com/t/50 详细安装指南

############## 下面不建议修改 ###########################

###设置容易调用的jquery 文件
JQUERY = "http://lib.sinaapp.com/js/jquery/1.6.2/jquery.min.js"

COPY_YEAR = '2011 - 2013'

MAJOR_DOMAIN = '%s.sinaapp.com' % APP_NAME  # 主域名，默认是SAE 的二级域名
#MAJOR_DOMAIN = 'www.yourdomain.com'

LANGUAGE = 'zh-CN'

LINK_BROLL = [
    {"text": '思奇博客', "url": 'http://www.im47.cn'},
]

#  当发表新博文时自动ping RPC服务，中文的下面三个差不多了
XML_RPC_ENDPOINTS = [
    'http://blogsearch.google.com/ping/RPC2',
    'http://rpc.pingomatic.com/',
    'http://ping.baidu.com/ping/RPC2'
]

# 安全密钥
COOKIE_SECRET = '7nVA0WeZSJSzTCUF8UZB/C3OfLrl7k26iHxfnVa9x0I='
#import base64
#import uuid
#print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

###############
# MySQL 数据库 #
###############
if debug:
    BASE_URL = 'http://localhost:8080'
    STATIC_URL = BASE_URL
    MYSQL_DB = 'app_healthnote'
    MYSQL_USER = 'root'
    MYSQL_PASS = 'hisense2002j'
    MYSQL_HOST_M = '127.0.0.1'
    MYSQL_HOST_S = '127.0.0.1'
    MYSQL_PORT = '3306'
else:
    BASE_URL = 'http://%s' % MAJOR_DOMAIN
    STATIC_URL = 'http://healthnote.sinaapp.com'
    import sae.const

    MYSQL_DB = sae.const.MYSQL_DB
    MYSQL_USER = sae.const.MYSQL_USER
    MYSQL_PASS = sae.const.MYSQL_PASS
    MYSQL_HOST_M = sae.const.MYSQL_HOST
    MYSQL_HOST_S = sae.const.MYSQL_HOST_S
    MYSQL_PORT = sae.const.MYSQL_PORT

#########
# 云存储 #
#########
#使用SAE Storage 服务（保存上传的附件），需在SAE管理面板创建
DEFAULT_BUCKET = 'attachment'