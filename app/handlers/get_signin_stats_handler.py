# -*- coding: utf-8 -*-
import sqlite3
import numpy as np
import pandas as pd
import logging
import time
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
    signins = pd.read_sql_query("select ts_day from signin where user=? and channel=? order by ts_day asc", conn, params=(user, channel))

    for i, signin in signins.iterrows():
        signin_info[i] = {
            'index': i,
            'date': '{}'.format(time.strftime("%Y-%m-%d", time.gmtime(signin['ts_day'] + 8 * 3600))),
        }
        signin_info = OrderedDict(sorted(signin_info.items(), key=lambda t: t[1]["index"], reverse=True))
    conn.close()
    return signin_info

def get_signin_stats(channel, user):
    header_translation = [
        ('index', '流水號'),
        ('date', '日期'),
    ]
    signin_info = get_signin_info(channel, user)

    html_str = []
    welcome_str = "Hi!  ㄈ{} 已經累積簽到 {} 次，阿不就好棒棒(́◉◞౪◟◉‵)".format(style_color(user, 'blue'), style_color(len(signin_info), 'red'))
    welcome_str = h2(welcome_str)
    html_str.append(welcome_str)
    row = []
    for header in header_translation:
        row.append(th(header[1]))
    html_str.append(tr("".join(row)))
    for _id in signin_info:
        row = []
        for header in header_translation:
            row.append(td(signin_info[_id][header[0]]))
        html_str.append(tr("".join(row)))
    html_str = table("".join(html_str), border=1, style="font-size:24px;")
    return html_str


