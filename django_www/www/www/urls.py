from django.urls import path, include, re_path
from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.contrib.staticfiles.views import serve
from aip import AipImageCensor
from . import api_process, web_socket, GlobalVar, view
import redis
GlobalVar._init()
GlobalVar.set_value('g_local_domain', '127.0.0.1:8080')
GlobalVar.set_value('g_server_seckey', 'huoji120')
GlobalVar.set_value('g_mysql_user', 'root')
GlobalVar.set_value('g_mysql_password', '')
GlobalVar.set_value('g_mysql_ip', '127.0.0.1')
GlobalVar.set_value('g_mysql_port', 3306)
GlobalVar.set_value('g_mysql_database', 'test')
# redis:
GlobalVar.set_value('g_redis_ip', '127.0.0.1')
GlobalVar.set_value('g_redis_port', 1060)
GlobalVar.set_value('g_redis_password',
                    'huoji120')
GlobalVar.set_value('g_init_redis', False)
GlobalVar.set_value('g_redis_server', redis.Redis(host=GlobalVar.get_value('g_redis_ip'), port=GlobalVar.get_value(
    'g_redis_port'), password=GlobalVar.get_value('g_redis_password')))

# https://www.vaptcha.com
GlobalVar.set_value('g_vaptcha_id', '0')
GlobalVar.set_value('g_vaptcha_secretkey', '0')
websocket_clients = {}
GlobalVar.set_value('g_websocket_clients', websocket_clients)
# https://console.bce.baidu.com/

GlobalVar.set_value('g_baidu_APP_ID', '0')
GlobalVar.set_value('g_baidu_API_KEY', '0')
GlobalVar.set_value('g_baidu_APP_SECKEY', '0')
GlobalVar.set_value('g_baidu_APP', AipImageCensor(
    GlobalVar.get_value('g_baidu_APP_ID'), GlobalVar.get_value('g_baidu_API_KEY'), GlobalVar.get_value('g_baidu_APP_SECKEY')))
websocket_urlpatterns = [
    path('websocket/room/', web_socket.websocket_main),
]
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
urlpatterns = [
    path('favicon.ico', serve, {'path': 'images/favicon.ico'}),
    path('ha4k1r_admin/', view.admin, name='admin_index'),
    path('bind_steam/', view.bind_steam, name='bind_steam'),
    re_path(r'^$', view.index, name='index'),
    re_path(r'^bind_steamid_process/(?P<key>\w+)/$',
            view.steam_login, name='bing_steam_login'),
    re_path(r'^ha4k1r_admin/(?P<moudle>\w+)/$',
            view.admin_moudle, name='admin_moudle'),
    re_path(r'^api/(?P<moudle>\w+)/$', view.api_main, name='api_index'),
    re_path(r'^player/(?P<playername>\w+)/$', view.player, name='player_info')
]
