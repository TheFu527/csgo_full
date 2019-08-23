from django.http import HttpResponse
from django.shortcuts import render, redirect
import platform
import django
from www import GlobalVar


def getALLinfos(first, last):
    return GlobalVar.runSQL("select * from matchserver limit %s,%s ", (first, last))


def getALLinfos_casual(first, last):
    return GlobalVar.runSQL("select * from casualservers limit %s,%s ", (first, last))


def getNowCount():
    return GlobalVar.runSQL("select COUNT(*) from matchserver")[0][0]


def getNowCount_casual():
    return GlobalVar.runSQL("select COUNT(*) from casualservers")[0][0]


def deleteServerByID(id):
    GlobalVar.runSQL(
        "DELETE FROM matchserver where `serverID` = %s limit 1", (id))


def changeMatchStusbyID(id, status):
    GlobalVar.runSQL(
        "UPDATE matchserver SET `matching` = %s WHERE `serverID` = %s limit 1", (int(status), id))


def getMatchingStatus(id):
    return GlobalVar.runSQL("SELECT * FROM matchserver where `serverID` = %s limit 1", (id))[0][GlobalVar.sql_matchserver_matching]


def search(name):
    return GlobalVar.runSQL("select * from matchserver where serverID like %s", ('%' + name + '%'))


def search_casual(name):
    return GlobalVar.runSQL("select * from casualservers where serverid like %s", ('%'+name+'%'))


def add_casual(request, index_path):
    info = {'server_id': '服务器ID',
            'hostname': '服务器主人名字',
            'ip': 'ip地址',
            'port': '27015',
            'type': '死斗',
            'add_server': 1
            }
    if request.method == 'GET':
        if 'add_casual' in request.GET:
            server_id = request.GET['id']
            hostname = request.GET['hostname']
            ip = request.GET['ipaddr']
            port = request.GET['port']
            type = request.GET['type']
            GlobalVar.runSQL(
                'INSERT INTO casualservers (`serverid`,`hostname`,`ip`,`port`,`type`) VALUES (%s,%s,%s,%s,%s)',
                (server_id, hostname, ip, port, type))
    return render(request, index_path + "/admin-edit-server-casual.html", info)


def add(request, index_path):
    info = {'server_id': '服务器ID',
            'server_location': '服务器地理位置',
            'server_group': '服务器分组',
            'server_ip_port': '127.0.0.1:27015',
            'add_server': 1
            }
    if request.method == 'GET':
        if 'addserver' in request.GET:
            server_id = request.GET['id']
            location = request.GET['location']
            group = request.GET['group']
            ipaddr = request.GET['ipaddr']
            ip = ipaddr.split(':')[0]
            port = int(ipaddr.split(':')[1])
            matching = 0
            GlobalVar.runSQL(
                'INSERT INTO matchserver (`serverID`,`location`,`group`,`matching`,`ip`,`port`) VALUES (%s,%s,%s,%s,%s,%s)',
                (server_id, location, group, matching, ip, port))
    return render(request, index_path + "/admin-edit-server.html", info)


