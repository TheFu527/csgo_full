from django.http import HttpResponse
from django.shortcuts import render, redirect
import django
import json
import platform
import string
import random
from www import GlobalVar, api_process


def generate_random_str(randomlength):
    str_list = random.sample(
        string.digits + string.ascii_letters, randomlength)
    random_str = ''.join(str_list)
    return random_str


def getNowCount():
    return GlobalVar.runSQL("select COUNT(*) from invitecode ")[0][0]


def getALLinfos(first, last):
    return GlobalVar.runSQL("select * from invitecode limit %s,%s", (first, last))


def SearchMatch(id):
    return GlobalVar.runSQL("select * from invitecode where `code` like %s", ('%' + id + '%'))


def add_code(request, index_path):
    result = []
    if 'add' in request.GET:
        add_num = int(request.GET['add'])
        if add_num > 100:
            return json.dumps(result)
        for index in range(add_num):
            rand_str = generate_random_str(24)
            result.append(rand_str)
            GlobalVar.runSQL(
                'INSERT INTO invitecode (`code`) VALUES (%s)', rand_str)
    return render(request, index_path + "/invitecode-add.html", {'code_array': result})


def main(request, index_path):
    all_info = []
    Info = []
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
            use_text = '未使用'
            used = all_info[index][GlobalVar.sql_invitecode_used]
            if used == 1:
                use_text = '已经使用'
            Info.append({
                'code': all_info[index][GlobalVar.sql_invitecode_code],
                'used': use_text,
                'name': all_info[index][GlobalVar.sql_invitecode_name]
            })
    return render(request, index_path + "/invitecode-list.html", {'info': Info, 'flush': all_flush})
