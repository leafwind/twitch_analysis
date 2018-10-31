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
    return "<td>" + s + "</td>"

def style_color(s, color='blue'):
    return "<span style='color:{}'>".format(color) + s + "</span>"


def get_stream_info(channel, n_top_chatters, n_top_msgs):
    global CONFIG
    stream_info = {}
    conn = sqlite3.connect(CONFIG['db'])
    streams = pd.read_sql_query("select id, game, created_at, end_at from stream where channel =\'{}\' order by created_at desc".format(channel), conn)

    popularity = pd.read_sql_query("select n_user, ts from channel_popularity where channel = \'{}\'".format(channel), conn)
    chat = pd.read_sql_query("select user, msg, ts from chat where channel = \'{}\'".format(channel), conn)

    for index, stream in streams.iterrows():
        stream['end_at'] = stream['end_at'] if stream['end_at'] > 0 else int(time.time())
        p = popularity[(popularity.ts >= stream['created_at']) & (popularity.ts <= stream['end_at'])]
        c = chat[(chat.ts >= stream['created_at']) & (chat.ts <= stream['end_at'])]
        n_total_chat = c['user'].count()

        def group_by_min(df, ind, col):
            return int(df[col].loc[ind]/60)

        chat_groupby_min = c['ts'].groupby(lambda x: group_by_min(c, x, 'ts')).count()
        max_chat_by_min = chat_groupby_min.max()
        mean_chat_by_min = chat_groupby_min.mean()
        std_chat_by_min = chat_groupby_min.std()

        created_at = stream['created_at']
        end_at = stream['end_at']
        max_user = p['n_user'].max()
        mean_user = p['n_user'].mean()
        unique_chat_user = c['user'].nunique()

        chat_groupby_user = c[['user', 'ts']].groupby('user', as_index=False).count()
        top_chatters = chat_groupby_user.nlargest(n_top_chatters, columns='ts')['user'].tolist()
        top_chatters = ", ".join(top_chatters)
        top_chatters = top_chatters.encode('utf-8')
                    
        chat_groupby_msg = c[['msg', 'ts']].groupby('msg', as_index=False).count()
        top_msgs = chat_groupby_msg.nlargest(n_top_msgs, columns='ts')['msg'].tolist()
        top_msgs = ", ".join(top_msgs)
        top_msgs = top_msgs.encode('utf-8')

        stream_info[stream['id']] = {
            'game': stream['game'].encode('utf-8'),
            'created_at': '{}'.format(time.strftime("%Y-%m-%d %H:%M", time.gmtime(created_at + 8 * 3600))),
            'end_at': '{}'.format(time.strftime("%Y-%m-%d %H:%M", time.gmtime(end_at + 8 * 3600))),
            'duration_min': '{}'.format(int((end_at - created_at) / 60)),
            'n_total_chat': str(n_total_chat),
            'max_user': str(max_user),
            'mean_user': 'nan' if math.isnan(mean_user) else str(int(mean_user)),
            'unique_chat_user': str(unique_chat_user),
            'interactivity': '{:.0%}'.format(1.0 * unique_chat_user / max_user),
            'max_chat_by_min': str(max_chat_by_min),
            'mean_chat_by_min': '{:.1f}'.format(mean_chat_by_min),
            'cov_chat_by_min': '{:.0%}'.format(std_chat_by_min / mean_chat_by_min),
            'top_chatters': top_chatters,
            'top_msgs': top_msgs,
        }
        stream_info = OrderedDict(sorted(stream_info.items(), key=lambda t: t[1]["created_at"], reverse=True))
    conn.close()
    return stream_info


def get_signin_ranking(channel):
    global CONFIG
    stream_info = {}
    conn = sqlite3.connect(CONFIG['db'])
    result = pd.read_sql_query("select user, count(1) as count, strftime('%Y-%m-%d', datetime(max(ts_day), 'unixepoch')) as last_signin_date from signin where channel = \'{}\' group by user order by count(1) desc".format(channel), conn)

    header_translation = [
        ('user', '使用者'),
        ('count', '簽到次數'),
        ('last_signin_date', '最後簽到日期')
    ]

    html_str = []
    row = []
    for header in header_translation:
        row.append(th(header[1]))
    html_str.append(tr("".join(row)))
    for index, log in result.iterrows():
        row = []
        for header in header_translation:
            value = str(log[header[0]])
            row.append(td(value))
        html_str.append(tr("".join(row)))
    html_str = table("".join(html_str), border=1, style="font-size:24px;")
    return html_str

def get_stats(channel):
    header_translation = [
        ('game', '遊戲名稱'),
        ('created_at', '開始時間'),
        ('end_at', '結束時間'),
        ('duration_min', '實況時間(分)'),
        ('n_total_chat', '總發言數量'),
        ('mean_chat_by_min', '平均每分鐘發言'),
        ('max_chat_by_min', '最大每分鐘發言'),
        ('mean_user', '平均觀眾'),
        ('max_user', '最多同時觀眾'),
        ('unique_chat_user', '不重複發言觀眾'),
        ('interactivity', '互動比例(發言/全部觀眾)'),
        ('cov_chat_by_min', '觀眾情緒起伏指數'),
        ('top_chatters', '最常發言觀眾'),
        ('top_msgs', '最多重複訊息'),
    ]
    stream_info = get_stream_info(channel, n_top_chatters=5, n_top_msgs=10)

    html_str = []
    row = []
    for header in header_translation:
        row.append(th(header[1]))
    html_str.append(tr("".join(row)))
    for _id in stream_info:
        row = []
        for header in header_translation:
            row.append(td(stream_info[_id][header[0]]))
        html_str.append(tr("".join(row)))
    html_str = table("".join(html_str), border=1, style="font-size:24px;")
    return html_str

def whatisthis(s):
    if isinstance(s, str):
        print "ordinary string: {}".format(s)
    elif isinstance(s, unicode):
        print "unicode string: {}".format(s.encode('utf-8'))
    else:
        print "not a string"

