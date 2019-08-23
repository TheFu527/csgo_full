#!/bin/bash
su
apt-get update
apt-get install python3
apt-get install python3-pip
python3 -m pip install redis
python3 -m pip install channels
python3 -m pip install django
python3 -m pip install pysocks
python3 -m pip install requests 
python3 -m pip install requests[socks] 
python3 -m pip install django-steamauth 
python3 -m pip install python-valve
python3 -m pip install pymysql
python3 -m pip install gevent
python3 -m pip install baidu-aip
