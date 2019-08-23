from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import django
import re
import json
import hashlib
import os
import base64
import hmac
import time
import requests
from www import web_socket, api_process, GlobalVar, security


def get_md5(byte):
    return hashlib.md5(byte).hexdigest()


def api_get_byKey(request):
    result = {
        'msgType': 'get_player',
        'rank': 0,
        'ico': '',
        'success': 0
    }
    if request.GET:
        if 'key' in request.GET:
            Key = request.GET['key']
            check = api_process.process_getdata_by_key(Key)
            if not check:
                return api_process.get_json(result)
            result['success'] = 1
            result['rank'] = check[0][GlobalVar.sql_userdata_rank]
            result['ico'] = check[0][GlobalVar.sql_userdata_PlayerInfo]
            return api_process.get_json(result)
    return api_process.get_json(result)


def api_setmusic(request):
    result = {
        'msgType': 'set_music',
        'success': 0
    }
    if request.GET:
        if 'key' in request.GET and 'musicid' in request.GET:
            sec_key = request.GET['key']
            musicid = request.GET['musicid']
            if not web_socket.is_number(musicid):
                return api_process.get_json(result)
            check = api_process.process_getdata_by_key(sec_key)
            if not check:
                return api_process.get_json(result)
            if check[0][GlobalVar.sql_userdata_banned] == 1:
                return api_process.get_json(result)
            result['success'] = 1
            data_encode = check[0][GlobalVar.sql_userdata_data]
            data_decode = api_process.process_playerlist_decode(data_encode)
            data_decode['music'] = musicid
            data_encode = api_process.process_playerlist_encode(
                data_decode).decode(encoding='GBK')
            GlobalVar.runSQL(
                'update userdata set `data` = %s where `Key` = %s limit 1', (data_encode, sec_key))
    return api_process.get_json(result)


def api_get(request):
    result = {
        'msgType': 'get_player',
        'rank': 0,
        'info': {},
        'ico': '',
        'matchid': [],
        'banned': 0,
        'success': 0
    }
    if request.GET:
        if 'name' in request.GET:
            player_name = web_socket.htmlescape(request.GET['name'])
            check = GlobalVar.runSQL(
                'SELECT * FROM userdata WHERE `username` = %s LIMIT 1', player_name)
            if not check:
                return api_process.get_json(result)
            data_encode = check[0][GlobalVar.sql_userdata_data]
            data_decode = api_process.process_playerlist_decode(data_encode)
            result['info'] = data_decode
            result['banned'] = check[0][GlobalVar.sql_userdata_banned]
            result['success'] = 1
            result['rank'] = check[0][GlobalVar.sql_userdata_rank]
            result['ico'] = check[0][GlobalVar.sql_userdata_PlayerInfo]
            result['matchid'] = data_decode['matched']
            return api_process.get_json(result)
    return api_process.get_json(result)


def file_extension(patch):
    return os.path.splitext(patch)[1]


def check_file_name(file):
    name = file_extension(file.name)
    return name == '.jpg' or name == '.bmp' or name == '.gif' or name == '.png' or name == '.jpeg' or name == '.ico'


@csrf_exempt
def update_image(request):
    result = {
        'msgType': 'update_image',
        'image': '',
        'uFuck': 0,
        'success': 0
    }
    if request.method == 'POST':
        image_file = request.FILES.get('file', None)
        sec_key = request.POST['key']
        method = request.POST['method']
        check = api_process.process_getdata_by_key(sec_key)
        if not check:
            return api_process.get_json(result)
        if check[0][GlobalVar.sql_userdata_banned] == 1:
            return api_process.get_json(result)
        if method == 'room_ico' and check[0][GlobalVar.sql_userdata_roomid] == '0':
            return api_process.get_json(result)
        if image_file:
            if image_file.size > 2 * 1024 * 1024:
                result['uFuck'] = 1
                return api_process.get_json(result)
            if not check_file_name(image_file):
                result['uFuck'] = 2
                return api_process.get_json(result)
            if file_extension(image_file.name) == '.gif':
                extension = '.gif'
            else:
                extension = '.jpg'
            byte = image_file.read()
            if extension != '.gif':
                if not security.check_iamge(byte):
                    result['success'] = 0
                    result['uFuck'] = 3
                    return api_process.get_json(result)
            save_name = get_md5(byte) + extension
            result['image'] = save_name
            save_dir = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.realpath(__file__)))), 'static')
            save_dir = os.path.join(save_dir, 'images')
            if method == 'player_avater':
                save_dir = os.path.join(save_dir, 'players')
            elif method == 'room_ico':
                save_dir = os.path.join(save_dir, 'room')
            save_name = os.path.join(save_dir, save_name)
            result['success'] = 1
            if method == 'player_avater':
                GlobalVar.runSQL(
                    'UPDATE userdata SET `PlayerInfo` = %s WHERE `key` = %s LIMIT 1', (result['image'], sec_key))
            elif method == 'room_ico':
                roomid = check[0][GlobalVar.sql_userdata_roomid]
                roomlist = GlobalVar.runSQL(
                    'SELECT * FROM roomlist WHERE `RoomID` = %s limit 1', roomid)
                if not roomid:
                    return api_process.get_json(result)
                room_config_decode = api_process.process_playerlist_decode(
                    roomlist[0][GlobalVar.sql_roomlist_config])
                room_config_decode['ico'] = result['image']
                room_config_encode = api_process.process_playerlist_encode(
                    room_config_decode).decode(encoding='GBK')
                GlobalVar.runSQL(
                    'UPDATE roomlist SET `config` = %s WHERE `RoomID` = %s LIMIT 1', (room_config_encode, roomid))
                GlobalVar.runSQL(
                    'UPDATE userdata SET `roomconfig` = %s WHERE `Key` = %s LIMIT 1', (room_config_encode, sec_key))
            with open(save_name, 'wb') as file:
                file.write(byte)
            return api_process.get_json(result)
    return api_process.get_json(result)
