HUOJI CSGO对战平台[正在开发]
*注意,本开源项目没有客户端反作弊.有真正实力可以商业化搭建的朋友请联系我 邮箱: root@key08.com
===============
写这个项目的时候初衷是为了提高CSGO的水平,以及让有些人有更多可能.
捐助,你的捐助会让我更有时间开发这个平台:
![image](https://github.com/huoji120/csgo_full/blob/master/pic/alipay.jpg)
功能特点:
 + 5人房间系统
 + 邀请码注册系统
 + 服务端反作弊，检测自瞄、屏蔽透视(透视不能穿墙)
 + 客户端基于VT虚拟化技术的反作弊 *注意,本开源项目没有客户端反作弊
 + 房间聊天系统
 + 天梯排位系统
 + 个人战绩系统
 + 内容审核系统
待完成:
 + 好友系统
 + demo储存与解析系统
 + 紧急关闭系统
> 反作弊系统单独写了一套,不过没有和这个平台对接.基于VT虚拟化技术.留给有实力商业化搭建的朋友.所以暂不开源.
> 这个平台只是写了一个月的demo,商业化搭建的话要重构.个人因为生活原因不能顾及全部.有bug可以发我邮箱改进.

## 搭建:
请耐心打磨。很容易就可以搭建的
## 前期准备:
注册： https://www.vaptcha.com 并且购买VIP服务(连VIP钱都没有谈什么搭建平台?)
注册:  https://console.bce.baidu.com/ 创建内容审核服务
安装electron 并且安装客户端所需依赖项
## 开始搭建
注册新浪云 -> 云应用 -> 创建应用,推荐配置如图:
![image](https://github.com/huoji120/csgo_full/blob/master/pic/1.png)
购买对应的redis和mysql服务:
![image](https://github.com/huoji120/csgo_full/blob/master/pic/2.png)
将代码的 django_www/www/www/url.py里面的mysql配置文件、redis配置、vaptcha、百度ak、服务器通讯密钥(重要)修改为你注册的
将代码的 django_www/EzServer.py 的mysql和redis连接配置也改为和上面一样的东西
![image](https://github.com/huoji120/csgo_full/blob/master/pic/3.png)
进入phpadmin 恢复备份文件 备份文件是 backup.sql
之后修改 client/electron/main.js 的vaptcha_id为你的注册的vaptcha的信息,WebsiteDomain和Domain对应你的域名
修改 django_www/www/www/view.py 里面的admin登陆账号密码(提示: 搜索huoji120)
## 最后一步
进入SAE的LINUX终端 上传你改好的代码,之后执行django/www/install_lib.sh的代码安装python和支持库
利用自带的mint创建后台服务 创建两个EzServer.py与python3 /home/django_www/www/manage.py runserver 0:5050
在客户端目录执行electron --no-sandbox ./ 如果黑屏请加--disable-gpu关掉显卡渲染(白屏黑屏很多时候和显卡有关)
客户端目录有pack.cmd 那是打包命令.
成功:
![image](https://github.com/huoji120/csgo_full/blob/master/pic/4.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/5.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/6.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/7.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/8.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/9.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/10.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/11.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/12.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/13.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/14.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/15.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/16.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/17.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/18.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/19.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/20.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/21.png)
![image](https://github.com/huoji120/csgo_full/blob/master/pic/22.png)
## 最最后一步
上传sourcemod服务器到你的CSGO服务器中
打开sourcemode/addons/cfg/crow.ini文件
修改里面的 服务器id和服务器通讯密钥
访问 http://csgo.applinzi.com/ha4k1r_admin/ 点击增加服务器,填写你刚刚增加的服务器id即可拥有比赛服务器!
run.sh是开服脚本 修改里面的steamkey为你的.放到csgo服务端目录后直接./run.sh即可开服