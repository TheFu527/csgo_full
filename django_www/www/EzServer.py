import re
import json
import hashlib
import random
import base64
import time
import redis
import _thread
import threading
import pymysql
#from www import GlobalVar

mysql_ip = '127.0.0.1'
mysql_port = 3306
mysql_user = 'root'
mysql_password = 'huoji120'
mysql_database = 'test'

redis_ip = '127.0.0.1'
redis_port = 6379
redis_password = 'huoji120'

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

sql_matchserver_serverID = 0
sql_matchserver_location = 1
sql_matchserver_group = 2
sql_matchserver_matching = 3
sql_matchserver_ip = 4
sql_matchserver_port = 5

search_range = 500
redis_server = redis.Redis(host=redis_ip, port=redis_port, password=redis_password)
match_map = 'huoji'

def hash_md5(str):
    return hashlib.md5(str).hexdigest()

def runSQL(sql, param='ha4k1r1337huoji120'):
    # hahahahahaaha XD
    db = pymysql.connect(host=mysql_ip, port=mysql_port, user=mysql_user,
                         password=mysql_password, db=mysql_database)
    cur = db.cursor()
    # SELECT
    #print(sql + param)
    if param != 'ha4k1r1337huoji120':
        cur.execute(sql, param)
    else:
        cur.execute(sql)
    if sql[0:6].upper() != 'SELECT':
        db.commit()
    db.close()
    return cur.fetchall()

def process_playerlist_decode(playerlist):
    return json.loads(base64.b64decode(playerlist).decode(encoding='GBK'))

def process_playerlist_encode(playerlist):
    return base64.b64encode(json.dumps(playerlist).encode(encoding='GBK'))


def random_get(arr):
	length = len(arr)
	if length < 1:
		return ''
	if length == 1:
		return str(arr[0])
	randomNumber = random.randint(0, length-1)
	return str(arr[randomNumber])

def checkmaps(a, b):
    tmp = [val for val in a if val in b]
    if not tmp:
        return False
    else:
        global match_map
        match_map = random_get(tmp)
        return True

def dict_find_players(dict, need_number, myRank, self_room_id,maps):
    found = 0
    result = []
    tmp = []
    for roomid in dict:
        if found == need_number:
            break
        if roomid in self_room_id:
            continue
        room = dict[roomid]
        range = abs(room['MaxRank'] - myRank)
        if range > search_range:
            continue
        if not checkmaps(room['maps'], maps):
            continue
        # 找刚好够人的房间
        if room['PlayerNumber'] == need_number:
            result.append(roomid)
            break
        if room['PlayerNumber'] < need_number:
            if room['PlayerNumber'] + found == 5:
                tmp.append(roomid)
                result = tmp
                break
            if found + room['PlayerNumber'] > 5:
                continue
            tmp.append(roomid)
            found += room['PlayerNumber']
    return result


def set_room_status_to_matching(roomid):
    runSQL("UPDATE roomlist SET `StartSearch` = 0 ,`ingame` = 1 WHERE `RoomID` = %s LIMIT 1", (roomid))
    result = {
        'msgType': 'match_start',
        'name': '',
        'roomid': roomid
    }
    json_encode = process_playerlist_encode(result).decode(encoding='GBK')
    redis_connect = redis_server
    redis_connect.publish('room', json_encode)


def get_players_by_room_id(roomlist, roomid):
    room_data = []
    players = []
    for index in range(len(roomlist)):
        if roomlist[index][sql_roomlist_RoomID] == roomid:
            room_data = roomlist[index]
            break
    if not room_data:
        return players
    playerlist = room_data[sql_roomlist_PlayerList]
    playerlist_decode = process_playerlist_decode(playerlist)
    for player_name in playerlist_decode:
        players.append(player_name)
    return players

def find_working_server(serverlist):
    working_server_data = []
    for index in range(len(serverlist)):
        if serverlist[index][sql_matchserver_matching] == 0:
            working_server_data = serverlist[index]
            break
    return working_server_data[sql_matchserver_serverID]

