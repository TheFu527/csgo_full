import requests
import json
import base64
import pymysql
import datetime
import re
import json
import hashlib
import os
import base64
import hmac
import time


def process_playerlist_decode(playerlist):
    return json.loads(base64.b64decode(playerlist).decode(encoding='GBK'))


def process_playerlist_encode(playerlist):
    return base64.b64encode(json.dumps(playerlist).encode(encoding='GBK'))


def runSQL(sql, param='ha4k1r1337huoji120'):
    # hahahahahaaha XD

    db = pymysql.connect(host='127.0.0.1', port=3306,
                         user='root', password='huoji120', db='test')
    cur = db.cursor()
    # SELECT
    # print(sql + str(param))
    if param != 'ha4k1r1337huoji120':
        cur.execute(sql, param)
    else:
        cur.execute(sql)
    if sql[0:6].upper() != 'SELECT':
        db.commit()
    db.close()
    return cur.fetchall()


list1 = {
    'ha4k1r': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'qz': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'wh': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'xyq': {
        'Rank': 100, 'ico': 'null', 'ready': True
    }
}
list2 = {
    'av': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'qz': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'xs': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'tg': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'lmm': {
        'Rank': 100, 'ico': 'null', 'ready': True
    }
}
list3 = {
    'az': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'gh': {
        'Rank': 100, 'ico': 'null', 'ready': True
    },
    'qw': {
        'Rank': 100, 'ico': 'null', 'ready': True
    }
}
list4 = {
    'aoqsjhf': {
        'Rank': 100, 'ico': 'null', 'ready': True
    }
}
list2.pop('av')
print(list2)

list1_encode = process_playerlist_encode(list1).decode(encoding='GBK')
list2_encode = process_playerlist_encode(list2).decode(encoding='GBK')
list3_encode = process_playerlist_encode(list3).decode(encoding='GBK')
list4_encode = process_playerlist_encode(list4).decode(encoding='GBK')

config = {
    'ico': 'default.jpg',
    'title': '菜鸡房间',
    'text': '这个人是菜鸡,因为他的房间还是默认的标题和内容!',
    'maps': ['de_dust2', 'de_nuke', 'de_mirage', 'de_overpass', 'de_cache', 'de_inferno', 'de_train', 'de_cbble'],
    'public': 1
}
config_encode = process_playerlist_encode(config).decode(encoding='GBK')
data = {
    'kill': 10,
    'dead': 20,
    'first': 5,
    'headshot': 8,
    'help': 1,
    'music': 39227624,
    'autoplay': 1,
    'matched': ['80b893ee3e1ca307756277b5fe5098db'],
    'rank': {},
    'ico': 'null'
}
data_encode = process_playerlist_encode(data).decode(encoding='GBK')
print(data_encode)

team_red = ['test1_red']
team_blue = ['test2_blue']
red_players = ['test888', 'huoji', 'qz', 'aj', 'aw']
blue_players = ['qwrssa', 'jhdcxvq', 'htwd', 'cvqe', 'agqsds']
team_red_encode = process_playerlist_encode(
    team_red).decode(encoding='GBK')
team_blue_encode = process_playerlist_encode(
    team_blue).decode(encoding='GBK')
team_red_players_encode = process_playerlist_encode(
    red_players).decode(encoding='GBK')
team_blue_players_encode = process_playerlist_encode(
    blue_players).decode(encoding='GBK')

# requests.packages.urllib3.disable_warnings()
url = 'https://steamcommunity.com/openid/login'
proxie = {'http': 'socks5://localhost:1080',
          'https': 'socks5://localhost:1080'}

# request = requests.get(url, proxies=proxie, verify=False)
# print(request.text)
# runSQL(
#    'INSERT INTO matching (`matchid`,`team_red`,`team_blue`,`team_red_players`,`team_blue_players`,`serverid`,`map`,`uptime`) VALUES (%s,%s,%s,%s,%s,%s,%s,now())', (
#        'test',
#        team_red_encode,
#        team_blue_encode,
#        team_red_players_encode,
#        team_blue_players_encode,
#        'test2',
#        'de_cache'
#    ))
# print(process_playerlist_encode(config).decode(encoding='GBK'))
# runSQL(
#    'INSERT INTO roomlist (`RoomID`,`ingame`,`PlayerNumber`,`ReadyNumber`,`PlayerList`,`Rank`,`StartSearch`,`config`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
#    ('list1', 0, 4, 4, list1_encode, 100, 1, config_encode))
# runSQL(
#    'INSERT INTO roomlist (`RoomID`,`ingame`,`PlayerNumber`,`ReadyNumber`,`PlayerList`,`Rank`,`StartSearch`,`config`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
#    ('list2', 0, 5, 5, list2_encode, 100, 1, config_encode))
# runSQL(
#    'INSERT INTO roomlist (`RoomID`,`ingame`,`PlayerNumber`,`ReadyNumber`,`PlayerList`,`Rank`,`StartSearch`,`config`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
#    ('list3', 0, 3, 3, list3_encode, 100, 1, config_encode))
# runSQL(
#    'INSERT INTO roomlist (`RoomID`,`ingame`,`PlayerNumber`,`ReadyNumber`,`PlayerList`,`Rank`,`StartSearch`,`config`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
#    ('list4', 0, 1, 1, list4_encode, 100, 1, config_encode))
SINA_SECRETKEY = 'j312zz53xxkz24wz5lj0lxk41x4150ih4z510xk3'
SINA_ACCESSKEY = '3yz0zwwmnz'
TIMESTAMP = str(int(time.time()))
signature = ''
HEADERS = {
    'x-sae-accesskey': SINA_ACCESSKEY,
    'x-sae-timestamp': TIMESTAMP,
    'Authorization': signature
}
msgToSign = "\n".join(["GET", "/log/http/2015-06-05/1-access.log HTTP/1.1",
                       "\n".join([(k + ":" + v)for k, v in sorted(HEADERS) if k.startswith('x-sae-')])])
signature = "SAEV1_HMAC_SHA256 " + \
    base64.b64encode(hmac.new(SINA_SECRETKEY.encode(encoding='GBK'), msgToSign,
                              hashlib.sha256).digest()).decode(encoding='GBK')

print(signature)
