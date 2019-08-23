from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import base64,time,random,hashlib,json,re,django,platform
from . import server_helper,match,view,web_socket,search_process,GlobalVar
from www.index import player as index_player


def hash_md5(str):
    return hashlib.md5(str).hexdigest()


def get_json(result):
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json,charset=utf-8")


def process_getdata_by_key(key):
    return GlobalVar.runSQL('SELECT * FROM userdata WHERE `Key` = %s LIMIT 1', key)


def process_playerlist_decode(playerlist):
    return json.loads(base64.b64decode(playerlist).decode(encoding='GBK'))


def process_playerlist_encode(playerlist):
    return base64.b64encode(json.dumps(playerlist).encode(encoding='GBK'))


def process_playerlist_remove(playerlist, name):
    #del playerlist[name]
    playerlist.pop(name)
    return playerlist

def get_by_steamid(steamid):
    return GlobalVar.runSQL(
        'SELECT * FROM userdata WHERE `SteamID` = %s LIMIT 1', (steamid))
def get_by_name(player_name):
    return GlobalVar.runSQL(
        'SELECT * FROM userdata WHERE `username` = %s LIMIT 1', (player_name))


def process_exit_room(sec_key):
    Check = process_getdata_by_key(sec_key)
    if not Check:
        return False
    room_id = Check[0][GlobalVar.sql_userdata_roomid]
    myName = Check[0][GlobalVar.sql_userdata_username]
    if room_id == '0':
        return False
    Check = GlobalVar.runSQL(
        'SELECT * FROM roomlist WHERE `RoomID` = %s LIMIT 1', (room_id))
    if not Check:
        GlobalVar.runSQL(
            "UPDATE userdata SET `roomid` = '0' WHERE `Key` = %s LIMIT 1", sec_key)
        return True
    player_list = Check[0][GlobalVar.sql_roomlist_PlayerList]
    player_number = Check[0][GlobalVar.sql_roomlist_PlayerNumber]
    ready_number = Check[0][GlobalVar.sql_roomlist_ReadyNumber]
    player_list_decode = process_playerlist_decode(player_list)
    found = False
    for name in player_list_decode:
        if name == myName:
            found = True
    if not found:
        GlobalVar.runSQL(
            "UPDATE userdata SET `roomid` = '0' WHERE `Key` = %s LIMIT 1", sec_key)
        return True
    if Check[0][GlobalVar.sql_roomlist_ingame]:
        return True
    # if search_process.check_in_search(Check):
    #    search_process.stop_search(room_id)
    if player_number == 1:
        if search_process.check_in_search(Check):
            search_process.stop_search(room_id)
        GlobalVar.runSQL(
            "UPDATE userdata SET `roomid` = '0' WHERE `Key` = %s LIMIT 1", sec_key)
        GlobalVar.runSQL(
            "DELETE FROM roomlist WHERE `RoomID` = %s LIMIT 1", room_id)
        return True
    player_list_decode = process_playerlist_remove(player_list_decode, myName)
    web_socket.send_player_leave_room(room_id, myName)
    new_player_num = player_number - 1
    new_ready_num = ready_number - 1
    new_max_rank = 100
    #{'ready': False, 'Rank': 100, 'ico': 'null'}
    for name in player_list_decode:
        #print('name:' + name + "rank:" + str(player_list_decode[name]['Rank']))
        if player_list_decode[name]['Rank'] > new_max_rank:
            new_max_rank = player_list_decode[name]['Rank']
    player_list_encode = process_playerlist_encode(
        player_list_decode).decode(encoding='GBK')
    GlobalVar.runSQL(
        "UPDATE userdata SET `roomid` = '0' WHERE `Key` = %s LIMIT 1", sec_key)
    GlobalVar.runSQL(
        "UPDATE roomlist SET `Rank`=%s,`PlayerNumber` = %s ,`ReadyNumber`= %s,`PlayerList`= %s WHERE `RoomID` = %s LIMIT 1", (new_max_rank, new_player_num, new_ready_num, player_list_encode, room_id))
    return True

def get_invietcode(name,code):
    check = GlobalVar.runSQL("SELECT * FROM invitecode WHERE `code` = %s and `used` = 0 limit 1", code)
    if not check:
        return False
    GlobalVar.runSQL("UPDATE invitecode SET `used` = 1,`name` = %s WHERE `code` = %s limit 1", (name, code))
    return True