def casual(request, index_path):
    all_info = []
    serverInfo = []
    all_flush = []
    if request.method == 'GET':
        if 'del' in request.GET:
            GlobalVar.runSQL(
                'DELETE FROM casualservers WHERE `serverid` = %s', (request.GET['del']))
        if 'edit_server' in request.GET and 'id' in request.GET:
            info = {'server_id': request.GET['id'],
                    'hostname': request.GET['hostname'],
                    'ip': request.GET['ip'],
                    'port': request.GET['port'],
                    'type': request.GET['type'],
                    'add_server': 0
                    }
            return render(request, index_path + "/admin-edit-server-casual.html", info)
        if 'config_casual' in request.GET:
            server_id = request.GET['id']
            hostname = request.GET['hostname']
            ip = request.GET['ipaddr']
            port = request.GET['port']
            type = request.GET['type']
            GlobalVar.runSQL("UPDATE casualservers SET `serverid`=%s,`hostname`=%s,`ip`=%s,`port`=%s,`type`=%s WHERE `serverid` = %s limit 1",
                            (server_id,hostname,ip,port,type,request.GET['config_casual']))
        if 'search' in request.GET:
            all_info = search_casual(request.GET['search'])
        else:
            try:
                if 'p' in request.GET:
                    int_get = int(request.GET['p'])
                    if int_get < 0:
                        return HttpResponse('FUCK YOU HACKER')
                    maxNumber = getNowCount_casual()
                    needFlush = 0
                    if maxNumber > 10:
                        needFlush = (maxNumber // 10) + 1
                        temp = 0
                        while True:
                            if temp == needFlush:
                                break
                            all_flush.append(temp)
                            temp += 1
                    all_info = getALLinfos_casual(
                        int_get * 10, 20)
            except:
                all_info = getALLinfos_casual(0, 10)
    for index in range(len(all_info)):
        serverInfo.append({
            'id': all_info[index][GlobalVar.sql_casualservers_serverid],
            'hostname': all_info[index][GlobalVar.sql_casualservers_hostname],
            'ip': all_info[index][GlobalVar.sql_casualservers_ip],
            'port': all_info[index][GlobalVar.sql_casualservers_port],
            'type': all_info[index][GlobalVar.sql_casualservers_type]
        })
    # 剩下的交给前端
    return render(request, index_path + "/server_casual.html", {'servers': serverInfo, 'flush': all_flush})


def main(request, index_path):
    all_info = []
    serverInfo = []
    all_flush = []
    if request.method == 'GET':
        if 'del' in request.GET:
            GlobalVar.runSQL(
                'DELETE FROM matchserver WHERE `serverID` = %s', (request.GET['del']))
        if 'change' in request.GET:
            status = getMatchingStatus(request.GET['change'])
            if status == 3:
                status = 0
            else:
                status = not status
            changeMatchStusbyID(request.GET['change'], status)
        if 'edit_server' in request.GET and 'serverid' in request.GET and 'location' in request.GET:
            info = {'server_id': request.GET['serverid'],
                    'server_location': request.GET['location'],
                    'server_group': request.GET['group'],
                    'server_matching': request.GET['matching'],
                    'server_ip_port': request.GET['ip_port'],
                    'add_server': 0
                    }
            return render(request, index_path + "/admin-edit-server.html", info)
        if 'config' in request.GET and 'location' in request.GET and 'group' in request.GET and 'ipaddr' in request.GET:
            server_id = request.GET['id']
            location = request.GET['location']
            group = request.GET['group']
            ipaddr = request.GET['ipaddr']
            ip = ipaddr.split(':')[0]
            port = int(ipaddr.split(':')[1])
            GlobalVar.runSQL(
                "UPDATE matchserver SET `serverID`= %s,`location` = %s,`group`=%s,`ip`=%s,`port`=%s WHERE `serverID` = %s limit 1", (server_id, location, group, ip, port, request.GET['config']))
        if 'search' in request.GET:
            all_info = search(request.GET['search'])
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
                        int_get * 10, 20)
            except:
                all_info = getALLinfos(0, 10)
    for index in range(len(all_info)):
        matching = '空闲'
        btn_class = "layui-btn layui-btn-normal layui-btn-mini"
        if all_info[index][GlobalVar.sql_matchserver_matching] == 1:
            matching = '比赛中'
            btn_class = "layui-btn layui-btn-warm layui-btn-mini"
        elif all_info[index][GlobalVar.sql_matchserver_matching] == 3:
            matching = '崩溃'
            btn_class = "layui-btn layui-btn-warm layui-btn-danger"
        serverInfo.append({
            'id': all_info[index][GlobalVar.sql_matchserver_serverID],
            'location': all_info[index][GlobalVar.sql_matchserver_location],
            'group': all_info[index][GlobalVar.sql_matchserver_group],
            'matching': matching,
            'btn_class': btn_class,
            'ip_port': all_info[index][GlobalVar.sql_matchserver_ip] + ":" + str(all_info[index][GlobalVar.sql_matchserver_port])
        })
    # 剩下的交给前端
    return render(request, index_path + "/server_manage.html", {'servers': serverInfo, 'flush': all_flush})
