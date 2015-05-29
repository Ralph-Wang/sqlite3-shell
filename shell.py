#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
shell.py

sqlite3 的 shell 工具
"""

import sqlite3
import sys
import re

HELP_FORMAT = "{0:<10}\t{1}".format


def display_help(conn=None, arg=None):
    """
    输出帮助信息
    """
    print
    print HELP_FORMAT("?", "print this help menu")
    print HELP_FORMAT("connect", "connect to other database")
    print HELP_FORMAT("quit", "quit sqlite3 shell")
    print HELP_FORMAT("tables", "show all tables")
    print
    return conn


def connect(conn, file_name):
    """
    连接到别的数据库
    @param {basestring} file_name 数据库所在文件
    @return {sqlite3.Connection} conn 返回新的数据库连接
    """
    conn = sqlite3.connect(file_name)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None
    return conn


def quit_shell(conn=None, arg=None):
    """
    退出 shell
    """
    exit(0)


def render_column(value, width):
    """
    渲染单元格
    """
    cell = ('{0:>%s}' % width).format
    return cell(value)


def display_row(row, widths):
    """
    显示一行
    """
    result = ''
    for value, width in zip(row, widths):
        result += '|' + render_column(value, width)
    result += '|'
    print result


def display_division(widths):
    """
    显示行分割符
    """
    div = ''
    for width in widths:
        div += '+' + '-' * width
    div += '+'
    print div


def display(cursor):
    """
    格式化显示游标结果
    """
    rows = []
    lens = []
    keys = []
    for row in cursor:
        lens.append(map(len, map(str, row)))
        rows.append(row)
        keys = row.keys()
    lens.append(map(len, keys))
    widths = map(max, zip(*lens))
    display_division(widths)
    display_row(keys, widths)
    for row in rows:
        display_division(widths)
        display_row(row, widths)
    display_division(widths)


def execute_sql(conn, sql):
    """
    执行 sql
    @params {sqlite3.Connection} conn 数据库连接
    @params {basestring} sql 要执行的sql
    @return {sqlite3.Connection} conn 返回原来的数据库连接
    """
    try:
        sql = sql.strip()
        cur = conn.execute(sql)
        if sql.lstrip().upper().startswith("SELECT"):
            display(cur)
    except sqlite3.Error as err:
        print "An error occurred:", err.args[0]
    return conn


def tables(conn, arg=None):
    """
    显示所有表
    """
    sql = "select distinct tbl_name as [table_name] from sqlite_master;"
    execute_sql(conn, sql)
    return conn


class FakeRow(object):
    def __init__(self, keys, row):
        self._keys = keys
        self.row = row

    def __iter__(self):
        for value in self.row:
            yield value

    def keys(self):
        return self._keys

def desc(conn, table_name):
    """
    显示表结构
    """
    sql = "select sql from sqlite_master where name='%s'" % table_name
    pattern = re.compile(r'\((.*)\)')
    cur = conn.execute(sql)
    ddl = cur.fetchone()[0]
    fields = pattern.search(ddl).group(1)

    values = fields.split(',')
    fields = ['field', 'type']
    frs = []
    for value in values:
        cells = value.strip().split(' ', 1)
        frs.append(FakeRow(fields, cells))

    display(frs)
    return conn

COMMANDS = {
    "?": display_help,
    "connect": connect,
    "quit": quit_shell,
    "default": execute_sql,
    "tables": tables,
    "desc": desc,
}


def main(database=":memory:"):
    conn = connect(None, database)

    buf = ""
    print "Enter your SQL commands to execute in sqlite3."

    try:
        while True:
            try:
                line = raw_input("sqlite3 >> ")
            except (KeyboardInterrupt, EOFError):
                print
                quit()
            buf += line + " "
            if sqlite3.complete_statement(buf):
                execute_sql(conn, buf)
                buf = ""
            else:
                cmd, args = buf.split(" ", 1)
                if cmd in COMMANDS:
                    conn = COMMANDS[cmd](conn, args.strip())
                    buf = ""

    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
