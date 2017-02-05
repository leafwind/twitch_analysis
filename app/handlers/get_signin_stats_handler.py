# -*- coding: utf-8 -*-
import sqlite3
import numpy as np
import pandas as pd
import logging
import time
from datetime import datetime
import json
from collections import OrderedDict
import math

with open('config.json') as fp:
    CONFIG = json.load(fp)

html_newline = '<br />'

def h1(s):
    return "<h1>" + s + "</h1>"
def h2(s):
    return "<h2>" + s + "</h2>"
def ul(s):
    return "<ul>" + s + "</ul>"
def li(s):
    return "<li>" + s + "</li>"
def table(s, border=1, style=""):
    return "<table border=\'{}\' style=\'{}\'>".format(border, style) + s + "</table>"
def th(s):
    return "<th>" + s + "</th>"
def tr(s):
    return "<tr>" + s + "</tr>"
def td(s):
    return "<td>" + str(s) + "</td>"

def style_color(s, color='blue'):
    return "<span style='color:{}'>".format(color) + str(s) + "</span>"


def get_signin_info(channel, user):
    global CONFIG
    signin_info = {}
    conn = sqlite3.connect(CONFIG['db'])
    signins = pd.read_sql_query("select 1 from signin where user=? and channel=?", conn, params=(user.lower(), channel))
    count = len(signins)
    last_signin = pd.read_sql_query("select ts_day from signin where user=? and channel=? order by ts_day desc limit 1", conn, params=(user.lower(), channel))

    signin_info = {
        'count': count,
        'last_date': '{}'.format(time.strftime("%Y-%m-%d", time.gmtime(last_signin['ts_day'] + 8 * 3600))),
        'last_date_ts_utc': last_signin['ts_day'],
    }
    conn.close()
    return signin_info

def get_signin_stats(channel, user):
    signin_info = get_signin_info(channel, user)
    html_str = []
    welcome_str = "Hi!  ㄈ{} 已經累積簽到 {} 次，阿不就好棒棒(́◉◞౪◟◉‵)".format(style_color(user, 'blue'), style_color(signin_info['count'], 'red'))
    welcome_str = h2(welcome_str)
    html_str.append(welcome_str)
    welcome_str = "最近一次簽到在 {} 也就是{}".format(signin_info['last_date'], _decode_human_date(signin_info['last_date_ts_utc']))
    welcome_str = h2(welcome_str)
    html_str.append(welcome_str)
    html_str = ''.join(html_str)
    return html_str

def _decode_human_date(ts_utc):
    last_date = datetime.utcfromtimestamp(ts_utc)
    now = datetime.utcnow()
    delta = now - last_date
    if delta.days == 0:
        return "今天"
    else:
        return " {} 天前".format(delta.days)
