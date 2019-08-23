from time import ctime
import socket
import threading
import time
import datetime
import hashlib
import random
import base64
from Crypto.Cipher import AES
aes_key = "apffwetyhjyrtsfd"
aes_iv = b'gfdartgqhjkuyrlp'
def add_to_16(text):
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')
def encrypt(text):
    key = aes_key.encode('utf-8')
    mode = AES.MODE_CBC
    iv = aes_iv
    text = add_to_16(text)
    cryptos = AES.new(key, mode, iv)
    cipher_text = cryptos.encrypt(text)
    return base64.b64encode(cipher_text)
def decrypt(text):
    key = aes_key.encode('utf-8')
    iv = aes_iv
    mode = AES.MODE_CBC
    cryptos = AES.new(key, mode, iv)
    #text = add_to_16(text)
    plain_text = cryptos.decrypt(base64.b64decode(text))
    return bytes.decode(plain_text).rstrip('\0')
def SendPacket(client_handle,msg):
    #client_handle.send(encrypt(msg))
    try:
        client_handle.send(encrypt(msg))
    except:
        client_handle.close()
def ProcessData(client_handle,Msg):
    Msg = str(base64.b64decode(Msg),'utf-8')
    msg = Msg[0:6]
    if msg.find('0x4000') != -1:
        report_info = Msg[6:]
        # [0]event_id [1]process_id [2]base_address [3]region_size [4]other_data [5]event_sig
        report_Data = report_info.split("|");
        event_id = report_Data[0]
        process_id = report_Data[1]
        base_address = report_Data[2]
        region_size = report_Data[3]
        other_data = report_Data[4]
        event_sig = str(base64.b64decode(report_Data[5]),'utf-8')
        print("One Report InComing: EventID: " + event_id + " processID: " + process_id + " addr: " + base_address + " size: " + region_size + " other_data: " + other_data + " sig: " + event_sig)
def ServerThread(csgo_client):
    Trust_This_Client = False
    Trust_Key = "0x1337_huoji"
    Hashed = "?"
    clientName = csgo_client.getpeername()
    print ('一个客户端已经连接: ',clientName)
    while True:
        try:
            recv_data = csgo_client.recv(1024)
        except:
            print ('客户端强制断开!: ',clientName)
            csgo_client.close()
            break
        if recv_data:
            try:
                recv_data_decode = recv_data.decode('gbk')
                recv_data_decode = decrypt(recv_data_decode)
            except:
                print ('出现问题,强制断开客户端!: ',clientName)
                csgo_client.close()
                break
            print('收到的信息：',recv_data_decode)
            if not Trust_This_Client:
                if recv_data_decode.find('0x6666') != -1:
                    Md5HashShit = str(str(time.time()) + str(random.uniform(10, 20))).encode('gbk')
                    Hashed = hashlib.md5(Md5HashShit).hexdigest()
                    #csgo_client.send(Hashed.encode('gbk'))
                    SendPacket(csgo_client,Hashed)
                    print ("开始验证客户端身份:",Trust_Key)
                    continue
                Trust_Key = hashlib.md5(str(Hashed + Trust_Key).encode('gbk')).hexdigest()
                print ("Trust_Key:",Trust_Key)
                if recv_data_decode.find(Trust_Key) != -1:
                    Trust_This_Client = True
                    print ('得到一个信任客户端: ',recv_data_decode)
                    SendPacket(csgo_client,"TRUST")
                    #csgo_client.send("TRUST".encode('gbk'))
                else:
                    print ('客户端不受信任,已经断开连接: ',recv_data_decode)
                    csgo_client.close()
                    break
                continue
            else:
                 ProcessData(csgo_client,recv_data_decode)
        if not recv_data:
            print ("客户端",csgo_client.getpeername(),"断开连接!")
            csgo_client.close()
            break
def start_server():
    try:
        while True:
            tcp_socket_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket_host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            tcp_socket_host.bind(('', 6666))
            tcp_socket_host.listen(128)
            csgo_client, addr_client = tcp_socket_host.accept()
            threading.Thread(target=ServerThread, args=(csgo_client,)).start()
    except:
        pass
    
if __name__ == '__main__':
    start_server()