@csrf_exempt
def do_register(request):
    result = {
        'msgType': 'register',
        'uFuck': 1,
        'success': 0
    }
    room_config = {
        'ico': 'default.jpg',
        'title': '菜鸡房间',
        'text': '这个人是菜鸡,因为他的房间还是默认的标题和内容!',
        'maps': ['de_dust2', 'de_nuke', 'de_mirage', 'de_overpass', 'de_cache', 'de_inferno', 'de_train', 'de_cbble'],
        'public': 1
    }
    data = {
        'kill': 0,
        'dead': 0,
        'first': 0,
        'headshot': 0,
        'help': 0,
        'music': 39227624,
        'autoplay': 1,
        'matched': [],
        'rank': {},
        'ico': 'null'
    }
    if request.method == 'POST':
        if True:
            if 'Regname' in request.POST and 'Regpass' in request.POST and 'Regemail' in request.POST and 'auth' in request.POST and 'InviteCode' in request.POST:
                if not view.auth_send_post(request.POST['auth']):
                    result['uFuck'] = 6
                    return get_json(result)
                if not re.findall(r'^[0-9a-zA-Z\_\-]+(\.[0-9a-zA-Z\_\-]+)*@[0-9a-zA-Z]+(\.[0-9a-zA-Z]+){1,}$', request.POST['Regemail']):
                    result['uFuck'] = 2
                    return get_json(result)
                name_proccesed = web_socket.htmlescape(request.POST['Regname'])
                if name_proccesed == '你是个好人' or name_proccesed == 'huoji':
                    result['uFuck'] = 5
                    return get_json(result)
                if len(name_proccesed) > 15:
                    result['uFuck'] = 7
                    return get_json(result)
                email_proccesed = web_socket.htmlescape(
                    request.POST['Regemail'])
                if not re.search(u'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', name_proccesed):
                    result['uFuck'] = 5
                    return get_json(result)
                Check = GlobalVar.runSQL(
                    'SELECT * FROM userdata WHERE username = %s LIMIT 1', (name_proccesed))
                if Check:
                    result['uFuck'] = 3
                    return get_json(result)
                Check = GlobalVar.runSQL(
                    'SELECT * FROM userdata WHERE email = %s LIMIT 1', (email_proccesed))
                if Check:
                    result['uFuck'] = 4
                    return get_json(result)
                if not get_invietcode(name_proccesed, request.POST['InviteCode']):
                    result['uFuck'] = 8
                    return get_json(result)
                password = hash_md5(
                    hash_md5(request.POST['Regpass'].encode(encoding='GBK')).encode(encoding='GBK'))
                TheKey = hash_md5(base64.b64encode(
                    str(
                        name_proccesed +
                        email_proccesed
                    ).encode(encoding='GBK')
                    + password.encode(encoding='GBK')
                ))
                data_encode = process_playerlist_encode(
                    data).decode(encoding='GBK')
                GlobalVar.runSQL(
                    'INSERT INTO userdata (`username`,`password`,`email`,`Key`,`roomconfig`,`data`) VALUES (%s,%s,%s,%s,%s,%s)', (name_proccesed, password, email_proccesed, TheKey, process_playerlist_encode(room_config).decode(encoding='GBK'), data_encode))
                result['uFuck'] = 0
                result['success'] = 1
                return get_json(result)
        #except:
        #    return HttpResponse('you mother fuck up')
    return get_json(result)


@csrf_exempt
def do_login(request):
    result = {
        'msgType': 'Login',
        'uFuck': 1,
        'secKey': 'NULL',
        'success': 0
    }
    if 'logname' in request.POST and 'logpass' in request.POST:
        Check = GlobalVar.runSQL(
            'SELECT * FROM userdata WHERE username = %s LIMIT 1', (request.POST['logname']))
        if not Check:
            result['uFuck'] = 2
            return get_json(result)
        hashed_key = hash_md5(hash_md5(request.POST['logpass'].encode(
            encoding='GBK')).encode(encoding='GBK'))
        if Check[0][GlobalVar.sql_userdata_password] != hashed_key:
            result['uFuck'] = 3
            return get_json(result)
        if Check[0][GlobalVar.sql_userdata_banned]:
            result['uFuck'] = 4
            return get_json(result)
        result['secKey'] = Check[0][GlobalVar.sql_userdata_Key]
        result['uFuck'] = 0
        result['success'] = 1
        return get_json(result)
    return get_json(result)


