# -*- coding: utf-8 -*-
import StringIO
from hashlib import md5
import re
import time
import math

from tornado import escape
import tornado
from tornado.database import OperationalError

from core.common import BaseHandler, authorized, clear_cache_by_pathlist, clear_all_cache, clearAllKVDB, getAttr, sendEmail
from core.storage import put_storage, get_storage_list
from core.utils.random_utils import random_string, random_int
from model.data import Data
from model.folk import Folk
from model.type import Type
from setting import *
from extensions.imagelib import Thumbnail, Recaptcha
from model.user import User
from model.base import MyData


try:
    import json
except:
    import simplejson as json

if not debug:
    import sae.mail


class HomePage(BaseHandler):
    @authorized()
    def get(self):
        output = self.render('admin_index.html', {
            'title': "后台首页",
            'keywords': getAttr('KEYWORDS'),
            'description': getAttr('SITE_DECR'),
            'test': '',
        }, layout='_layout_admin.html')
        self.write(output)
        return output


class DailyController(BaseHandler):
    @authorized()
    def get(self):
        folk_id = self.get_argument("id", '')
        today = time.strftime("%Y-%m-%d", time.localtime())

        # 类型列表
        type_list = Data.get_all_data(folk_id, today)
        if not type_list:
            type_list = Type.get_all()
        else:
            # TODO 补充没有赋值的属性
            pass

        folk = Folk.get_folk(0, folk_id)
        self.echo('admin_daily.html', {
                'title': "数据录入",
                'objs': type_list,
                'folk': folk,
        }, layout='_layout_admin.html')

    @authorized()
    def post(self):
        self.set_header("Content-Type", "application/json")
        folk_id = self.get_argument("folk_id", '')

        type_list = Type.get_all()
        for i in type_list:
            key = str(i.type_id)
            value = self.get_argument(key, '')
            if value:
                try:
                    Data.create_data(folk_id, key, value)
                except:
                    Data.update_data_by_folk_key(folk_id, key, value)

        self.write(json.dumps("OK"))


class ReportController(BaseHandler):
    @authorized()
    def get(self):
        act = self.get_argument("act", '')
        id = self.get_argument("id", '')

        obj = None
        if act == 'del':
            if id:
                Type.delete_type(id)
                clear_cache_by_pathlist(['/'])
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps("OK"))
            return
        elif act == 'edit':
            if id:
                obj = Type.get_type(id)
                clear_cache_by_pathlist(['/'])

        # 类型列表
        type_list = Type.get_all()
        total = math.ceil(Type.count_all() / float(getAttr('ADMIN_TYPE_NUM')))
        self.echo('admin_report.html', {
                'title': "数据报表",
                'objs': type_list,
                'obj': obj,
                'total': total,
        }, layout='_layout_admin.html')

    @authorized()
    def post(self):
        act = self.get_argument("act", '')
        id = self.get_argument("id", '')

        type_name = self.get_argument("type_name", '')
        type_type = self.get_argument("type_type", '')
        type_order = self.get_argument("type_order", 0)

        if id or type_name or type_type or type_order:
            if act == 'add':
                Type.create_type(type_name, type_type, type_order)

            if act == 'edit':
                params = {'type_id': id, 'type_name': type_name, 'type_type': type_type, 'type_order': type_order}
                Type.update_type(params)

            if act == 'del':
                Type.delete_type(id)

            clear_cache_by_pathlist(['/'])

            self.set_header("Content-Type", "application/json")
            self.write(json.dumps("OK"))
        else:
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps("参数异常"))


class FolkController(BaseHandler):
    @authorized()
    def get(self):
        act = self.get_argument("act", '')
        folk_id = self.get_argument("id", '')
        user_id = self.get_secure_cookie("user_id")

        obj = None
        if act == 'del':
            if folk_id:
                Folk.delete_folk(user_id, folk_id)
                clear_cache_by_pathlist(['/'])
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps("OK"))
            return
        elif act == 'edit':
            if folk_id:
                obj = Folk.get_folk(user_id, folk_id)
                clear_cache_by_pathlist(['/'])

        # 亲人列表
        page = self.get_argument("page", 1)
        objs = Folk.get_paged(user_id, page, getAttr('ADMIN_FOLK_NUM'))
        total = math.ceil(Folk.count_all(user_id) / float(getAttr('ADMIN_FOLK_NUM')))
        if page == 1:
            self.echo('admin_folk_list.html', {
                'title': "亲人管理",
                'objs': objs,
                'obj': obj,
                'total': total,
            }, layout='_layout_admin.html')
        else:
            result = {
                'list': objs,
                'total': total,
            }
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(result))
            return

    @authorized()
    def post(self):
        self.set_header("Content-Type", "application/json")
        act = self.get_argument("act", '')
        folk_id = self.get_argument("id", '')

        folk_name = self.get_argument("folk_name", '')
        relation = self.get_argument("relation", '')
        birthday = self.get_argument("birthday", 0)

        if folk_id or folk_name or relation or birthday:
            user_id = self.get_secure_cookie("user_id")
            if act == 'add':
                Folk.create_folk(user_id, folk_name, relation, birthday)

            if act == 'edit':
                params = {'user_id': user_id, 'folk_id': folk_id, 'folk_name': folk_name, 'relation': relation, 'birthday': birthday}
                Folk.update_folk(params)

            if act == 'del':
                Folk.delete_folk(user_id, folk_id)

            clear_cache_by_pathlist(['/'])
            self.write(json.dumps("OK"))
        else:
            self.write(json.dumps("参数异常"))


