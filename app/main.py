from flask import Flask
from flask import request
from flask import jsonify
import logging
import requests
import json
import time
import calendar

from handlers.get_channel_stats_handler import get_stats, get_signin_ranking
from handlers.get_signin_stats_handler import get_signin_stats

application = Flask(__name__)
application.config['PROPAGATE_EXCEPTIONS'] = True

logging.basicConfig(filename='error.log',level=logging.DEBUG)

with open('config.json') as fp:
    CONFIG = json.load(fp)
client_id = CONFIG["client_id"]

@application.route("/")
def hello():
    return "<h1 style='color:red'>Hello There!</h1>"


## set the project root directory as the static folder, you can set others.
#app = Flask(__name__, static_url_path='')
#@application.route('/js/<path:path>')
#def send_js(path):
#    return send_from_directory('js', path)

def h1(s):
    return "<h1>{}</h1>".format(s)

@application.route('/signin_ranking/<channel>')
def get_signin_ranking_handler(channel):
    result = get_signin_ranking(channel)
    return result


@application.route('/signin', methods=['GET'])
def _get_signin_status_hanlder():
    user = request.args.get('user')
    channel = request.args.get('channel')
    result = get_signin_stats(channel, user, html=False)
    return jsonify(result)

@application.route('/signin/<channel>/<user>')
def get_signin_status_hanlder(channel, user):
    result = get_signin_stats(channel, user, html=True)
    return result

@application.route('/follow/<channel>/<user>')
def follow_status(channel, user):
    global client_id
    url = 'https://api.twitch.tv/kraken/users/{}/follows/channels/{}'.format(user, channel)
    headers = {'Accept': 'application/vnd.twitchtv.v3+json', 'Client-ID': client_id}
    r = requests.get(url, headers=headers)
    info = json.loads(r.text)
    if info.get('status', None) == 404:
        return h1("{} is not following {}".format(user, channel))
    else:
        since = time.strptime(info['created_at'], "%Y-%m-%dT%H:%M:%S+00:00")
        since_ts = calendar.timegm(since)
        now = time.gmtime(time.time())
        now_ts = calendar.timegm(now)
        diff_ts = now_ts - since_ts
        msg = "{} start following {} from <span style='color:red'>{}-{}-{}</span>, total <span style='color:blue'>{}</span> days".format(user, channel, since.tm_year, since.tm_mon, since.tm_mday, int(diff_ts / 86400))
        msg = h1(msg)
        return msg

@application.route('/<channel>/list_all_current_users')
def get_all_users(channel):
    from twitch_utils import get_current_users
    all_users = get_current_users(channel)
    msg = "<br />".join(all_users)
    msg = h1(msg)
    return msg

@application.route('/<channel>/stats')
def get_stats_handler(channel):
    result = get_stats(channel)
    return result

@application.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post %d' % post_id


#if __name__ == "__main__":
#    application.run(host='0.0.0.0')
