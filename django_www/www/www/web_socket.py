from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import gevent
import platform
import django
import re
import json
import hashlib
import random
import base64
import time
import redis
import threading
import html
import unicodedata
import datetime
from . import GlobalVar, api_process, search_process


def string_toDatetime(st):
    return datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S")


def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def htmlescape(str):
    return (html.escape(str))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def websocket_add(key, values):
    tmp = GlobalVar.get_value('g_websocket_clients')
    if not values in tmp:
        tmp[key] = values
        GlobalVar.set_value('g_websocket_clients', tmp)


def websocket_del(key):
    tmp = GlobalVar.get_value('g_websocket_clients')
    if key in tmp:
        del tmp[key]
        GlobalVar.set_value('g_websocket_clients', tmp)


def websocket_find(sec_key):
    return GlobalVar.get_value('g_websocket_clients')[sec_key]


def send_player_leave_room(room_id, player_name):
    result = {
        'msgType': 'leave_room',
        'name': player_name,
        'roomid': room_id
    }
    json_encode = api_process.process_playerlist_encode(
        result).decode(encoding='GBK')
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_connect.publish('room', json_encode)


def send_match_was_finish(room_id):
    result = {
        'msgType': 'match_finifsh',
        'name': '',
        'roomid': room_id
    }
    json_encode = api_process.process_playerlist_encode(
        result).decode(encoding='GBK')
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_connect.publish('room', json_encode)


def send_player_join_room(room_id, player_name):
    result = {
        'msgType': 'join_room',
        'name': player_name,
        'roomid': room_id
    }

    json_encode = api_process.process_playerlist_encode(
        result).decode(encoding='GBK')
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_connect.publish('room', json_encode)


def send_player_ready(room_id, player_name):
    result = {
        'msgType': 'player_ready',
        'name': player_name,
        'roomid': room_id
    }
    json_encode = api_process.process_playerlist_encode(
        result).decode(encoding='GBK')
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_connect.publish('room', json_encode)

def send_match_server_crash(room_id):
    result = {
        'msgType': 'server_crash',
        'name': '',
        'roomid': room_id
    }
    json_encode = api_process.process_playerlist_encode(
        result).decode(encoding='GBK')
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_connect.publish('room', json_encode)

def get_players_by_id(roomid):
    result = {
        'msgType': 'get_room_player_number',
        'number': 0,
        'uFuck': 0,
        'success': 1
    }
    room = GlobalVar.runSQL(
        'SELECT * FROM roomlist WHERE `RoomID` = %s LIMIT 1', (roomid))
    if not room:
        result['uFuck'] = 1
        return json.dumps(result)
    number = room[0][GlobalVar.sql_roomlist_PlayerNumber]
    result['number'] = number
    return json.dumps(result)


def get_rand_roomlist():
    # 前端最多容得下12个
    result = {
        'msgType': 'get_rand_roomlist',
        'roomlist': 'null',
        'success': 1
    }
    all_room = GlobalVar.runSQL(
        'SELECT * FROM roomlist WHERE `StartSearch` = 0 AND `ingame` = 0 AND `PlayerNumber` < 5 AND `public` = 1')
    if not all_room:
        return json.dumps(result)

    room_infos = {
        # 'RoomID': {
        #    'players': 0,
        #    'ico': 'default.jpg',
        #    'title': 'title',
        #    'text': 'text',
        #    'maps': []
        # }
    }
    if len(all_room) <= 8:
        for index in range(len(all_room)):
            roomid = all_room[index][GlobalVar.sql_roomlist_RoomID]
            room_config_decode = api_process.process_playerlist_decode(
                all_room[index][GlobalVar.sql_roomlist_config])
            room_infos[roomid] = {
                'players': all_room[index][GlobalVar.sql_roomlist_PlayerNumber],
                'ico': room_config_decode['ico'],
                'title': room_config_decode['title'],
                'text': room_config_decode['text'],
                'maps': room_config_decode['maps']
            }
    else:
        rand_number = []
        raned_num = []
        for index in range(0, 8):
            rand = random.randint(0, len(all_room))
            while rand in raned_num:
                rand = random.randint(0, len(all_room))
            rand_number[index] = rand
            raned_num.append(rand_number[index])
        for rand in range(len(raned_num)):
            index = raned_num[rand]
            roomid = all_room[index][GlobalVar.sql_roomlist_RoomID]
            room_config_decode = api_process.process_playerlist_decode(
                all_room[index][GlobalVar.sql_roomlist_config])
            room_infos[roomid] = {
                'players': all_room[index][GlobalVar.sql_roomlist_PlayerNumber],
                'ico': room_config_decode['ico'],
                'title': room_config_decode['title'],
                'text': room_config_decode['text'],
                'maps': room_config_decode['maps']
            }

    result['roomlist'] = json.dumps(room_infos)
    return json.dumps(result)


