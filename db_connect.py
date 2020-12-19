#! /usr/bin/env python3

import sqlite3


class DatabaseConnect(object):
    def __init__(self, db_name):
        self.db = db_name

    def __enter__(self):
        try:
            self.con = sqlite3.connect(self.db)
        except Exception as e:
            self.con = None
            raise e
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.con != None:
            self.con.commit()
            self.con.close()

    def execute(self, sql, *args):
        return self.con.execute(sql, args)

    def create_table(self, tb_name: str, coulumns: str):
        sql = 'CREATE TABLE ' + tb_name + ' (' + coulumns + ')'
        return self.con.execute(sql)

    def insert(self, tb_name: str, values: str):
        sql = 'INSERT INTO ' + tb_name + ' values (' + values + ')'
        self.con.execute(sql)

    def test(self, *args):
        print('test!')


if __name__ == "__main__":
    with DatabaseConnect('databases/test.db') as db:
        # db.create_table('Movies', 'id str, title str')
        try:
            id = 'aaa'
            result = db.execute('insert into test values(?,?)',id, 'aaa')
            print(result.fetchall())
            if result.fetchall() == []:
                print(None)
        except Exception as e:
            print(e)