def process_check_room(key):
    Check = process_getdata_by_key(key)
    if not Check:
        return 0
    sec_key = Check[0][GlobalVar.sql_userdata_Key]
    player_name = Check[0][GlobalVar.sql_userdata_username]
    room_id = Check[0][GlobalVar.sql_userdata_roomid]
    banned = Check[0][GlobalVar.sql_userdata_banned]
    if room_id == '0':
        return 0
    if banned == 1:
        return 110
    Check = GlobalVar.runSQL(
        'SELECT * FROM roomlist WHERE `RoomID` = %s LIMIT 1', room_id)
    if not Check:
        GlobalVar.runSQL(
            "UPDATE userdata SET `roomid` = '0' WHERE `Key` = %s LIMIT 1", key)
        return 0
    return room_id


def do_check_steamid(request):
    result = {
        'msgType': 'CheckSteamid',
        'success': 0
    }
    if request.GET and 'key' in request.GET:
        data = GlobalVar.runSQL('select * from userdata where `SteamID` is null and `Key` = %s limit 1',request.GET['key'])
        if not data:
            return get_json(result)
        result['success'] = 1
        return get_json(result)
    return get_json(result)

def do_check(request):
    result = {
        'msgType': 'CheckRoom',
        'uFuck': 1,
        'RoomID': 'NULL',
        'ingame': 0,
        'success': 0
    }
    if request.method != 'GET':
        return get_json(result)
    try:
        if 'key' in request.GET:
            result['uFuck'] = 0
            result['success'] = 1
            result['RoomID'] = 0
            room_id = process_check_room(request.GET['key'])
            if room_id == 0:
                return get_json(result)
            elif room_id == 110:
                result['uFuck'] = 3
                result['RoomID'] = room_id
                return get_json(result)
            else:
                Check = GlobalVar.runSQL(
                    'SELECT * FROM roomlist WHERE `RoomID` = %s AND `ingame` = 0 LIMIT 1', room_id)
                if not Check:
                    result['ingame'] = 1
                result['uFuck'] = 2
                result['RoomID'] = room_id
                return get_json(result)
    except:
        result['success'] = 0
        return get_json(result)
    return get_json(result)


def do_exit(request):
    result = {
        'msgType': 'ExitRoom',
        'uFuck': 1,
        'success': 0
    }
    # 要加try
    if True:
        if 'key' in request.GET:
            result['success'] = process_exit_room(request.GET['key'])
            return get_json(result)
    # except:
    return get_json(result)


