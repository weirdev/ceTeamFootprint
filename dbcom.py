#!/usr/bin/env python

import mysql.connector
#http://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html

class DBCom(object):

    def __init__(self, database='uihc', user='uihc', password='comp3pi',
                    host='vinci.cs.uiowa.edu'):

        self.connection = mysql.connector.connect(user=user, 
                                        password=password, host=host,
                                        database=database)

        self.cursor = self.connection.cursor()

    def query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def commit(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.close()