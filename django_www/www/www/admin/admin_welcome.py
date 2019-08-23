from django.http import HttpResponse
from django.shortcuts import render, redirect
import platform
import django
from www import GlobalVar

# 不用自带的orm因为mysql版本兼容问题太复杂


def getMysqlVersion():
    return GlobalVar.runSQL("select version()")[0][0]


def getRegisterUsers():
    return GlobalVar.runSQL("SELECT COUNT(id) FROM userdata")[0][0]


def getServers():
    return GlobalVar.runSQL("SELECT COUNT(*) FROM matchserver")[0][0]


def getMatchs():
    return GlobalVar.runSQL("SELECT COUNT(*) FROM matching")[0][0]


def getBannedPlayer():
    return GlobalVar.runSQL("SELECT COUNT(*) FROM userdata WHERE `banned` = 1")[0][0]


def getInviteCode():
    return GlobalVar.runSQL("SELECT COUNT(*) FROM invitecode")[0][0]


def main(request, index_path):
    context = {}
    context['system'] = platform.platform()
    context['django_version'] = "DJANGO" + str(django.VERSION)
    context['mysqlVersion'] = str(getMysqlVersion())
    context['RegisterUsers'] = str(getRegisterUsers())
    context['ServerNumbers'] = str(getServers())
    context['MatchingNum'] = str(getMatchs())
    context['BannedNum'] = str(getBannedPlayer())
    context['InviteCode'] = str(getInviteCode())
    return render(request, index_path + "/welcome.html", context)
