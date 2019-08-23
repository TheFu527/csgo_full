from django.http import HttpResponse
from django.shortcuts import render, redirect
import django
import re
import json
from . import GlobalVar
from . import web_socket
from . import api_process
import valve.source
import valve.source.a2s
import valve.source.master_server


def get_all_casual_server(request):
    result = {
        'msgType': 'get_all_casual_server',
        'servers': {},
        'success': 0
    }
    server = {}
    check = GlobalVar.runSQL('SELECT * FROM casualservers')
    if not check:
        return api_process.get_json(result)
    for index in range(len(check)):
        serverid = check[index][GlobalVar.sql_casualservers_serverid]
        hostname = check[index][GlobalVar.sql_casualservers_hostname]
        ip = check[index][GlobalVar.sql_casualservers_ip]
        port = check[index][GlobalVar.sql_casualservers_port]
        type = check[index][GlobalVar.sql_casualservers_type]
        server[serverid] = {
            'hostname': hostname,
            'ip': ip,
            'port': port,
            'type': type
        }
    result['servers'] = server
    result['success'] = 1
    return api_process.get_json(result)


def resolve_server(request):
    result = {
        'msgType': 'resolve_server',
        'player_count': 0,
        'max_players': 0,
        'server_name': '',
        'vac_enabled': 0,
        'map': '',
        'timeout': 0,
        'success': 0
    }
    if 'serverip' in request.GET and 'port' in request.GET:
        port = request.GET['port']
        ip = request.GET['serverip']
        if not web_socket.is_number(port):
            return api_process.get_json(result)
        try:
            a2s = valve.source.a2s.ServerQuerier((ip, int(port)))
            info = a2s.info()
        except:
            result['timeout'] = 1
            return api_process.get_json(result)
        result['success'] = 1
        result['player_count'] = info['player_count']
        result['max_players'] = info['max_players']
        result['server_name'] = info['server_name']
        result['vac_enabled'] = info['vac_enabled']
        result['map'] = info['map']
    return api_process.get_json(result)
