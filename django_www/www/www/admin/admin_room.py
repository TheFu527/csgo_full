from django.http import HttpResponse
from django.shortcuts import render, redirect
import platform
import django
from www import GlobalVar
from www import api_process


def getALLinfos(first, last):
    return GlobalVar.runSQL("select * from roomlist limit %s,%s ", (first, last))


def getNowCount():
    return GlobalVar.runSQL("select COUNT(*) from roomlist")[0][0]


def main(request, index_path):
    all_info = []
    roomInfo = []
    all_flush = []
    if request.method == 'GET':
        if 'delroom' in request.GET:
            roomid = request.GET['delroom']
            check = GlobalVar.runSQL(
                'SELECT * FROM roomlist WHERE `RoomID` = %s', roomid)
            if check:
                if not check[0][GlobalVar.sql_roomlist_ingame]:
                    result = {
                        'msgType': 'kick',
                        'name': '',
                        'roomid': roomid
                    }
                    GlobalVar.runSQL(
                        "DELETE FROM roomlist WHERE `RoomID` = %s LIMIT 1", roomid)
                    json_encode = api_process.process_playerlist_encode(
                        result).decode(encoding='GBK')
                    redis_connect = GlobalVar.get_value('g_redis_server')
                    redis_connect.publish('room', json_encode)
        try:
            if 'p' in request.GET:
                int_get = int(request.GET['p'])
                if int_get < 0:
                    return HttpResponse('FUCK YOU HACKER')
                maxNumber = getNowCount()
                needFlush = 0
                if maxNumber > 10:
                    needFlush = (maxNumber // 10) + 1
                    temp = 0
                    while True:
                        if temp == needFlush:
                            break
                        all_flush.append(temp)
                        temp += 1
                all_info = getALLinfos(
                    int_get * 10, 20)
        except:
            all_info = getALLinfos(0, 10)

    for index in range(len(all_info)):
        player_list_encode = all_info[index][GlobalVar.sql_roomlist_PlayerList]
        player_list_decode = api_process.process_playerlist_decode(
            player_list_encode)
        players_name = list(player_list_decode.keys())
        config = all_info[index][GlobalVar.sql_roomlist_config]
        config_decode = api_process.process_playerlist_decode(config)
        public = '隐身'
        btn_class = "layui-btn layui-btn-normal layui-btn-mini"
        if all_info[index][GlobalVar.sql_roomlist_public]:
            public = '公开'
            btn_class = "layui-btn layui-btn-warm layui-btn-mini"
        search = '空闲'
        btn_search_class = "layui-btn layui-btn-normal layui-btn-mini"
        if all_info[index][GlobalVar.sql_roomlist_StartSearch]:
            search = '搜索中'
            btn_search_class = "layui-btn layui-btn-warm layui-btn-mini"
        ingame = '空闲'
        btn_ingame_class = "layui-btn layui-btn-normal layui-btn-mini"
        if all_info[index][GlobalVar.sql_roomlist_ingame]:
            ingame = '游戏中'
            btn_ingame_class = "layui-btn layui-btn-warm layui-btn-mini"
        roomInfo.append({
            'roomid': all_info[index][GlobalVar.sql_roomlist_RoomID],
            'players': players_name,
            'in_search': all_info[index][GlobalVar.sql_roomlist_StartSearch],
            'rank': all_info[index][GlobalVar.sql_roomlist_Rank],
            'title': config_decode['title'],
            'text': config_decode['text'],
            'ico': config_decode['ico'],
            'ingame': ingame,
            'public': public,
            'search': search,
            'btn_class': btn_class,
            'btn_search_class': btn_search_class,
            'btn_ingame_class': btn_ingame_class
        })
    # 剩下的交给前端
    return render(request, index_path + "/room_manage.html", {'rooms': roomInfo, 'flush': all_flush})
