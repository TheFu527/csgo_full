#!/usr/bin/python
# -*- coding: utf-8 -*-
from enum import Enum, unique
import pymysql
import redis

sql_userdata_id = 0
sql_userdata_username = 1
sql_userdata_password = 2
sql_userdata_email = 3
sql_userdata_Key = 4
sql_userdata_SteamID = 5
sql_userdata_matching = 6
sql_userdata_roomid = 7
sql_userdata_PlayerInfo = 8
sql_userdata_LastActivityTime = 9
sql_userdata_rank = 10
sql_userdata_Online = 11
sql_userdata_roomconfig = 12
sql_userdata_banned = 13
sql_userdata_data = 14
sql_userdata_match_ban = 15


sql_roomlist_RoomID = 0
sql_roomlist_PlayerList = 1
sql_roomlist_StartSearch = 2
sql_roomlist_SearchTime = 3
sql_roomlist_ingame = 4
sql_roomlist_PlayerNumber = 5
sql_roomlist_ReadyNumber = 6
sql_roomlist_Rank = 7
sql_roomlist_config = 8
sql_roomlist_public = 9

sql_searchlist_RoomID = 0
sql_searchlist_PlayerList = 1
sql_searchlist_Rank = 2
sql_searchlist_PlayerNumber = 3
sql_searchlist_Time = 4

sql_matchserver_serverID = 0
sql_matchserver_location = 1
sql_matchserver_group = 2
sql_matchserver_matching = 3
sql_matchserver_ip = 4
sql_matchserver_port = 5

sql_matching_matchid = 0
sql_matching_team_red = 1
sql_matching_team_blue = 2
sql_matching_team_red_status = 3
sql_matching_team_blue_status = 4
sql_matching_hvh = 5
sql_matching_team_red_players = 6
sql_matching_team_blue_players = 7
sql_matching_serverid = 8
sql_matching_map = 9
sql_matching_uptime = 10
sql_matching_connectinfo = 11


sql_casualservers_serverid = 0
sql_casualservers_hostname = 1
sql_casualservers_ip = 2
sql_casualservers_port = 3
sql_casualservers_type = 4

sql_matched_matchid = 0
sql_matched_red_team_player = 1
sql_matched_blue_team_player = 2
sql_matched_red_team_score = 3
sql_matched_blue_team_score = 4
sql_matched_cheater = 5
sql_matched_serverid = 6
sql_matched_demoid = 7
sql_matched_time = 8
sql_matched_map = 9

sql_invitecode_code = 0
sql_invitecode_used = 1
sql_invitecode_name = 2


def _init():
    global _global_dict
    _global_dict = {}


def set_value(name, value):
    _global_dict[name] = value


def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue


def runSQL(sql, param='你是个好人'):
    # 来源于真实的作者悲伤经历.
    db = pymysql.connect(host=get_value('g_mysql_ip'), port=get_value('g_mysql_port'),
                         user=get_value('g_mysql_user'), password=get_value('g_mysql_password'), db=get_value('g_mysql_database'))
    cur = db.cursor()
    if param != '你是个好人':
        cur.execute(sql, param)
    else:
        cur.execute(sql)
    if sql[0:6].upper() != 'SELECT':
        db.commit()
    db.close()
    return cur.fetchall()