def do_join(request):
    result = {
        'msgType': 'JoinRoom',
        'uFuck': 1,
        'RoomID': 'NULL',
        'success': 0
    }
    if request.method != 'GET':
        return get_json(result)
    # 要加try
    try:
        if 'key' in request.GET and 'create' in request.GET and 'roomid' in request.GET:
            if request.GET['create'] != 'true' and request.GET['create'] != 'false':
                return get_json(result)
            sec_key = request.GET['key']
            Check = process_getdata_by_key(sec_key)
            if not Check:
                return get_json(result)
            room_id = process_check_room(sec_key)
            if room_id != 0:
                result['uFuck'] = 2
                result['RoomID'] = room_id
                return get_json(result)
            player_name = Check[0][GlobalVar.sql_userdata_username]
            player_rank = Check[0][GlobalVar.sql_userdata_rank]
            player_room_config = Check[0][GlobalVar.sql_userdata_roomconfig]
            player_ico =  Check[0][GlobalVar.sql_userdata_PlayerInfo]
            if Check[0][GlobalVar.sql_userdata_banned]:
                result['RoomID'] = '好聪明哦'
                return get_json(result)
            if request.GET['create'] == 'true':
                player_room_config_decode = process_playerlist_decode(
                    player_room_config)
                time_tick = str(time.time()).replace('.', '')
                room_id = hash_md5(
                    str(time_tick + str(player_name)).encode(encoding='GBK'))[0:6]
                player_list = process_playerlist_encode({
                    player_name:
                    {
                        'ready': False,
                        'Rank': player_rank,
                        'ico': player_ico
                    }
                }).decode(encoding='GBK')
                GlobalVar.runSQL(
                    "UPDATE userdata SET `roomid` = %s WHERE `Key` = %s LIMIT 1", (room_id, sec_key))
                GlobalVar.runSQL(
                    'INSERT INTO roomlist (`RoomID`,`ingame`,`PlayerNumber`,`PlayerList`,`Rank`,`config`,`public`) VALUES (%s,%s,%s,%s,%s,%s,%s)', (room_id, 0, 1, player_list, player_rank, player_room_config, player_room_config_decode['public']))
                result['uFuck'] = 0
                result['success'] = 1
                result['RoomID'] = room_id
                # print(result['success'])
                return get_json(result)
            elif request.GET['create'] == 'false':
                room_id = request.GET['roomid']
                result['RoomID'] = room_id
                Check = GlobalVar.runSQL(
                    'SELECT * FROM roomlist WHERE `RoomID` = %s LIMIT 1', (room_id))
                if not Check:
                    result['uFuck'] = 3
                    return get_json(result)
                if Check[0][GlobalVar.sql_roomlist_PlayerNumber] >= 5:
                    result['uFuck'] = 4
                    return get_json(result)
                if Check[0][GlobalVar.sql_roomlist_ingame] == 1:
                    result['uFuck'] = 6
                    return get_json(result)
                if search_process.check_in_search(Check):
                    search_process.stop_search(room_id)
                result['success'] = 1
                GlobalVar.runSQL(
                    "UPDATE userdata SET `roomid` = %s WHERE `Key` = %s LIMIT 1", (room_id, sec_key))
                plyaer_list_decode = process_playerlist_decode(
                    Check[0][GlobalVar.sql_roomlist_PlayerList])
                plyaer_list_decode[player_name] = {
                    'ready': False,
                    'Rank': player_rank,
                    'ico': player_ico
                }
                new_player_num = Check[0][GlobalVar.sql_roomlist_PlayerNumber] + 1
                new_ready_num = Check[0][GlobalVar.sql_roomlist_ReadyNumber] + 1
                new_max_rank = 100
                for name in plyaer_list_decode:
                    if plyaer_list_decode[name]['Rank'] > new_max_rank:
                        new_max_rank = plyaer_list_decode[name]['Rank']
                player_list_encode = process_playerlist_encode(
                    plyaer_list_decode).decode(encoding='GBK')
                #print(str((new_max_rank, player_list_encode,
                #           new_player_num, new_ready_num, room_id)))
                GlobalVar.runSQL(
                    "UPDATE roomlist SET `Rank` = %s ,`PlayerList` = %s,`PlayerNumber`=%s,`ReadyNumber`=%s WHERE `RoomID` = %s LIMIT 1",
                    (new_max_rank, player_list_encode, new_player_num, new_ready_num, room_id))
                result['uFuck'] = 0
                result['success'] = 1
                result['RoomID'] = room_id
                web_socket.send_player_join_room(room_id, player_name)
                return get_json(result)
    except:
        return get_json(result)


@csrf_exempt
def process(request, moudle):
    result = HttpResponse()
    if moudle in 'register':
        result = do_register(request)
    if moudle in 'login':
        result = do_login(request)
    if moudle in 'check_in_room':
        result = do_check(request)
    if moudle in 'exit_room':
        result = do_exit(request)
    if moudle in 'join_room':
        result = do_join(request)
    if moudle in 'check_steamid':
        result = do_check_steamid(request)
    if moudle in 'resolve_server':
        result = server_helper.resolve_server(request)
    if moudle in 'get_all_casual_server':
        result = server_helper.get_all_casual_server(request)
    if moudle in 'get_player':
        result = index_player.api_get(request)
    if moudle in 'set_music':
        result = index_player.api_setmusic(request)
    if moudle in 'api_get_by_key':
        result = index_player.api_get_byKey(request)
    if moudle in 'update_image':
        result = index_player.update_image(request)
    if moudle in 'match_api':
        result = match.main(request)
    if moudle in 'get_match':
        result = match.get_matched_info(request)
    return result
