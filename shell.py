#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
shell.py

sqlite3 的 shell 工具
"""

import sqlite3
import sys

HELP_FORMAT = "{0:<10}\t{1}".format


def display_help(conn=None, arg=None):
    """
    输出帮助信息
    """
    print
    print HELP_FORMAT("?", "print this help menu")
    print HELP_FORMAT("connect", "connect to other database")
    print HELP_FORMAT("quit", "quit sqlite3 shell")
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


def display_row(row):
    """
    显示一行
    """
    result = ''
    cell = '|{0:>10}'.format
    for value in row:
        result += cell(value)
    result += '|'
    print result


def display(cursor):
    """
    格式化显示游标结果
    """
    for idx, row in enumerate(cursor):
        n = len(row)
        print '-' * (11 * n + 1)
        if idx == 0:
            display_row(row.keys())
            print '-' * (11 * n + 1)
        display_row(row)
    try:
        print '-' * (11 * n + 1)
    except UnboundLocalError:
        pass


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


COMMANDS = {
    "?": display_help,
    "connect": connect,
    "quit": quit_shell,
    "default": execute_sql,
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
