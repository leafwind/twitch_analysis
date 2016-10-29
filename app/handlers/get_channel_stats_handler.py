# -*- coding: utf-8 -*-
import sqlite3
import logging
import time
import json
from collections import OrderedDict

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

def get_stats(channel):
    global CONFIG
    conn = sqlite3.connect(CONFIG['db'])
    c = conn.cursor()
    c.execute('''select id, game, created_at, end_at from stream where channel = \'{}\';'''.format(channel))
    result = c.fetchall()
    streams = {}
    now = int(time.time())
    for r in result:
        streams[r[0]] = {
            'game': r[1],
            'created_at': r[2],
            'end_at': r[3] if r[3] > 0 else now,
        }
    streams = OrderedDict(sorted(streams.items(), key=lambda t: t[1]["created_at"], reverse=True))
    for _id in streams:
        c.execute('''select avg(n_user) from channel_popularity where channel = \'{}\' and ts > {} and ts < {};'''.format(channel, streams[_id]['created_at'], streams[_id]['end_at']))
        result = c.fetchall()
        streams[_id]['avg_view_user'] = result[0][0]

        c.execute('''select count(distinct(user)) from chat where channel = \'{}\' and ts > {} and ts < {};'''.format(channel, streams[_id]['created_at'], streams[_id]['end_at']))
        result = c.fetchall()
        streams[_id]['distinct_chat_user'] = result[0][0]

        c.execute('''select max(c), avg(c) from (select ts/60 t, count(1) as c from chat where channel = \'{}\' and ts > {} and ts < {} group by ts/60) as tmp;'''.format(channel, streams[_id]['created_at'], streams[_id]['end_at']))
        result = c.fetchall()
        streams[_id]['max_chat_per_min'] = result[0][0]
        streams[_id]['avg_chat_per_min'] = result[0][1]

    c.execute('''select user, count(1) from chat where channel = \'{}\' group by user order by count(1) desc limit 10;'''.format(channel))
    result = c.fetchall()
    streams[_id]['top_chat_users'] = []
    for r in result:
        streams[_id]['top_chat_users'].append((r[0], r[1]))

    c.execute('''select msg, count(1) from chat where channel = \'{}\' group by msg order by count(1) desc limit 10;'''.format(channel))
    result = c.fetchall()
    streams[_id]['top_chat_msgs'] = []
    for r in result:
        streams[_id]['top_chat_msgs'].append((r[0], r[1]))
        
    conn.close()

    channel_html = []
    top_chat_users = ["{}: {}".format(u, c) for (u, c) in streams[_id]['top_chat_users']]
    top_chat_users = "".join([li(s) for s in top_chat_users])
    top_chat_users = ul("top_chat_users: " + top_chat_users)
    channel_html.append(top_chat_users)

    top_chat_msgs = ["{}: {}".format(m.encode('utf-8'), c) for (m, c) in streams[_id]['top_chat_msgs']]
    top_chat_msgs = "".join([li(s) for s in top_chat_msgs])
    top_chat_msgs = ul("top_chat_msgs: " + top_chat_msgs)
    channel_html.append(top_chat_msgs)

    stream_html = []
    stream_html.append(h1("最近實況記錄"))

    header = ["遊戲", "開始", "結束", "持續時間(min)", "平均觀看人數", "不重複聊天人數", "每分鐘最多對話次數", "每分鐘平均對話次數"]
    header = [th(h) for h in header]
    row = tr("".join(header))
    stream_html.append(row)

    for _id in streams:
        l = [
            "{}".format(streams[_id]['game']),
            "{}".format(time.strftime("%Y-%m-%d %H:%M", time.gmtime(streams[_id]['created_at'] + 8 * 3600))),
            "{}".format(time.strftime("%Y-%m-%d %H:%M", time.gmtime(streams[_id]['end_at'] + 8 * 3600))),
            "{}".format((streams[_id]['end_at'] - streams[_id]['created_at']) / 60),
            "{}".format(int(streams[_id]['avg_view_user'])),
            "{}".format(streams[_id]['distinct_chat_user']),
            "{}".format(streams[_id]['max_chat_per_min']),
            "{:.1f}".format(streams[_id]['avg_chat_per_min']),
        ]
        row = "".join([td(col) for col in l])
        row = tr(row)
        stream_html.append(row)
    stream_html = table("".join(stream_html), border=1, style="font-size:24px;")

    msg = html_newline.join(channel_html) + stream_html
    return h2(msg)
            
