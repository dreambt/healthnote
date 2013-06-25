# -*- coding: utf-8 -*-
import time
from core.common import getAttr
from model.base import mdb, sdb

_author__ = 'baitao.ji'


class Data():
    def count_all(self):
        sdb._ensure_connected()
        return sdb.query('SELECT COUNT(*) AS num FROM `mh_data`')[0]['num']

    def create_data(self, folk_id='', key='', value=''):
        if folk_id and key:
            timestamp = int(time.time())
            sql = "insert into `mh_data` (`folk_id`,`key`,`value`,`add_date`,`edit_time`)"
            sql += " values(%s,%s,%s,%s,%s)"
            mdb._ensure_connected()
            return mdb.execute(sql, folk_id, key, value, time.strftime("%Y-%m-%d", time.localtime()), timestamp)
        else:
            return None

    def delete_data(self, data_id):
        mdb._ensure_connected()
        query = "DELETE FROM `mh_data` WHERE `data_id`=%s"
        mdb.execute(query, data_id)

    def update_data(self, data_id, value=''):
        if data_id and value:
            timestamp = int(time.time())
            sql = "update `mh_data` set `value`= \'%s\', `edit_time` =\'%s\' " \
                  "where `data_id` = \'%s\' LIMIT 1" % (value, timestamp, data_id)
            mdb._ensure_connected()
            return mdb.execute(sql)
        else:
            return None

    def update_data_by_folk_key(self, folk_id='', key='', value=''):
        if folk_id and key:
            timestamp = int(time.time())
            sql = "update `mh_data` set `value`= \'%s\', `edit_time` =\'%s\' " \
                  "where `folk_id` = \'%s\' and `key` = \'%s\' LIMIT 1" % (value, timestamp, folk_id, key)
            mdb._ensure_connected()
            return mdb.execute(sql)
        else:
            return None

    def get_data(self, data_id):
        sdb._ensure_connected()
        return sdb.get('SELECT * FROM `mh_data` WHERE `data_id` = \'%s\' LIMIT 1' % data_id)

    def get_data_by_key_date(self, folk_id, key, date):
        sdb._ensure_connected()
        return sdb.get('SELECT * FROM `mh_data` WHERE `folk_id` = \'%s\' and `key` = \'%s\' LIMIT 1' % (folk_id, key))

    def get_all(self, folk_id, key=''):
        sdb._ensure_connected()
        sql = "SELECT * FROM `mh_data` WHERE `folk_id` = \'%s\'" % folk_id
        if key:
            sql += " and `key` = \'%s\'" % key
        return sdb.query(sql)

    def get_all_data(self, folk_id, today=''):
        sdb._ensure_connected()
        sql = "select * from `mh_data` left join mh_type on mh_data.key = mh_type.type_id " \
              "where `add_date` = \'%s\' and `folk_id` = \'%s\'" % (today, folk_id)
        return sdb.query(sql)

    # 分页
    def get_paged(self, page=1, limit=None):
        if limit is None:
            limit = getAttr('ADMIN_data_NUM')
        limit = int(limit)
        sdb._ensure_connected()
        sql = "SELECT * FROM `mh_data` ORDER BY `type_order` DESC LIMIT %s,%s" % ((int(page) - 1) * limit, limit)
        return sdb.query(sql)


Data = Data()