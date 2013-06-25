# -*- coding: utf-8 -*-
import time

from core.common import getAttr
from model.base import mdb, sdb


class Folk():
    def count_all(self, user_id):
        sql = 'SELECT COUNT(*) AS num FROM `mh_folk` left join `mh_user_folk` ' \
              'on mh_folk.folk_id=mh_user_folk.folk_id WHERE mh_user_folk.user_id = %s' % user_id
        sdb._ensure_connected()
        return sdb.query(sql)[0]['num']

    def create_folk(self, user_id='', folk_name='', relation='', birthday=0):
        if folk_name and birthday:
            timestamp = int(time.time())
            sql = "insert into `mh_folk` (`folk_name`,`birthday`, `add_time`, `edit_time`)"
            sql += " values(%s,%s,%s,%s)"
            mdb._ensure_connected()
            folk_id = mdb.execute(sql, folk_name, birthday, timestamp, timestamp)
            if folk_id:
                sql = "insert into `mh_user_folk` (`user_id`,`folk_id`, `relation`) values(%s,%s,%s)"
                mdb._ensure_connected()
                return mdb.execute(sql, user_id, folk_id, relation)
        else:
            return None

    def delete_folk(self, user_id, folk_id):
        query = "DELETE FROM `mh_user_folk` WHERE `user_id`=%s and `folk_id`=%s"
        mdb._ensure_connected()
        mdb.execute(query, user_id, folk_id)

        if not Folk.get_folk(0, folk_id):
            query = "DELETE FROM `mh_folk` WHERE `folk_id`=%s"
            mdb.execute(query, folk_id)

    def update_folk(self, params):
        if params['folk_name'] and params['birthday']:
            timestamp = int(time.time())
            sql = "update `mh_folk` set `folk_name`= \'%s\', `birthday` = \'%s\'" % (params['folk_name'], params['birthday'])
            sql += ", `edit_time` = %s where `folk_id` = \'%s\' LIMIT 1" % (timestamp, params['folk_id'])
            sql2 = "update `mh_user_folk` set `relation`= \'%s\' where `user_id` = %s and `folk_id` = %s" % (params['relation'], params['user_id'], params['folk_id'])
            mdb._ensure_connected()
            mdb.execute(sql2)
            return mdb.execute(sql)
        else:
            return None

    def get_folk(self, user_id, folk_id):
        if user_id:
            sql = "SELECT * FROM `mh_folk` left join `mh_user_folk` on mh_folk.folk_id=mh_user_folk.folk_id " \
              "WHERE mh_user_folk.user_id = %s and mh_folk.folk_id = %s LIMIT 1" % (user_id, folk_id)
        else:
            sql = 'SELECT * FROM `mh_folk` WHERE `folk_id` = %s LIMIT 1' % folk_id
        sdb._ensure_connected()
        return sdb.get(sql)

    def get_all(self):
        sdb._ensure_connected()
        return sdb.query('SELECT * FROM `mh_folk`')

    # 分页
    def get_paged(self, user_id, page=1, limit=None):
        if limit is None:
            limit = getAttr('ADMIN_folk_NUM')
        limit = int(limit)
        sdb._ensure_connected()
        sql = "SELECT * FROM `mh_folk` left join `mh_user_folk` on mh_folk.folk_id=mh_user_folk.folk_id " \
              "WHERE mh_user_folk.user_id = %s ORDER BY `edit_time` DESC LIMIT %s,%s" % (user_id, (int(page) - 1) * limit, limit)
        return sdb.query(sql)


Folk = Folk()