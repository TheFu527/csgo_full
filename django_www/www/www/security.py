from aip import AipImageCensor
from . import web_socket, api_process, GlobalVar
import json


def check_iamge(image):
    client = GlobalVar.get_value('g_baidu_APP')
    result = client.faceAudit(image)
    return result['result'][0]['res_code'] == 0
