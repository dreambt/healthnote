# -*- coding: utf-8 -*-
import json
from hashlib import md5
from model.user import User

from setting import *

from core.common import BaseHandler, unquoted_unicode, getAttr, setAttr


class HomePage(BaseHandler):
    # @pagecache()
    def get(self):
        output = self.render('index.html', {
            'title': "%s - %s" % (getAttr('SITE_TITLE'), getAttr('SITE_SUB_TITLE')),
        }, layout='_layout.html')
        self.write(output)
        return output


class SignUp(BaseHandler):
    """用户注册
    """
    def get(self):
        output = self.render('sign-up.html', {
            'title': "%s - %s" % (getAttr('SITE_TITLE'), getAttr('SITE_SUB_TITLE')),
        }, layout='_layout.html')
        self.write(output)
        return output

    def post(self):
        self.set_header("Content-Type", "application/json")

        try:
            email = str(self.get_argument("email"))
            password = str(self.get_argument("password"))
            password2 = str(self.get_argument("password2"))
        except:
            self.write(json.dumps("邮箱、密码、确认密码均为必填项！"))
            return

        if password != password2:
            self.write(json.dumps("两次输入的密码不一致!"))
            return

        has_user = User.get_user_by_email(email)
        if not has_user:
            try:
                # TODO baitao.ji 改造为发送验证邮件后才插入数据库中的用户表
                User.create_user("无名氏", email, password)
                self.write(json.dumps("OK"))
            except:
                self.write(json.dumps("保存用户时数据库超时，请稍后重试!"))
        else:
            self.write(json.dumps("已存在该邮箱, 请尝试其他邮箱或用该邮箱登录!"))
            return


class SignIn(BaseHandler):
    """用户登录
    """
    def get(self):
        output = self.render('sign-in.html', {
            'title': "%s - %s" % (getAttr('SITE_TITLE'), getAttr('SITE_SUB_TITLE')),
        }, layout='_layout.html')
        self.write(output)
        return output

    def post(self):
        self.set_header("Content-Type", "application/json")

        try:
            email = self.get_argument("email")
            password = self.get_argument("password")
        except:
            self.write(json.dumps("邮箱、密码均为必填项！"))
            return

        has_user = User.get_user_by_email(email)
        if has_user:
            password += has_user.salt
            password = md5(password.encode('utf-8')).hexdigest()
            if password == has_user.password:
                self.set_secure_cookie('email', email, expires_days=365)
                self.set_secure_cookie('password', password, expires_days=365)
                role = User
                self.write(json.dumps("OK"))
                return
            else:
                self.write(json.dumps("权限验证失败或帐户不可用!"))
                return
        else:
            self.write(json.dumps("不存在该用户!"))
            return


class SignOut(BaseHandler):
    """用户注销
    """
    def get(self):
        self.clear_all_cookies()
        self.redirect('%s/' % BASE_URL)


class Robots(BaseHandler):
    def get(self):
        self.echo('robots.txt')


class Sitemap(BaseHandler):
    def get(self, id=''):
        self.set_header('Content-Type', 'text/xml')
        self.echo('sitemap.html', {'id': id})


class Attachment(BaseHandler):
    def get(self, name):
        self.redirect('http://%s-%s.stor.sinaapp.com/%s' % (APP_NAME, DEFAULT_BUCKET, unquoted_unicode(name)), 301)
        return


# 初始化一些参数
def Init():
    setAttr('SITE_TITLE', SITE_TITLE)
    setAttr('SITE_TITLE2', SITE_TITLE2)
    setAttr('SITE_SUB_TITLE', SITE_SUB_TITLE)
    setAttr('KEYWORDS', KEYWORDS)
    setAttr('SITE_DECR', SITE_DECR)
    setAttr('ADMIN_NAME', ADMIN_NAME)
    setAttr('NOTICE_MAIL', NOTICE_MAIL)

    setAttr('MAIL_FROM', MAIL_FROM)
    setAttr('MAIL_KEY', MAIL_KEY)
    setAttr('MAIL_SMTP', MAIL_SMTP)
    setAttr('MAIL_PORT', MAIL_PORT)

    setAttr('ADMIN_USER_NUM', ADMIN_USER_NUM)
    setAttr('ADMIN_TYPE_NUM', ADMIN_TYPE_NUM)

    setAttr('ANALYTICS_CODE', ANALYTICS_CODE)
    setAttr('ADSENSE_CODE1', ADSENSE_CODE1)
    setAttr('ADSENSE_CODE2', ADSENSE_CODE2)


class Install(BaseHandler):
    def get(self):
        Init()
        self.echo('admin_install.html')
        # try:
        #     self.write('如果出现错误请尝试刷新本页。')
        #     has_user = User.check_has_user()
        #     if has_user:
        #         self.write('博客已经成功安装了，你可以直接 <a href="/admin/flushdata">清空网站数据</a>')
        #     else:
        #         self.write('博客数据库已经建立，现在就去 <a href="/admin/">设置一个管理员帐号</a>')
        # except:
        #     try:
        #         MyData.creat_table()
        #         Init()  # 初始化系统参数
        #     except:
        #         pass
        #     self.write('博客已经成功安装了，现在就去 <a href="/admin/">设置一个管理员帐号</a>')

    def post(self):
        pass


class NotFoundPage(BaseHandler):
    def get(self):
        self.set_status(404)
        self.echo('error.html', {
            'page': '404',
            'title': "Can't find out this URL",
            'h2': 'Oh, my god!',
            'msg': '<script type="text/javascript" src="http://www.qq.com/404/search_children.js?edition=small" charset="utf-8"></script>'
        })

########
urls = [
    (r"/", SignIn),
    (r"/sign-up.html", SignUp),
    (r"/sign-in.html", SignIn),
    (r"/sign-out.html", SignOut),
    (r"/robots.txt", Robots),
    (r"/sitemap_(\d+)\.xml$", Sitemap),
    (r"/attachment/(.+)$", Attachment),
    (r"/install", Install),
    (r".*", NotFoundPage)
]
