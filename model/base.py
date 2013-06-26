# -*- coding: utf-8 -*-
import re

from tornado import database

from core.common import safe_encode
from setting import *


##
HTML_REG = re.compile(r"""<[^>]+>""", re.I | re.M | re.S)
CODE_RE = re.compile(r"""\[code\](.+?)\[/code\]""", re.I | re.M | re.S)

#主数据库 进行Create,Update,Delete 操作
mdb = database.Connection("%s:%s" % (MYSQL_HOST_M, str(MYSQL_PORT)), MYSQL_DB, MYSQL_USER, MYSQL_PASS,
                          max_idle_time=MAX_IDLE_TIME)
#从数据库 读取
sdb = database.Connection("%s:%s" % (MYSQL_HOST_S, str(MYSQL_PORT)), MYSQL_DB, MYSQL_USER, MYSQL_PASS,
                          max_idle_time=MAX_IDLE_TIME)


def n2br(text):
    con = text.replace('>\n\n', '>').replace('>\n', '>')
    con = "<p>%s</p>" % ('</p><p>'.join(con.split('\n\n')))
    return '<br/>'.join(con.split("\n"))


def tran_content(text, code=False):
    if code:
        codetag = '[mycodeplace]'
        codes = CODE_RE.findall(text)
        for i in range(len(codes)):
            text = text.replace(codes[i], codetag)
        text = text.replace("[code]", "").replace("[/code]", "")

        text = n2br(text)

        a = text.split(codetag)
        b = []
        for i in range(len(a)):
            b.append(a[i])
            try:
                b.append('<pre><code>' + safe_encode(codes[i]) + '</code></pre>')
            except:
                pass

        return ''.join(b)
    else:
        return n2br(text)


class MyData():
    def flush_all_data(self):
        mdb._ensure_connected()
        sql = """
        TRUNCATE TABLE `cp_user`;
        TRUNCATE TABLE `cp_role`;
        TRUNCATE TABLE `cp_user_role`;
        TRUNCATE TABLE `cp_function`;
        TRUNCATE TABLE `cp_role_function`;
        TRUNCATE TABLE `cp_merchant`;
        """
        mdb.execute(sql)

    def creat_table(self):
        sql = """
DROP TABLE IF EXISTS `mh_user`;
CREATE TABLE IF NOT EXISTS `mh_user` (
  `user_id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_name` varchar(20) NOT NULL DEFAULT '',
  `email` varchar(40) NOT NULL DEFAULT '',
  `password` varchar(32) NOT NULL DEFAULT '',
  `salt` varchar(8) NOT NULL DEFAULT '',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0',
  `edit_time` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

DROP TABLE IF EXISTS `mh_type`;
CREATE TABLE IF NOT EXISTS `mh_type` (
  `type_id` int unsigned NOT NULL AUTO_INCREMENT,
  `type_name` varchar(40) NOT NULL DEFAULT '',
  `type_type` varchar(20) NOT NULL DEFAULT '',
  `type_unit` varchar(20) NOT NULL DEFAULT '',
  `type_order` tinyint(3) NOT NULL DEFAULT 0,
  PRIMARY KEY (`type_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

DROP TABLE IF EXISTS `mh_data`;
CREATE TABLE IF NOT EXISTS `mh_data` (
  `data_id` int unsigned NOT NULL AUTO_INCREMENT,
  `folk_id` varchar(20) NOT NULL DEFAULT '',
  `key` varchar(40) NOT NULL DEFAULT '',
  `value` varchar(32) NOT NULL DEFAULT '',
  `add_date` varchar(20) NOT NULL DEFAULT '',
  `edit_time` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`data_id`),
  UNIQUE (`folk_id`, `key`, `add_date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

DROP TABLE IF EXISTS `mh_folk`;
CREATE TABLE IF NOT EXISTS `mh_folk` (
  `folk_id` int unsigned NOT NULL AUTO_INCREMENT,
  `folk_name` varchar(20) NOT NULL DEFAULT '',
  `birthday` varchar(20) NOT NULL DEFAULT '',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0',
  `edit_time` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`folk_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

DROP TABLE IF EXISTS `mh_user_folk`;
CREATE TABLE IF NOT EXISTS `mh_user_folk` (
  `user_id` int unsigned NOT NULL,
  `folk_id` int unsigned NOT NULL,
  `relation` varchar(20) NOT NULL DEFAULT '',
  PRIMARY KEY (`user_id`, `folk_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

"""
        mdb._ensure_connected()
        mdb.execute(sql)


MyData = MyData()
