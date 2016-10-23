# -*- coding: utf-8 -*-
import sqlite3
import logging
import time
import json

with open('config.json') as fp:
    CONFIG = json.load(fp)

html_newline = '<br />'

def h1(s):
    return "<h1>" + s + "</h1>"
def h2(s):
    return "<h2>" + s + "</h2>"

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
        
    conn.close()

    def ul(s):
        return "<ul>" + s + "</ul>"
    def li(s):
        return "<li>" + s + "</li>"

    stream_list = []
    for _id in streams:
        l = [
            "遊戲: {}".format(streams[_id]['game']),
            "開始: {}".format(time.strftime("%Y-%m-%d %H:%M", time.gmtime(streams[_id]['created_at'] + 8 * 3600))),
            "結束: {}".format(time.strftime("%Y-%m-%d %H:%M", time.gmtime(streams[_id]['end_at'] + 8 * 3600))),
            "持續時間: {} 分鐘".format((streams[_id]['end_at'] - streams[_id]['created_at']) / 60),
            "平均觀看人數: {}".format(int(streams[_id]['avg_view_user'])),
            "不重複聊天人數: {}".format(streams[_id]['distinct_chat_user']),
            "每分鐘最多對話次數: {}".format(streams[_id]['max_chat_per_min']),
            "每分鐘平均對話次數: {:.1f}".format(streams[_id]['avg_chat_per_min']),
        ]
        tmp = "".join([li(s) for s in l])
        tmp = ul("stream id: {}".format(_id) + tmp)
        stream_list.append(tmp)

    msg = html_newline.join(stream_list)
    return h2(msg)
            
