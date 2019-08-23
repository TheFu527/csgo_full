from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import django
import re
import json
import hashlib
import os
import datetime
from . import web_socket, api_process, GlobalVar, elo
ELO_RESULT_WIN = 1
ELO_RESULT_LOSS = -1
ELO_RESULT_TIE = 0


def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def strtodatetime(datestr,format):      
    return datetime.datetime.strptime(datestr, format)
    
def datediff(beginDate, endDate):
    format = "%Y-%m-%d"
    bd = strtodatetime(beginDate, format)
    ed = strtodatetime(endDate, format)
    oneday = datetime.timedelta(days=1)
    count = 0
    while bd != ed:
        ed = ed-oneday
        count += 1
    return count

def get_player_by_username(name):
    check = GlobalVar.runSQL(
        'SELECT * from userdata where `username` = %s limit 1', name)
    if not check:
        return 0
    return check[0]


def get_rank(rank, max_rank, win_or_lost):
    eloscore = elo.EloScore()
    k = eloscore.computeK(rank)
    EA = eloscore.computeScore(rank, max_rank)
    new_rank = eloscore.getNewScore(rank, k, win_or_lost, EA)
    return int(new_rank)


def get_data(userdata):
    data_encode = userdata[GlobalVar.sql_userdata_data]
    return api_process.process_playerlist_decode(data_encode)


def appen_data(data_decode, key):
    data_encode = api_process.process_playerlist_encode(
        data_decode).decode(encoding='GBK')
    GlobalVar.runSQL(
        'update userdata set `data` = %s where `Key` = %s limit 1', (data_encode, key))


def playerdata_process_rank(userdata, rank):
    data_decode = get_data(userdata)
    tmp = []
    for key in data_decode['rank']:
        now = str(datetime.date.today())
        diff = datediff(key, now)
        if diff > 10:
            tmp.append(key)
    if not tmp:
        for index in range(len(tmp)):
            key = tmp[index]
            data_decode['rank'].pop(key)
    data_decode['rank'][str(datetime.date.today())] = rank
    appen_data(data_decode, userdata[GlobalVar.sql_userdata_Key])

def playerdata_process(userdata, matchid):
    data_decode = get_data(userdata)
    data_decode['matched'].insert(0, matchid)
    appen_data(data_decode, userdata[GlobalVar.sql_userdata_Key])

def playerdata_process_data(userdata, kill, dead, first, headshot, help):
    data_decode = get_data(userdata)
    data_decode['kill'] += int(kill)
    data_decode['dead'] += int(dead)
    data_decode['first'] += int(first)
    data_decode['headshot'] += int(headshot)
    data_decode['help'] += int(help)
    
    appen_data(data_decode, userdata[GlobalVar.sql_userdata_Key])


def get_matched_info(request):
    result = {
        'msgType': 'match_info',
        'matchid':'',
        'red_team_player': [],
        'blue_team_player': [],
        'red_team_score': 0,
        'blue_team_score': 0,
        'cheater': [],
        'time': '',
        'demoid': '',
        'server_location':'',
        'success': 0
    }
    if request.GET:
        if 'matchid' in request.GET:
            matchid = request.GET['matchid']
            match = GlobalVar.runSQL('SELECT * FROM matched WHERE `matchid` = %s LIMIT 1',matchid)
            if not match:
                return api_process.get_json(result)
            server_location = ''
            server_info = GlobalVar.runSQL(
                'SELECT * FROM matchserver WHERE `serverID` = %s LIMIT 1', match[0][GlobalVar.sql_matched_serverid])
            if not server_info:
                server_location = '广西'
            else:
                server_location = server_info[0][GlobalVar.sql_matchserver_location]
            red_team_player = api_process.process_playerlist_decode(
                match[0][GlobalVar.sql_matched_red_team_player])
            blue_team_player = api_process.process_playerlist_decode(
                match[0][GlobalVar.sql_matched_blue_team_player])
            result['matchid'] = match[0][GlobalVar.sql_matched_matchid]
            result['red_team_player'] =red_team_player
            result['blue_team_player'] =blue_team_player
            result['red_team_score'] = match[0][GlobalVar.sql_matched_red_team_score]
            result['blue_team_score'] = match[0][GlobalVar.sql_matched_blue_team_score]
            result['cheater'] = match[0][GlobalVar.sql_matched_cheater]
            result['time'] = str(match[0][GlobalVar.sql_matched_time])
            result['demoid'] = match[0][GlobalVar.sql_matched_demoid]
            result['map'] = match[0][GlobalVar.sql_matched_map]
            result['server_location'] = server_location
            result['success'] = 1
    return api_process.get_json(result)
