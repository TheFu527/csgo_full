from www.admin import admin_welcome, admin_room, admin_memberlist, admin_server_manager, admin_match, admin_invitecode
import requests
import socks  # 需要安装：pip install pysocks
import json
import platform
from . import GlobalVar, api_process, steamauth
from urllib import request, parse, error
from urllib.parse import urlsplit, urlparse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from channels.generic.websocket import WebsocketConsumer
from django.views.decorators.csrf import csrf_exempt
requests.packages.urllib3.disable_warnings()
admin_dir = "ha4k1r_admin"


def http_request(method, url, payload, proxie=False):
    request = []
   # print(url)
    head = {}
    head['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    if not proxie:
        if method == 'POST':
            request = requests.post(
                url, data=payload, headers=head, verify=False)
        else:
            request = requests.get(
                url, data=payload, headers=head, verify=False)
    else:
        # 走代理绕过防火墙,这个国内服务器必须设置否则无法绑定steam!
        proxie = {'http': 'socks5://localhost:1080',
                  'https': 'socks5://localhost:1080'}
        if method == 'POST':
            request = requests.post(
                url, data=payload, proxies=proxie, headers=head, verify=False)
        else:
            request = requests.get(
                url, data=payload, proxies=proxie, headers=head, verify=False)
    request.connection.close()
    return request


def auth_send_post(token):
    url = "http://api.vaptcha.com/v2/validate"

    payload = {'id': GlobalVar.get_value('g_vaptcha_id'),
               'secretkey': GlobalVar.get_value('g_vaptcha_secretkey'),
               'token': token
               }
    json_result = http_request('POST', url, payload).json()
    # print(json_result)
    return json_result['success'] == 1 and json_result['score'] > 60 and json_result['msg'] == 'success'


def admin_moudle(request, moudle):
    try:
        if moudle in 'login_auth':
            if request.session.get('admin_login_name', None):
                del request.session['admin_login_name']
            if request.POST and 'json' in request.POST:
                json_result = json.loads(request.POST['json'])
                if auth_send_post(request.POST['auth']):
                    if json_result['username'] in 'huoji' and json_result['password'] in 'huoji120':
                        request.session['admin_login_name'] = json_result['username']
                        return HttpResponse("登陆成功")
            else:
                return redirect("/" + admin_dir)
            return HttpResponse("登陆失败!")
    except:
        return HttpResponse("系统内部错误!")

    if not request.session.get('admin_login_name', None):
        return render(request, admin_dir + "/login.html", {'g_vaptcha_id': GlobalVar.get_value('g_vaptcha_id')})
    if moudle in 'welcome':
        return admin_welcome.main(request, admin_dir)
    if moudle in 'member_list':
        return admin_memberlist.main(request, admin_dir)
    if moudle in 'server_manage':
        return admin_server_manager.main(request, admin_dir)
    if moudle in 'server_manage_casual':
        return admin_server_manager.casual(request, admin_dir)
    if moudle in 'add_server':
        return admin_server_manager.add(request, admin_dir)
    if moudle in 'add_server_casual':
        return admin_server_manager.add_casual(request, admin_dir)
    if moudle in 'admin_room':
        return admin_room.main(request, admin_dir)
    if moudle in 'match_matched':
        return admin_match.matched(request, admin_dir)
    if moudle in 'match_matching':
        return admin_match.matching(request, admin_dir)
    if moudle in 'invitecode_list':
        return admin_invitecode.main(request, admin_dir)
    if moudle in 'invitecode_add':
        return admin_invitecode.add_code(request, admin_dir)


def admin(request):
    if not request.session.get('admin_login_name', None):
        return render(request, admin_dir + "/login.html", {'g_vaptcha_id': GlobalVar.get_value('g_vaptcha_id')})
    context = {}
    context['static_url'] = request.get_host()
    return render(request, admin_dir + "/index.html", context)


def index(request):
    return render(request,  "index/index.html")


def player(request, playername):
    return render(request,  "index/playerdata.html", {'playername': playername})


def bind_steam(request):
    if request.GET:
        if 'key' in request.GET:
            key = request.GET['key']
            data = api_process.process_getdata_by_key(key)
            if not data:
                return HttpResponse('非法访问,请联系管理员')
            return steamauth.auth('/bind_steamid_process/' + key + "/", use_ssl=False)
    return HttpResponse('非法访问,请联系管理员')


def steam_login(request, key):
    steam_uid = steamauth.get_uid(request.GET)
    if not steam_uid:
        return HttpResponse('绑定steaid失败!')
    else:
        data = api_process.process_getdata_by_key(key)
        if not data:
            return HttpResponse('????????!')
        GlobalVar.runSQL(
            'UPDATE userdata SET `SteamID` = %s WHERE `Key` = %s LIMIT 1', (steam_uid, key))
        return HttpResponse('绑定steamid成功!你现在要做的只是关闭这个窗口即可!')


@csrf_exempt
def api_main(request, moudle):
    context = {}
    context['static_url'] = request.get_host()
    return api_process.process(request, moudle)
