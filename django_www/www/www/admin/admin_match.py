from django.http import HttpResponse
from django.shortcuts import render, redirect
import platform
import django
from www import GlobalVar, api_process


def getNowCount_matching():
    return GlobalVar.runSQL("select COUNT(id) from matching ")[0][0]


def getALLinfos_matching(first, last):
    return GlobalVar.runSQL("select * from matching ORDER BY `uptime` ASC limit %s,%s", (first, last))


def SearchMatch_matching(id):
    return GlobalVar.runSQL("select * from matching where `serverid` ORDER BY `uptime` ASC like %s", ('%' + id + '%'))


def getNowCount():
    return GlobalVar.runSQL("select COUNT(id) from matched ")[0][0]


def getALLinfos(first, last):
    return GlobalVar.runSQL("select * from matched ORDER BY `time` ASC limit %s,%s", (first, last))


def SearchMatch(id):
    return GlobalVar.runSQL("select * from matched where `matchid` ORDER BY `time` ASC like %s", ('%' + id + '%'))


def matching(request, index_path):
    all_info = []
    matchInfo = []
    all_flush = []
    if request.method == 'GET':
        if 'search' in request.GET:
            all_info = SearchMatch(request.GET['search'])
        else:
            try:
                if 'p' in request.GET:
                    int_get = int(request.GET['p'])
                    if int_get < 0:
                        return HttpResponse('FUCK YOU HACKER')
                    maxNumber = getNowCount_matching()
                    needFlush = 0
                    if maxNumber > 10:
                        needFlush = (maxNumber // 10) + 1
                        temp = 0
                        while True:
                            if temp == needFlush:
                                break
                            all_flush.append(temp)
                            temp += 1
                    all_info = getALLinfos_matching(
                        int_get * 10, int_get * 10 + 10)
            except:
                all_info = getALLinfos_matching(0, 10)
        for index in range(len(all_info)):
            matchInfo.append({
                'matchid': all_info[index][GlobalVar.sql_matching_matchid],
                'red_team_player': api_process.process_playerlist_decode(all_info[index][GlobalVar.sql_matching_team_red_players]),
                'blue_team_player': api_process.process_playerlist_decode(all_info[index][GlobalVar.sql_matching_team_blue_players]),
                'red_team_score': all_info[index][GlobalVar.sql_matching_team_red_status],
                'blue_team_score': all_info[index][GlobalVar.sql_matching_team_blue_status],
                'cheater': all_info[index][GlobalVar.sql_matching_hvh],
                'serverid': all_info[index][GlobalVar.sql_matching_serverid],
                'map': all_info[index][GlobalVar.sql_matching_map],
                'time': all_info[index][GlobalVar.sql_matching_uptime]
            })
    return render(request, index_path + "/match-list-working.html", {'match': matchInfo, 'flush': all_flush})


def matched(request, index_path):
    all_info = []
    matchInfo = []
    all_flush = []
    if request.method == 'GET':
        if 'search' in request.GET:
            all_info = SearchMatch(request.GET['search'])
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
                        while True:
                            if temp == needFlush:
                                break
                            all_flush.append(temp)
                            temp += 1
                    all_info = getALLinfos(
                        int_get * 10, int_get * 10 + 10)
            except:
                all_info = getALLinfos(0, 10)
        for index in range(len(all_info)):
            matchInfo.append({
                'matchid': all_info[index][GlobalVar.sql_matched_matchid],
                'red_team_player': api_process.process_playerlist_decode(all_info[index][GlobalVar.sql_matched_red_team_player]),
                'blue_team_player': api_process.process_playerlist_decode(all_info[index][GlobalVar.sql_matched_blue_team_player]),
                'red_team_score': all_info[index][GlobalVar.sql_matched_red_team_score],
                'blue_team_score': all_info[index][GlobalVar.sql_matched_blue_team_score],
                'cheater': all_info[index][GlobalVar.sql_matched_cheater],
                'serverid': all_info[index][GlobalVar.sql_matched_serverid],
                'demoid': all_info[index][GlobalVar.sql_matched_demoid],
                'time': all_info[index][GlobalVar.sql_matched_time],
                'map': all_info[index][GlobalVar.sql_matched_map],
            })
    return render(request, index_path + "/match-list.html", {'match': matchInfo, 'flush': all_flush})
