from django.http import HttpResponse
from django.conf import settings
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import re
import requests
from . import view, GlobalVar
ABSOLUTE_URL = ""
STEAM_LOGIN_URL = 'https://steamcommunity.com/openid/login'


def auth(response_url, use_ssl):
    global ABSOLUTE_URL
    ABSOLUTE_URL = GlobalVar.get_value("g_local_domain")
    protocol_re = re.search('(?:http)', response_url)
    if protocol_re == None or protocol_re.group(0) == None:
        protocol = "http"
        if use_ssl:
            protocol = "https"
        response_url = "{0}://{1}{2}".format(protocol,
                                             ABSOLUTE_URL, response_url)

    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": response_url,
        "openid.realm": response_url,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select"
    }

    response = HttpResponse()
    response['Location'] = "{0}?{1}".format(STEAM_LOGIN_URL, urlencode(params))
    response['Content-Type'] = 'application/x-www-form-urlencoded'
    response.status_code = 302
    return response


def get_uid(results):
    results = dict(results)
    # 这样写有bug漏洞可以让用户随意绑定id,但是国内gfw屏蔽然后不走socket代理的话也只能这样了、
    # 其实这个漏洞毫无软用.除了绑定特定用户的id去恶心人之外毫无软用
    try:
        steam_full_url = results['openid.claimed_id']
        if steam_full_url:
            uid_re = re.search(
                'https://steamcommunity.com/openid/id/(\d+)', results['openid.claimed_id'][0])
            if uid_re != None or uid_re.group(1) != None:
                return uid_re.group(1)
    except:
        return False
    # args = {
    #    'openid.assoc_handle': results['openid.assoc_handle'][0],
    #    'openid.signed': results['openid.signed'][0],
    #    'openid.sig': results['openid.sig'][0],
    #    'openid.ns': results['openid.ns'][0]
    # }

    #s_args = results['openid.signed'][0].split(',')

    # for arg in s_args:
    #    itemArg = 'openid.{0}'.format(arg)
    #    if results[itemArg] not in s_args:
    #        args[itemArg] = results[itemArg]

    # print(args)
    #args['openid.mode'] = 'check_authentication'
    #request = view.http_request('POST', STEAM_LOGIN_URL, args, True)
    #request = requests.post(STEAM_LOGIN_URL, args)
    # request.connection.close()

    # if re.search('is_valid:true', request.text):
    #    uid_re = re.search(
    #        'https://steamcommunity.com/openid/id/(\d+)', results['openid.claimed_id'][0])
    #    if uid_re != None or uid_re.group(1) != None:
    #        return uid_re.group(1)
    #    else:
    #        return False
    # else:
    #    return False


def RedirectToSteamSignIn(response_url, use_ssl):
    import sys
    print >> sys.stdout, "Warning! `RedirectToSteamSignIn` and `GetSteamID64` methods are DEPRECATED. Please use `auth` and `get_uid` instead."
    return auth(response_url, use_ssl)


def GetSteamID64(results):
    import sys
    print >> sys.stdout, "Warning! `RedirectToSteamSignIn` and `GetSteamID64` methods are DEPRECATED. Please use `auth` and `get_uid` instead."
    return get_uid(results)
