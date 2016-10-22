import requests

USERLIST_API = "http://tmi.twitch.tv/group/user/{}/chatters"
def get_current_users(ch, user_type='all'):
    url = USERLIST_API.format(ch)
    r = requests.get(url).json()
    if user_type == 'all':
        all_users = set(sum(r['chatters'].values(), []))
        return all_users
    elif user_type in ['moderators', 'staff', 'admins', 'global_mods', 'viewers']:
        users = set(r['chatters'][user_type])
        return users
    else:
        return set()