class TypeController(BaseHandler):
    @authorized()
    def get(self):
        act = self.get_argument("act", '')
        id = self.get_argument("id", '')

        obj = None
        if act == 'del':
            if id:
                Type.delete_type(id)
                clear_cache_by_pathlist(['/'])
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps("OK"))
            return
        elif act == 'edit':
            if id:
                obj = Type.get_type(id)
                clear_cache_by_pathlist(['/'])

        # 类型列表
        page = self.get_argument("page", 1)
        type_list = Type.get_paged(page, getAttr('ADMIN_TYPE_NUM'))
        total = math.ceil(Type.count_all() / float(getAttr('ADMIN_TYPE_NUM')))
        if page == 1:
            self.echo('admin_type_list.html', {
                'title': "数据类型",
                'objs': type_list,
                'obj': obj,
                'total': total,
            }, layout='_layout_admin.html')
        else:
            result = {
                'list': type_list,
                'total': total,
            }
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(result))
            return

    @authorized()
    def post(self):
        self.set_header("Content-Type", "application/json")
        act = self.get_argument("act", '')
        type_id = self.get_argument("id", '')

        type_name = self.get_argument("type_name", '')
        type_type = self.get_argument("type_type", '')
        type_unit = self.get_argument("type_unit", '')
        type_order = self.get_argument("type_order", 0)

        if type_id or type_name or type_type or type_unit or type_order:
            if act == 'add':
                Type.create_type(type_name, type_type, type_unit, type_order)
            elif act == 'edit':
                Type.update_type(type_id, type_name, type_type, type_unit, type_order)
            elif act == 'del':
                Type.delete_type(type_id)

            clear_cache_by_pathlist(['/'])
            self.write(json.dumps("OK"))
        else:
            self.write(json.dumps("参数异常"))


class AddUser(BaseHandler):
    @authorized()
    def get(self):
        obj = User
        obj.user_id = ''
        obj.user_name = ''
        obj.email = ''
        obj.status = 1
        self.echo('admin_user_edit.html', {
            'title': "添加用户",
            'method': "/admin/add_user",
            'obj': obj,
        }, layout='_layout_admin.html')

    @authorized()
    def post(self):
        self.set_header('Content-Type', 'application/json')
        rspd = {'status': 201, 'msg': 'OK'}

        try:
            tf = {'true': 1, 'false': 0}
            email = self.get_argument("email", '')
            name = self.get_argument("username", '')
            pw = random_string(16)
            status = tf[self.get_argument("status", 'true')]
        except:
            rspd['status'] = 500
            rspd['msg'] = '错误： 注意必填项'
            self.write(json.dumps(rspd))
            return

        try:
            userid = User.create_user(name, email, pw, status)
            if userid:
                sendEmail(u"新用户注册通知 - " + SITE_TITLE, u"您的密码是：" + pw + u"<br />请及时登录并修改密码！", email)

                rspd['status'] = 200
                rspd['msg'] = '创建用户成功，已邮件通知该用户！'
                rspd['userid'] = userid
                rspd['method'] = "/admin/edit_user"
                clear_cache_by_pathlist(['/', 'user:%s' % str(userid)])
            else:
                rspd['status'] = 500
                rspd['msg'] = '错误： 通知邮件发送失败，请稍后重试'
        except OperationalError:
            rspd['status'] = 500
            rspd['msg'] = '错误： 该 Email 地址已被占用，请尝试重新提交'
        except:
            rspd['status'] = 500
            rspd['msg'] = '错误： 未知错误，请尝试重新提交'

        self.write(json.dumps(rspd))
        return


class ListUser(BaseHandler):
    @authorized()
    def get(self):
        page = self.get_argument("page", 1)
        limit = getAttr('ADMIN_USER_NUM')
        users = User.get_paged(page, limit)
        total = math.ceil(User.count_all() / float(limit))
        if page == 1:
            self.echo('admin_user_list.html', {
                'title': "用户列表",
                'objs': users,
                'total': total,
            }, layout='_layout_admin.html')
        else:
            result = {
                'list': users,
                'total': total,
            }
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(result))
            return