def reflush_room_config(roomlist_data):
    result = {
        'msgType': 'reflush_room_config',
        'config': {},
        'public': 1,
        'success': 1
    }
    room_config_decode = api_process.process_playerlist_decode(
        roomlist_data[0][GlobalVar.sql_roomlist_config])
    result['config'] = json.dumps(room_config_decode)
    result['public'] = roomlist_data[0][GlobalVar.sql_roomlist_public]
    return json.dumps(result)


def map_sec_check(maps):
    know_maps = {'de_dust2': 1, 'de_inferno': 1, 'de_nuke': 1, 'de_mirage': 1,
                 'de_overpass': 1, 'de_cache': 1, 'de_train': 1, 'de_cbble': 1}
    for index in range(len(maps)):
        if not maps[index] in know_maps:
            return False
    return True


def checkmatchserver(matchid,roomid):
    result = {
        'msgType': 'heartbeat_match',
        'success': 1
    }
    if matchid == '':
        return json.dumps(result)
    check = GlobalVar.runSQL('SELECT * FROM matching WHERE `matchid` = %s limit 1', matchid)
    if not check:
        return json.dumps(result)
    start_time = check[0][GlobalVar.sql_matching_uptime]
    end_time = datetime.datetime.now()
    sec = (end_time - start_time).seconds
    if sec < 60:
        return json.dumps(result)
    else:
        serverid = check[0][GlobalVar.sql_matching_serverid]
        team_blue_roomid = api_process.process_playerlist_decode(check[0][GlobalVar.sql_matching_team_blue])
        team_red_roomid = api_process.process_playerlist_decode(check[0][GlobalVar.sql_matching_team_red])
        all_roomid = team_red_roomid + team_blue_roomid
        GlobalVar.runSQL("update matchserver set `matching` = 3  where `serverID` = %s limit 1", serverid)
        GlobalVar.runSQL("delete from matching where `matchid` = %s limit 1", matchid)
        for index in range(len(all_roomid)):  
            GlobalVar.runSQL(
                "update roomlist set `ingame` = 0 where `RoomID` = %s limit 1", all_roomid[index])
            send_match_server_crash(all_roomid[index])
        
        return json.dumps(result)

def get_match_info(roomid):
    result = {
        'msgType': 'get_match_infos',
        'ingame': 1,
        'matchid': '',
        'map': '',
        'serverid': '',
        'server_location': '',
        'team_blue_players': [],
        'team_red_players': [],
        'ipaddr': '',
        'port': 27015,
        'elo': '0',
        'success': 0
    }
    check = GlobalVar.runSQL(
        'SELECT * FROM userdata WHERE `roomid` = %s LIMIT 1', roomid)
    if not check:
        return json.dumps(result)
    matchid = check[0][GlobalVar.sql_userdata_matching]
    if matchid == '0':
        result['success'] = 1
        result['ingame'] = 0
        return json.dumps(result)
    check = GlobalVar.runSQL(
        'SELECT * FROM matching WHERE `matchid` = %s LIMIT 1', matchid)
    if not check:
        return json.dumps(result)
    result['success'] = 1
    result['matchid'] = matchid
    result['map'] = check[0][GlobalVar.sql_matching_map]
    result['serverid'] = check[0][GlobalVar.sql_matching_serverid]
    result['team_blue_players'] = check[0][GlobalVar.sql_matching_team_blue_players]
    result['team_red_players'] = check[0][GlobalVar.sql_matching_team_red_players]
    server_info = GlobalVar.runSQL(
        'SELECT * FROM matchserver WHERE `serverID` = %s LIMIT 1', result['serverid'])
    result['ipaddr'] = server_info[0][GlobalVar.sql_matchserver_ip]
    result['server_location'] = server_info[0][GlobalVar.sql_matchserver_location]
    result['port'] = server_info[0][GlobalVar.sql_matchserver_port]
    return json.dumps(result)


