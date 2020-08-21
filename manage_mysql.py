# -*- coding: utf-8 -*-

import MySQLdb

def connect():

    con = MySQLdb.connect(host='xxx', db='xxx', user='xxx', password='xxx')

    return con