class EditUser(BaseHandler):
    @authorized()
    def get(self, id=''):
        obj = None
        if id:
            obj = User.get_user(id)
        self.echo('admin_user_edit.html', {
            'title': "编辑用户",
            'method': "/admin/edit_user/" + id,
            'obj': obj
        }, layout='_layout_admin.html')

    @authorized()
    def post(self, id=''):
        self.set_header('Content-Type', 'application/json')
        rspd = {'status': 201, 'msg': 'ok'}

        try:
            tf = {'true': 1, 'false': 0}
            status = tf[self.get_argument("status", 'false')]
            User.update_user_audit(id, status)
            rspd['status'] = 200
            rspd['msg'] = '用户编辑成功'
        except:
            rspd['status'] = 500
            rspd['msg'] = '错误：注意必填项'

        self.write(json.dumps(rspd))
        return


class DelUser(BaseHandler):
    @authorized()
    def get(self, id=''):
        try:
            if id:
                User.delete_user(id)
                cache_key_list = ['/', 'user:%s' % id]
                clear_cache_by_pathlist(cache_key_list)
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps("OK"))
                return
        except:
            raise tornado.web.HTTPError(500)


class RePassword(BaseHandler):
    def get(self):
        self.echo('repass.html')

    def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            name = self.get_argument("name")
            email = self.get_argument("email")
            captcha = self.get_argument("captcha", "")
        except:
            self.write(json.dumps("用户名、邮箱、验证码均为必填项！"))
            return

        if captcha:
            if self.get_secure_cookie("captcha") != captcha:
                self.write(json.dumps("验证码填写错误！"))
                return
        else:
            user_name_cookie = self.get_secure_cookie('username')
            user_pw_cookie = self.get_secure_cookie('userpw')
            if not User.check_user_password(user_name_cookie, user_pw_cookie):
                self.write(json.dumps("重置密码失败！"))
                return

        if name and email and User.check_name_email(name, email):
            pw = random_string(16)
            User.update_user(name, email, pw)
            sub = {
                "%website%": [getAttr("SITE_TITLE").encode('utf-8')],
                "%url%": [getAttr("BASE_URL")],
                "%name%": [name],
                "%password%": [pw]
            }
            #sendTemplateEmail(u"密码重置通知 - " + getAttr('SITE_TITLE'), sub, str(email))
            sendEmail(u"密码重置通知 - " + getAttr('SITE_TITLE'), u"您的新密码是：" + pw + u"<br /><br />请及时登录并修改密码！", str(email))

            self.write(json.dumps("OK"))
            return
        else:
            self.write(json.dumps("重置密码失败！"))
            return


class EditProfile(BaseHandler):
    @authorized()
    def get(self):
        self.echo('admin_profile.html', {
            'title': "个人资料",
        }, layout='_layout_admin.html')

    @authorized()
    def post(self):
        self.set_header("Content-Type", "application/json")
        oldPassword = self.get_argument("oldPassword", '')
        newPassword = self.get_argument("newPassword", '')
        newPassword2 = self.get_argument("newPassword2", '')
        if oldPassword and newPassword and newPassword2:
            if newPassword == newPassword2:
                email = self.get_secure_cookie('email')
                old_user = User.get_user_by_email(email)
                oldPassword = md5(oldPassword.encode('utf-8') + old_user.salt.encode('utf-8')).hexdigest()
                if oldPassword == old_user.password:
                    User.update_user_password(email, newPassword)
                    self.clear_all_cookies()
                    self.write(escape.json.dumps("OK"))
                    return
                else:
                    self.write(escape.json.dumps("更新用户失败！"))
                    pass
        self.write(escape.json.dumps("请认真填写必填项！"))
        return