def up_room_info(data, roomlist_data, name):
    result = {
        'msgType': 'up_room_info',
        'name': name,
        'roomid': '',
        'success': 1
    }
    sec_key = data['key']
    result['roomid'] = roomlist_data[0][GlobalVar.sql_roomlist_RoomID]
    room_config_decode = api_process.process_playerlist_decode(
        roomlist_data[0][GlobalVar.sql_roomlist_config])
    if not map_sec_check(data['maps']):
        return
    if not data['maps']:
        return
    if not is_number(data['public']):
        return
    # 放长一点
    if len(data['title']) > 9 or len(data['text']) > 30:
        return
    # ico
    # public
    room_config_decode['title'] = htmlescape(data['title'])
    room_config_decode['text'] = htmlescape(data['text'])
    room_config_decode['maps'] = data['maps']
    room_config_decode['public'] = data['public']
    room_config_encode = api_process.process_playerlist_encode(
        room_config_decode).decode(encoding='GBK')
    GlobalVar.runSQL('UPDATE roomlist SET `config` = %s,`public` = %s WHERE `RoomID` = %s LIMIT 1',
                     (room_config_encode, data['public'], roomlist_data[0][GlobalVar.sql_roomlist_RoomID]))
    GlobalVar.runSQL(
        'UPDATE userdata SET `roomconfig` = %s WHERE `Key` = %s LIMIT 1', (room_config_encode, sec_key))
    json_encode = api_process.process_playerlist_encode(
        result).decode(encoding='GBK')
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_connect.publish('room', json.dumps(json_encode))
    return

def send_chat(text,roomid):
    result = {
        'msgType': 'send_chat',
        'success': 1
    }
    text_encode = htmlescape(text)
    result_push = {
        'msgType': 'chat_reve',
        'name': text_encode,
        'roomid': roomid,
        'success': 1
    }
    json_encode = api_process.process_playerlist_encode(
        result_push).decode(encoding='GBK')
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_connect.publish('room', json.dumps(json_encode))
    return json.dumps(result)

def redis_listen():
    redis_connect = GlobalVar.get_value('g_redis_server')
    redis_pubsub = redis_connect.pubsub()
    redis_pubsub.subscribe('room')
    for msg in redis_pubsub.listen():
        if msg['type'] == 'message':
            result = {
                'msgType': 'null',
                'name': 'null',
                'success': 1
            }
            try:
                json_decode = api_process.process_playerlist_decode(
                    msg['data'])
                result['msgType'] = json_decode['msgType']
                result['name'] = json_decode['name']
                check = GlobalVar.runSQL(
                    'SELECT * FROM userdata WHERE `roomid` = %s', json_decode['roomid'])
                if check:
                    for index in range(len(check)):
                        if json_decode['msgType'] == 'join_room' or json_decode['msgType'] == 'leave_room':
                            if check[index][GlobalVar.sql_userdata_username] == json_decode['name']:
                                continue
                        key = check[index][GlobalVar.sql_userdata_Key]
                        obj_websocket = websocket_find(key)
                        #if check[0][GlobalVar.sql_userdata_banned]:
                        #    return obj_websocket.close()
                        if obj_websocket:
                            obj_websocket.send(json.dumps(result))
                        if result['msgType'] == 'kick':
                            GlobalVar.runSQL(
                                "UPDATE userdata SET `roomid` = '0' WHERE `Key` = %s LIMIT 1", key)
            except:
                continue