def main(request):
    result = {
        'msgType': 'huoji',
        'uFuck': 0,
        'steamid': '',
        'team': 6,
        'index': 0,
        'map': '',
        'players':[],
        'red_team_steamid': [],
        'blue_team_steamid': [],
        'success': 0
    }
    if request.GET:
        if 'request' in request.GET:
            msgType = request.GET['request']
            secKey = request.GET['key']
            serverid = request.GET['serverid']
            steamid = ''
            if 'steamid' in request.GET:
                steamid = request.GET['steamid']
                result['steamid'] = steamid
            if 'client' in request.GET:
                result['index'] = request.GET['client']
            if not secKey == GlobalVar.get_value('g_server_seckey'):
                return api_process.get_json(result)
            check = GlobalVar.runSQL(
                'SELECT * FROM matching WHERE `serverid` = %s LIMIT 1', (serverid))
            if not check:
                result['success'] = 0
                return api_process.get_json(result)
            GlobalVar.runSQL(
                'UPDATE matching SET `uptime` = now() WHERE `serverid` = %s LIMIT 1', (serverid))
            red_team_player_encode = check[0][GlobalVar.sql_matching_team_red_players]
            blue_team_player_encode = check[0][GlobalVar.sql_matching_team_blue_players]
            red_players = api_process.process_playerlist_decode(
                red_team_player_encode)
            blue_players = api_process.process_playerlist_decode(
                blue_team_player_encode)
            connectinfo = check[0][GlobalVar.sql_matching_connectinfo]
            connectinfo_decode = api_process.process_playerlist_decode(
                connectinfo)
            if msgType == 'smac_ban':
                result['msgType'] = 'smac_ban'      
                #player = api_process.get_by_steamid(steamid)
                #if not player: 
                #    return api_process.get_json(result)
                result['success'] = 1
                GlobalVar.runSQL(
                    'update userdata set `banned` = 1 where `SteamID` = %s limit 1', steamid)
                return api_process.get_json(result)
            if msgType == 'ban_player':
                result['msgType'] = 'ban_player'
                result['success'] = 1
                array_unconnect = connectinfo_decode['unconnect']
                if not steamid in array_unconnect:
                    return api_process.get_json(result)
                time_now = datetime_toString(datetime.datetime.now())
                GlobalVar.runSQL(
                    'update userdata set `match_ban` = %s where `SteamID` = %s limit 1', (str(time_now), steamid))
                return api_process.get_json(result)
            if msgType == 'start_match':
                all_players = blue_players + red_players
                result['msgType'] = 'start_match'
                result['success'] = 1
                result['map'] = check[0][GlobalVar.sql_matching_map]
                result['players'] = all_players
                red_steamid = []
                blue_steamid = []
                for index in range(len(red_players)):
                    player = get_player_by_username(red_players[index])
                    red_steamid.append(player[GlobalVar.sql_userdata_SteamID])
                for index in range(len(blue_players)):
                    player = get_player_by_username(blue_players[index])
                    blue_steamid.append(player[GlobalVar.sql_userdata_SteamID])
                result['red_team_steamid'] = red_steamid
                result['blue_team_steamid'] = blue_steamid
                # print(result)
                return api_process.get_json(result)
            if msgType == 'add_connect':
                result['msgType'] = 'add_connect'
                result['success'] = 1
                array = connectinfo_decode['connected']
                array_unconnect = connectinfo_decode['unconnect']
                if not steamid in array_unconnect:
                    return api_process.get_json(result)
                if steamid in array:
                    return api_process.get_json(result)
                array.append(steamid)
                array_unconnect.remove(steamid)
                connectinfo_decode['connected'] = array
                connectinfo_decode['unconnect'] = array_unconnect
                connectinfo_encode = api_process.process_playerlist_encode(
                    connectinfo_decode).decode(encoding='GBK')
                GlobalVar.runSQL(
                    'UPDATE matching SET `connectinfo` = %s WHERE `serverid` = %s LIMIT 1', (connectinfo_encode, serverid))
                return api_process.get_json(result)
            if msgType == 'del_connect':
                result['msgType'] = 'del_connect'
                result['success'] = 1
                array = connectinfo_decode['connected']
                array_unconnect = connectinfo_decode['unconnect']
                if not steamid in array:
                    return api_process.get_json(result)
                if steamid in array_unconnect:
                    return api_process.get_json(result)
                array.remove(steamid)
                array_unconnect.append(steamid)
                connectinfo_decode['connected'] = array
                connectinfo_decode['unconnect'] = array_unconnect
                connectinfo_encode = api_process.process_playerlist_encode(
                    connectinfo_decode).decode(encoding='GBK')
                GlobalVar.runSQL(
                    'UPDATE matching SET `connectinfo` = %s WHERE `serverid` = %s LIMIT 1', (connectinfo_encode, serverid))
                return api_process.get_json(result)
            if msgType == 'post_finish':
                matchid = check[0][GlobalVar.sql_matching_matchid]
                map = check[0][GlobalVar.sql_matching_map]
                result['msgType'] = 'post_finish'
                result['success'] = 1
                # 1 完成了 0 没有开起来
                status = request.GET['status']
                red_team_score = 0
                blue_team_score = 0
                team_blue_roomid = api_process.process_playerlist_decode(
                    check[0][GlobalVar.sql_matching_team_blue])
                team_red_roomid = api_process.process_playerlist_decode(
                    check[0][GlobalVar.sql_matching_team_red])
                all_roomid = team_blue_roomid + team_red_roomid
                if status != 0 and 'red' in request.GET:
                    win_team = []
                    lost_team = []  
                    max_rank = 0
                    red_team_score = request.GET['red']
                    blue_team_score = request.GET['blue']
                    # 0平局 1 red 2 blue
                    winner = 0
                    win_team_list = {
                        #    'playername': {
                        #        'rank': 0
                        #    }
                    }
                    lost_team_list = {}
                    if red_team_score > blue_team_score:
                        winner = 1
                        win_team = red_players
                        lost_team = blue_players
                    elif red_team_score < blue_team_score:
                        winner = 2
                        win_team = blue_players
                        lost_team = red_players
                    else:
                        win_team = red_players + blue_players
                        max_rank = 9999
                        lost_team = []
                    for index in range(len(win_team)):
                        player = get_player_by_username(win_team[index])
                        playerdata_process(player, matchid)
                        rank = player[GlobalVar.sql_userdata_rank]
                        win_team_list[win_team[index]] = {'rank': rank}
                        if winner == 0:
                            if rank < max_rank and rank != 0:
                                max_rank = rank
                        roomid = player[GlobalVar.sql_userdata_roomid]
                    if winner != 0:
                        for index in range(len(lost_team)):
                            player = get_player_by_username(lost_team[index])
                            playerdata_process(player, matchid)
                            rank = player[GlobalVar.sql_userdata_rank]
                            lost_team_list[lost_team[index]] = {'rank': rank}
                            if rank > max_rank:
                                max_rank = rank
                            roomid = player[GlobalVar.sql_userdata_roomid]
                    for name in win_team_list:
                        win_or_lost = 0
                        if winner != 0:
                            win_or_lost = ELO_RESULT_WIN
                        rank = win_team_list[name]['rank']
                        new_rank_int = get_rank(rank, max_rank, win_or_lost)
                        playerdata_process_rank(
                            get_player_by_username(name), new_rank_int)
                        GlobalVar.runSQL(
                            'update userdata set `rank` = %s where `username` = %s limit 1', (new_rank_int, name))
                    if winner != 0:
                        for name in lost_team_list:
                            rank = lost_team_list[name]['rank']
                            win_or_lost = ELO_RESULT_LOSS
                            new_rank_int = get_rank(
                                rank, max_rank, win_or_lost)
                            playerdata_process_rank(
                                get_player_by_username(name), new_rank_int)
                            if new_rank_int <= 100:
                                new_rank_int = 100
                            GlobalVar.runSQL(
                                'update userdata set `rank` = %s where `username` = %s limit 1', (new_rank_int, name))
                    #这部分有点乱,以后要重构.
                    demoid = '暂无demo'
                    GlobalVar.runSQL(
                        'INSERT INTO matched (`matchid`,`red_team_player`,`blue_team_player`,`red_team_score`,`blue_team_score`,`serverid`,`demoid`,`time`,`map`) VALUES (%s,%s,%s,%s,%s,%s,%s,now(),%s)',
                        (matchid, red_team_player_encode, blue_team_player_encode, red_team_score, blue_team_score, serverid, demoid,map))
                    GlobalVar.runSQL(
                        'delete from matching where `matchid` = %s limit 1', matchid)
                else:
                    array = connectinfo_decode['unconnect']
                    time_now = datetime_toString(datetime.datetime.now())
                    for index in range(len(array)):
                        steamid = array[index]
                        GlobalVar.runSQL(
                            'update userdata set `match_ban` = %s where `SteamID` = %s limit 1', (str(time_now), steamid))
                for index in range(len(all_roomid)):
                    web_socket.send_match_was_finish(all_roomid[index])
                GlobalVar.runSQL(
                    'update matchserver set `matching` = 0 where `serverID` = %s limit 1', serverid)
                result['success'] = 1
                return api_process.get_json(result)
            if msgType == 'auth_connect':
                result['msgType'] = 'auth_request'
                player = api_process.get_by_steamid(steamid)
                if not player:
                    return api_process.get_json(result)
                player_name = player[0][GlobalVar.sql_userdata_username]
                result['success'] = 1
                if player_name in red_players:
                    result['team'] = 1
                    return api_process.get_json(result)
                elif player_name in blue_players:
                    result['team'] = 2
                    return api_process.get_json(result)
                else:
                    result['success'] = 0
                    return api_process.get_json(result)
            if msgType == 'push_score':
                result['success'] = 1
                result['msgType'] = 'push_score'
                if 'red' in request.GET and 'blue' in request.GET:
                    red_team_score = request.GET['red']
                    blue_team_score = request.GET['blue']
                    GlobalVar.runSQL(
                        'update matching set `team_red_status` = %s,`team_blue_status` = %s where `serverid` = %s limit 1', (red_team_score, blue_team_score, serverid))
                    return api_process.get_json(result)
            if msgType == 'push_data':
                result['msgType'] = 'push_data'
                player = api_process.get_by_steamid(steamid)
                if not player or not 'kill' in request.GET or not 'dead' in request.GET:
                    return api_process.get_json(result)
                kill = request.GET['kill']
                dead = request.GET['dead']
                help = request.GET['help']
                firstshot = request.GET['firstshot']
                headshot = request.GET['headshot']
                player_data = player[0]
                playerdata_process_data(
                    player_data, kill, dead, firstshot, headshot, help)
                result['success'] = 1
                return api_process.get_json(result)
            if msgType == 'ping':
                result['msgType'] = 'pong'
                result['success'] = 1
                return api_process.get_json(result)
    return api_process.get_json(result)