def match_server():
    # 声明一个匹配队列的结构，不用mysql，匹配队列放在内存中，减缓mysql的压力
    search_list = {
       # 'RoomID':
       # {
       #     'PlayerList': 'NULL',
       #     'MaxRank': 100,
       #     'PlayerNumber': 0,
       #     'maps':[]
       # }
    }
    while True:
        # 每3秒处理一次比赛队列
        time.sleep(3)
        # 服务器判断没服务器就不继续操作...
        all_working_server = runSQL("SELECT * FROM `matchserver` WHERE matching = 0")
        if not all_working_server:
            time.sleep(10)
            continue
        working_Server_number = len(all_working_server)
        # 先读取所有在搜索状态的房间
        all_room_search = runSQL("SELECT * FROM `roomlist`")
        if not all_room_search or len(all_room_search) == 1:
            # 休息一分钟或者十秒都可以啦
            time.sleep(10)
            continue
        # 删掉队列中不匹配的
        for index in range(len(all_room_search)):
            if all_room_search[index][sql_roomlist_StartSearch] == 0:
                roomid = all_room_search[index][sql_roomlist_RoomID]
                if roomid in search_list:
                    del search_list[roomid]
        # all_room_search 全部放到等待队列中
        for index in range(len(all_room_search)):
            if all_room_search[index][sql_roomlist_StartSearch] != 1:
                continue
            roomid = all_room_search[index][sql_roomlist_RoomID]
            if roomid in search_list:
                continue
            player_num = all_room_search[index][sql_roomlist_PlayerNumber]
            config = all_room_search[index][sql_roomlist_config]
            maps = process_playerlist_decode(config)['maps']
            search_list[roomid] = {
                'PlayerList': 'NULL',
                'MaxRank': 100,
                'PlayerNumber': 0,
                'maps': maps
            }
            search_list[roomid]['PlayerList'] = all_room_search[index][sql_roomlist_PlayerList]
            search_list[roomid]['MaxRank'] = all_room_search[index][sql_roomlist_Rank]
            search_list[roomid]['PlayerNumber'] = player_num
        # 处理搜索请求:
        searched = []
        team_red = []
        team_blue = []
        all_room_id = []
        match = {
            #'matchID': {
            #    'team_red': [],
            #    'team_blue': [],
            #    'team_red_player':[],
            #    'team_blue_player':[],
            #    'server': 'china',
            #    'maps': ''
            #}
        }
        run_check = False
        match_num = 0
        all_room_id.clear()
        for roomid in search_list:
            if match_num >= working_Server_number:
                break
            global match_map
            match_map = ''
            
            room = search_list[roomid]
            searched.append(roomid)
            # 填补队友
            if room['PlayerNumber'] != 5:
                need_players = 5 - room['PlayerNumber']        
                result = dict_find_players(
                    search_list, need_players, room['MaxRank'], searched, room['maps'])
                if not result:
                    searched.clear()
                    team_blue.clear()
                    team_red.clear()
                    continue
                # 找到了,这几支队伍合在一起：
                searched = searched + result
                result.append(roomid)
                team_red = result
            else:
                team_red.append(roomid)
            if team_red:
                result = dict_find_players(
                    search_list, 5, room['MaxRank'], searched, room['maps'])
                if not result:
                    searched.clear()
                    team_blue.clear()
                    team_red.clear()
                    continue
                searched = searched + result
                team_blue = result
                print('Found Match! Team1:' + str(team_red) +
                      " ||Team2: " + str(team_blue) + " ||match_map:" + match_map)
                #开始填充数据:
                time_tick = str(time.time()).replace('.', '')
                match_id = hash_md5(
                    str(time_tick + str(str(team_blue + team_red))).encode(encoding='GBK'))
                red_players = []
                blue_players = []
                all_room_id = team_red + team_blue
                for index in range(len(team_red)):
                    red_players = red_players + get_players_by_room_id(all_room_search, team_red[index])
                for index in range(len(team_blue)):
                    blue_players = blue_players + get_players_by_room_id(all_room_search,team_blue[index])
                match[match_id] = {
                    'team_red': team_red,
                    'team_blue': team_blue,
                    'team_red_player': red_players,
                    'team_blue_player': blue_players,
                    'server': find_working_server(all_working_server),
                    'maps': match_map
                }
                team_blue = {}
                team_red = {}
                match_num += 1
                continue
        if not match:
            continue
        for match_id in match:
            red_players = match[match_id]['team_red_player']
            blue_players = match[match_id]['team_blue_player']
            all_players = red_players + blue_players
            connectinfo = {
                'connected': [],
                'unconnect':[]
            }
            array = []
            #for index in range(len(all_players)):
            #    steamid = runSQL(
            #        'SELECT `SteamID` FROM userdata WHERE `username` = %s LIMIT 1', (all_players[index]))[0][0]
            #    array.append(steamid)
            connectinfo['unconnect'] = array
            team_red_encode = process_playerlist_encode(
                match[match_id]['team_red']).decode(encoding='GBK')
            team_blue_encode = process_playerlist_encode(
                match[match_id]['team_blue']).decode(encoding='GBK')
            team_red_players_encode = process_playerlist_encode(
                red_players).decode(encoding='GBK')
            team_blue_players_encode = process_playerlist_encode(
                blue_players).decode(encoding='GBK')
            connectinfo_encode = process_playerlist_encode(
                connectinfo).decode(encoding='GBK')
            serverid = match[match_id]['server']
            runSQL(
                'INSERT INTO matching (`matchid`,`team_red`,`team_blue`,`team_red_players`,`team_blue_players`,`serverid`,`map`,`uptime`,`connectinfo`) VALUES (%s,%s,%s,%s,%s,%s,%s,now(),%s)', (
                    match_id,
                    team_red_encode,
                    team_blue_encode,
                    team_red_players_encode,
                    team_blue_players_encode,
                    serverid,
                    match[match_id]['maps'],
                    connectinfo_encode
                ))
            runSQL("UPDATE matchserver SET `matching` = %s WHERE `serverID` = %s LIMIT 1", (1, serverid))
            for index in range(len(all_players)):
                runSQL("UPDATE userdata SET `matching` = %s WHERE `username` = %s LIMIT 1", (match_id,all_players[index]))
            for index in range(len(all_room_id)):
                set_room_status_to_matching(all_room_id[index])
                roomlist = runSQL(
                    'SELECT * FROM roomlist WHERE `RoomID` = %s limit 1', all_room_id[index])
                player_list = roomlist[0][sql_roomlist_PlayerList]
                player_list_decode = process_playerlist_decode(player_list)
                for name in player_list_decode:
                    player_list_decode[name]['ready'] = False
                player_list_encode = process_playerlist_encode(
                        player_list_decode).decode(encoding='GBK')
                runSQL('update roomlist set `ingame`=0 ,`ReadyNumber`= 0,`PlayerList` = %s where `RoomID` = %s limit 1', (player_list_encode,all_room_id[index]))

def start_server():
    threading.Thread(target=match_server, args=()).start()


if __name__ == '__main__':
    start_server()