class websocket_main(WebsocketConsumer):
    def connect(self):
        if not GlobalVar.get_value('g_init_redis'):
            threading.Thread(target=redis_listen, args=()).start()
            GlobalVar.set_value('g_init_redis', True)
        self.accept()

    def disconnect(self, close_code):
        try:
            if self.sec_key:
                api_process.process_exit_room(self.sec_key)
                websocket_del(self.sec_key)
        except:
            pass

    def receive(self, text_data):
        result = {
            'msgType': 'get_room_info',
            'uFuck': 1,
            'RoomID': 'NULL',
            'playerlist': 'NULL',
            'is_ingame': 0,
            'is_search': 0,
            'player_num': 0,
            'freezetime': 0,
            'success': 0
        }
        if text_data == 'ping':
            return self.send('pong')
        # 这里要加try
        if True:
            data = json.loads(text_data)
            if 'key' in data:
                sec_key = data['key']
                user_data = api_process.process_getdata_by_key(sec_key)
                if not user_data:
                    return self.send(json.dumps(result))
                if user_data[0][GlobalVar.sql_userdata_roomid] == '0':
                    return self.send(json.dumps(result))
                roomlist_data = GlobalVar.runSQL(
                    'SELECT * FROM roomlist WHERE `RoomID` = %s LIMIT 1', (user_data[0][GlobalVar.sql_userdata_roomid]))
                if not roomlist_data:
                    return self.send(json.dumps(result))
                if user_data[0][GlobalVar.sql_userdata_banned]:
                    result['success'] = 1
                    result['msgType'] = 'banned'
                    return self.send(json.dumps(result))
                self.sec_key = data['key']
                self.room_id = user_data[0][GlobalVar.sql_userdata_roomid]
                websocket_add(data['key'], self)
                username = user_data[0][GlobalVar.sql_userdata_username]
                if data['request'] == 'get_room_info':
                    result['success'] = 1
                    result['uFuck'] = 0
                    result['playerlist'] = roomlist_data[0][GlobalVar.sql_roomlist_PlayerList]
                    result['is_ingame'] = roomlist_data[0][GlobalVar.sql_roomlist_ingame]
                    result['is_search'] = roomlist_data[0][GlobalVar.sql_roomlist_StartSearch]
                    result['RoomID'] = user_data[0][GlobalVar.sql_userdata_roomid]
                    result['player_num'] = roomlist_data[0][GlobalVar.sql_roomlist_PlayerNumber]
                    return self.send(json.dumps(result))
                if data['request'] == 'room_do_ready':
                    result['playerlist'] = 'null'
                    ban_time = user_data[0][GlobalVar.sql_userdata_match_ban]
                    if ban_time != '0':
                        end_time = datetime.datetime.now()
                        start_time = string_toDatetime(ban_time)
                        sec = (end_time - start_time).seconds
                        if sec <= 1800:
                            result['msgType'] = 'do_ready'
                            result['success'] = 1
                            result['uFuck'] = 3
                            result['freezetime'] = 1800 - sec
                            return self.send(json.dumps(result))

                    self.send(search_process.do_ready(
                        self, data, roomlist_data, user_data))
                    return send_player_ready(user_data[0][GlobalVar.sql_userdata_roomid], username)
                if data['request'] == 'rand_get_room':
                    return self.send(get_rand_roomlist())
                if data['request'] == 'get_room_players_number':
                    return self.send(get_players_by_id(data['other']))
                if data['request'] == 'up_room_infos':
                    up_room_info(data, roomlist_data, username)
                    return
                if data['request'] == 'reflush_room_config':
                    return self.send(reflush_room_config(roomlist_data))
                if data['request'] == 'exit_room':
                    return self.disconnect(0)
                if data['request'] == 'getMatchInfo':
                    return self.send(get_match_info(self.room_id))
                if data['request'] == 'heartbeat_match':
                    return self.send(checkmatchserver(data['matchid'],self.room_id))
                if data['request'] == 'send_chat':
                    return self.send(send_chat(data['other'], self.room_id))
            return self.send(json.dumps(result))
        # except:
        #    return self.send(json.dumps(result))
