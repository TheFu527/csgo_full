from django.http import HttpResponse
from django.shortcuts import render, redirect
from channels.generic.websocket import WebsocketConsumer
import platform
import django
import re
import json
import hashlib
import random
import base64
import time
import datetime
from . import GlobalVar
from . import api_process as api


def check_in_game(obj_room):
    return obj_room[0][GlobalVar.sql_roomlist_ingame] == 1


def check_in_search(obj_room):
    return obj_room[0][GlobalVar.sql_roomlist_StartSearch] == 1


def stop_search(roomid):
    # 暂时设置roomlist的，后面还要设置搜索池的以及判断是否在游戏里面的
    room = GlobalVar.runSQL(
        'SELECT * FROM roomlist WHERE `RoomID` = %s LIMIT 1', (roomid))
    if not room:
        return False
    if room[0][GlobalVar.sql_roomlist_ingame] == 1:
        return False
    if room[0][GlobalVar.sql_roomlist_StartSearch] == 0:
        return False
    GlobalVar.runSQL(
        "UPDATE roomlist SET `StartSearch` = 0,`SearchTime`= 0 WHERE `RoomID` = %s LIMIT 1", roomid)
    # GlobalVar.runSQL(
    #    "DELETE FROM searchlist WHERE `RoomID` = %s LIMIT 1", roomid)
    return True

# 实际上应该是do_ready


def do_ready(request, json_data, roomlist, userdata):
    json_data['msgType'] = 'do_ready'
    json_data['success'] = 0
    room_id = roomlist[0][GlobalVar.sql_roomlist_RoomID]
    # GlobalVar.runSQL(
    #    "UPDATE roomlist SET `StartSearch` = %s WHERE `RoomID` = %s LIMIT 1", (1, room_id))
    if check_in_game(roomlist):
        json_data['success'] = 1
        json_data['uFuck'] = 2
        return json.dumps(json_data)
    player_list = roomlist[0][GlobalVar.sql_roomlist_PlayerList]
    ready_number = roomlist[0][GlobalVar.sql_roomlist_ReadyNumber]
    player_list_decode = api.process_playerlist_decode(player_list)
    player_name = userdata[0][GlobalVar.sql_userdata_username]
    if not player_list_decode[player_name]:
        return json.dumps(json_data)
    player_list_decode[player_name]['ready'] = not player_list_decode[player_name]['ready']
    # 同步准备人数和玩家人数
    ready_number = 0
    player_number = 0
    for key in player_list_decode:
        player_number += 1
        if player_list_decode[key]['ready']:
            ready_number += 1
    json_data['is_search'] = 0
    if ready_number != player_number:
        stop_search(room_id)
    else:
        json_data['is_search'] = 1
    player_list_encode = api.process_playerlist_encode(
        player_list_decode).decode(encoding='GBK')
    GlobalVar.runSQL(
        "UPDATE roomlist SET `PlayerList` = %s,`PlayerNumber`=%s,`ReadyNumber`=%s,`StartSearch`=%s WHERE `RoomID` = %s LIMIT 1",
        (player_list_encode, player_number, ready_number, json_data['is_search'], room_id))

    json_data['success'] = 1
    json_data['uFuck'] = 0

    # 推送的事情交给线程去干
    # if roomlist[0][GlobalVar.sql_roomlist_PlayerNumber] == roomlist[0][GlobalVar.sql_roomlist_ReadyNumber]:
    #time_tick = str(time.time()).replace('.', '')
    # GlobalVar.runSQL(
    #    'INSERT INTO searchlist (`RoomID`,`Time`) VALUES (%s,%s)', (room_id, time_tick))
    #json_data['success'] = 1
    #json_data['uFuck'] = 0
    return json.dumps(json_data)
