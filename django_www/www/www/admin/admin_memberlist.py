from django.http import HttpResponse
from django.shortcuts import render, redirect
import platform
import django
from www import GlobalVar
from www import api_process


def getALLinfos(first, last):
    return GlobalVar.runSQL("select * from userdata ORDER BY `id` ASC limit %s,%s ", (first, last))


def getNowCount():
    return GlobalVar.runSQL("select COUNT(id) from userdata")[0][0]


def searchPlayer(name):
    return GlobalVar.runSQL("select * from userdata where `username` like %s ORDER BY `id` ASC", ('%'+name+'%'))


def getPlayerinfo(name):
    return GlobalVar.runSQL("select * from userdata where `username` = %s limit 1", (name))


def setPlayerBan(name, ban=1):
    return GlobalVar.runSQL("update userdata set `banned` = %s where username = %s limit 1", (ban, name))


def main(request, index_path):
    all_info = []
    userInfo = []
    all_flush = []
    if request.method == 'GET':
        if 'ban' in request.GET:
            setPlayerBan(request.GET['ban'])
        if 'unban' in request.GET:
            setPlayerBan(request.GET['unban'], 0)
        if 'search' in request.GET:
            all_info = searchPlayer(request.GET['search'])
        if 'username' in request.GET:
            all_info = getPlayerinfo(request.GET['username'])
        else:
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
                        left = int_get - 8
                        right = int_get + 8
                        while True:
                            temp += 1
                            if temp == needFlush:
                                break
                            if temp < left or temp > right:
                                continue
                            all_flush.append(temp)

                    all_info = getALLinfos(
                        int_get * 10, 20)
            except:
                all_info = getALLinfos(0, 10)

    for index in range(len(all_info)):
        config_decode = api_process.process_playerlist_decode(
            all_info[index][GlobalVar.sql_userdata_roomconfig])
        status = all_info[index][GlobalVar.sql_userdata_banned]
        banned = '封禁'
        btn_class = 'layui-btn layui-btn-danger layui-btn-mini'
        if not status:
            banned = '正常'
            btn_class = 'layui-btn layui-btn-normal layui-btn-mini'
        userInfo.append({
            'id': all_info[index][GlobalVar.sql_userdata_id],
            'name': all_info[index][GlobalVar.sql_userdata_username],
            'email': all_info[index][GlobalVar.sql_userdata_email],
            'steamID': all_info[index][GlobalVar.sql_userdata_SteamID],
            'title': config_decode['title'],
            'text': config_decode['text'],
            'ico': config_decode['ico'],
            'rank': all_info[index][GlobalVar.sql_userdata_rank],
            'status': banned,
            'btn_class': btn_class
        })
    # 剩下的交给前端
    return render(request, index_path + "/member-list.html", {'users': userInfo, 'flush': all_flush})