class FileUpload(BaseHandler):
    @authorized()
    def post(self):
        self.set_header('Content-Type', 'text/html')
        rspd = {'status': 201, 'msg': 'ok'}
        max_size = 10240000  # 10MB
        fileupload = self.request.files['imgFile']
        if fileupload:
            myfile = fileupload[0]
            if not myfile['filename']:
                self.write(json.dumps(
                    {'error': 1, 'message': u'请选择要上传的文件'}
                ))
                return

            # if myfile.size > max_size:
            #     self.write(json.dumps(
            #         { 'error': 1, 'message': u'上传的文件大小不能超过 10 MB'}
            #     ))
            #     return

            file_type = myfile['filename'].split('.')[-1].lower()
            file_name = str(int(time.time() * 1000))
            mime_type = myfile['content_type']
            encoding = None

            # 缩放图片
            try:
                if file_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                    new_file_name = "%s-thumb.%s" % (file_name, file_type)
                    img_data = Thumbnail(StringIO.StringIO(myfile['body'])).thumb((100, 100))
                    put_storage(file_name=new_file_name, data=img_data, expires='365',
                                con_type=mime_type, encoding=encoding)
                    #im = Image.open(StringIO.StringIO(myfile['body']))
                    # im.show()
                    #width, height = im.size
                    #if width > 750:
                    #    ratio = 1.0 * height / width
                    #    new_height = int(750 * ratio)
                    #    new_size = (750, new_height)
                    #    out = im.resize(new_size, Image.ANTIALIAS)
                    #    myfile['body'] = out.toString('jpeg', 'RGB')
                    #    file_type = 'jpg'
                    #    print 750, new_height
                    #    new_file_name = "%s-thumb.%s" % (str(int(time.time())), file_type)
                    #else:
                    #    pass
                else:
                    pass
            except:
                pass

            try:
                new_file_name = "%s.%s" % (file_name, file_type)
                attachment_url = put_storage(file_name=new_file_name, data=myfile['body'], expires='365',
                                             con_type=mime_type, encoding=encoding)
            except:
                attachment_url = ''

            if attachment_url:
                rspd['status'] = 200
                rspd['error'] = 0
                rspd['filename'] = myfile['filename']
                rspd['url'] = attachment_url
            else:
                rspd['status'] = 500
                rspd['error'] = 1
                rspd['message'] = 'put_saestorage error, try it again.'
        else:
            rspd['message'] = 'No file uploaded'
        self.write(json.dumps(rspd))
        return


class FileManager(BaseHandler):
    @authorized()
    def get(self):
        file_list = get_storage_list()

        upload = {
            "moveup_dir_path": "",
            "current_dir_path": "/stor-stub/attachment/",
            "current_url": BASE_URL + "/stor-stub/attachment/",
            "file_list": [],
        }

        for dirfile in file_list:
            filesize = dirfile['length']
            filetype = dirfile['name'].split('.')[-1].lower()
            filename = dirfile['name']
            datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dirfile['datetime']))
            if re.match('gif|jpg|jpeg|png|bmp', filetype):
                is_photo = True
            else:
                is_photo = False
            file_list = {
                "is_dir": False,
                "has_file": False,
                "filesize": filesize,
                "dir_path": "/stor-stub/attachment/",
                "is_photo": is_photo,
                "filetype": filetype,
                "filename": filename,
                "datetime": datetime,
            }
            upload["file_list"].append(file_list)

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(upload))
        return


# TODO KVDB 管理
class KVDBAdmin(BaseHandler):
    @authorized()
    def get(self):
        self.echo('admin_kvdb.html', {
            'title': "KVDB 管理",
        }, layout='_layout_admin.html')

    @authorized()
    def post(self):
        self.redirect('%s/admin/kvdb' % BASE_URL)
        return


class FlushData(BaseHandler):
    @authorized()
    def post(self):
        act = self.get_argument("act", '')
        if act == 'flush':
            MyData.flush_all_data()
            clear_all_cache()
            clearAllKVDB()
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps("OK"))
            return
        elif act == 'flushcache':
            clear_all_cache()
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps("OK"))
            return


class GetCaptcha(BaseHandler):
    def get(self):
        text = random_int(4)
        self.set_secure_cookie("captcha", text)

        strIO = Recaptcha(text)

        # ,mimetype='image/png'
        self.set_header("Content-Type", "image/png")
        self.write(strIO.read())
        return


class SendMail(BaseHandler):
    def post(self):
        subject = self.get_argument("subject", '')
        content = self.get_argument("content", '')

        if subject and content:
            sendEmail(subject, content, getAttr('NOTICE_MAIL'))


class Forbidden(BaseHandler):
    def get(self):
        self.write('Forbidden page')


#####
urls = [
    (r"/admin/", HomePage),
    (r"/admin/daily", DailyController),
    (r"/admin/report", ReportController),
    (r"/admin/folk_list", FolkController),  # 亲人
    (r"/admin/type_list", TypeController),  # 数据类型管理
    # 用户管理
    (r"/admin/add_user", AddUser),
    (r"/admin/edit_user/(\d*)", EditUser),
    (r"/admin/list_user", ListUser),
    (r"/admin/del_user/(\d+)", DelUser),
    (r"/admin/repass_user", RePassword),
    # 文件上传及管理
    (r"/admin/fileupload", FileUpload),
    (r"/admin/filelist", FileManager),
    (r"/admin/profile", EditProfile),
    (r"/admin/kvdb", KVDBAdmin),
    (r"/admin/flushdata", FlushData),
    (r"/captcha/", GetCaptcha),
    (r"/task/sendmail", SendMail),
    (r"/admin/403", Forbidden),
]
