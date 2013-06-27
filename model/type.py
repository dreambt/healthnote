# -*- coding: utf-8 -*-
from core.common import getAttr
from model.base import mdb, sdb

_author__ = 'baitao.ji'


class Type():
    def count_all(self):
        sdb._ensure_connected()
        return sdb.query('SELECT COUNT(*) AS num FROM `mh_type`')[0]['num']

    def create_type(self, type_name='', type_type='', type_unit='', type_order=0):
        if type_name and type_type:
            sql = "insert into `mh_type` (`type_name`,`type_type`,`type_unit`,`type_order`)"
            sql += " values(\'%s\',\'%s\',\'%s\',\'%s\')" % (type_name, type_type, type_unit, type_order)
            mdb._ensure_connected()
            return mdb.execute(sql)
        else:
            return None

    def delete_type(self, type_id):
        mdb._ensure_connected()
        query = "DELETE FROM `mh_type` WHERE `type_id`=%s"
        mdb.execute(query, type_id)

    def update_type(self, type_id, type_name='', type_type='', type_unit='', type_order=0):
        sql = "update `mh_type` set `type_name`= \'%s\', `type_type` = \'%s\', `type_unit` = \'%s\', `type_order` = %s " \
              "where `type_id` = \'%s\' LIMIT 1" % (type_name, type_type, type_unit, type_order, type_id)
        mdb._ensure_connected()
        return mdb.execute(sql)

    def get_type(self, type_id):
        sdb._ensure_connected()
        return sdb.get('SELECT * FROM `mh_type` WHERE `type_id` = %s LIMIT 1' % type_id)

    def get_all(self):
        sdb._ensure_connected()
        return sdb.query('SELECT *,\'\' as value FROM `mh_type` ORDER BY `type_order` DESC')

    # 分页
    def get_paged(self, page=1, limit=None):
        if limit is None:
            limit = getAttr('ADMIN_TYPE_NUM')
        limit = int(limit)
        sdb._ensure_connected()
        sql = "SELECT * FROM `mh_type` ORDER BY `type_order` DESC LIMIT %s,%s" % ((int(page) - 1) * limit, limit)
        return sdb.query(sql)


Type = Type()