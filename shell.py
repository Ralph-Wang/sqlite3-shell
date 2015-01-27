#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import sys


HELP_FORMAT = "{0:<10}\t{1}".format
def help(conn=None, arg=None):
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
    conn.isolation_level = None
    return conn

def quit(conn=None, arg=None):
    exit(0)

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
            print cur.fetchall()
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
    return conn


COMMANDS = {
        "?": help,
        "connect": connect,
        "quit": quit,
        "default": execute_sql,
        }


def main(db=":memory:"):
    conn = connect(None, db)

    buffer = ""
    print "Enter your SQL commands to execute in sqlite3."

    try:
        while True:
            try:
                line = raw_input("sqlite3 >> ")
            except (KeyboardInterrupt, EOFError):
                print
                quit()
            buffer += line + " "
            if sqlite3.complete_statement(buffer):
                execute_sql(conn, buffer)
                buffer = ""
            else:
                cmd, args = buffer.split(" ", 1)
                if cmd in COMMANDS:
                    conn = COMMANDS[cmd](conn, args.strip())
                    buffer = ""

    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
