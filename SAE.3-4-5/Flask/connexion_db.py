#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from dotenv import load_dotenv
import os
import pymysql.cursors

load_dotenv()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(
            host=os.environ.get("HOST"),
            user=os.environ.get("LOGIN"),    # CORRIGÉ : était "USER" auparavant
            password=os.environ.get("PASSWORD"),
            database=os.environ.get("DATABASE"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        activate_db_options(db)
    return db

def activate_db_options(db):
    cursor = db.cursor()
    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()
    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()
    cursor.execute("SHOW VARIABLES LIKE 'lower_case_table_names'")
    result = cursor.fetchone()
    if result:
        if result['Value'] != '0':
            cursor.execute("SET GLOBAL lower_case_table_names = 0")
            db.commit()
    cursor.close()