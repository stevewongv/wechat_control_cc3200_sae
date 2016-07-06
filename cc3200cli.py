# -*- coding:utf8 -*-
#encoding=utf-8
# import MySQLdb
import hashlib
import web
import time
import os
from lxml import etree
import myfun
import pylibmc
import re
from flask import Flask,jsonify as flask_jsonify, request,g,make_response
# from mysql import get_content
app = Flask(__name__)
app.debug = True
import mysql
# from sae.const import (MYSQL_HOST, MYSQL_HOST_S,
#     MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB
# )

def jsonify(*args, **kwargs):
    response = flask_jsonify(*args, **kwargs)
    if not response.data.endswith(b'\n'):
        response.data += b'\n'
    return response

@app.route('/')
def hello():
    return "Hello, god!"


@app.route('/get',methods=['GET',])#GET
def get():
    Content_res =  mysql.get_content()
    return jsonify(ID=Content_res['ID'],USER_NAME=Content_res['FromUserName'],Content=Content_res['Content'])
# ############################################################################################################
@app.route('/weixin',methods=['GET','POST'])
def weixin():

    token = 'xxxxxxxxxxx' # your token
    query = request.args  # GET 方法附上的参数
    signature = query.get('signature', '')
    timestamp = query.get('timestamp', '')
    nonce = query.get('nonce', '')
    echostr = query.get('echostr', '')
    s = [timestamp, nonce, token]
    s.sort()
    s = ''.join(s)
    if ( hashlib.sha1(s).hexdigest() == signature ):
        return make_response(echostr)

    if request.method == "GET" :
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        # 自己的token
        token = 'HEAVENLYKING'
        list = [token, timestamp, nonce]
        list.sort()
        list=''.join(list)
        sha1 = hashlib.sha1(list)
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
    # sha1加密算法
    # 如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return make_response(echostr)

    if request.method == 'POST':

    # str_xml = web.data()  # 获得post来的数据
        xml = etree.fromstring(request.data)  # 进行XML解析
    # content=xml.find("Content").text#获得用户所输入的内容
        msgType = xml.find("MsgType").text
        fromUser = xml.find("FromUserName").text
        toUser = xml.find("ToUserName").text
        msgId = int(xml.find("MsgId").text)
        mc = pylibmc.Client()
        reply = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
        # response = make_response( reply % (fromUser, toUser, str(int(time.time())), Content ) )
        # response.content_type = 'application/xml'
        # # return response


    # 欢迎订阅
        if msgType == 'event':
            Msgcontent = xml.find("Event").text
            if Msgcontent == 'subscribe':
                replyMsg = u'欢迎,欢迎,热烈欢迎~~,蟹蟹关注么么扎~~,直接输入地址就能查询天气~~,输入含有聊活着打招呼都可以进入聊天模式哟,输入"再见"与天王Say Goodbye~~后期会加入更多功能~~欢迎向我提交bug~~'
                response = make_response( reply % (fromUser, toUser, str(int(time.time())), replyMsg ) )
                return response
            if Msgcontent == "unsubscribe":
                replyMsg = u'还在测试阶段我会努力完善~~谢谢光临~~'
                response = make_response( reply % (fromUser, toUser, str(int(time.time())), replyMsg ) )
                return response

        if msgType == 'text':
            content = xml.find("Content").text  # 获得用户所输入的内容
        #指令内容分析
            if type(content).__name__ == "unicode":
                content = content.encode('UTF-8')
            if re.search('.*?状况', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'state'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n目前的状况"))
                return response
            if re.search('.*?温度', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'tem'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n目前的温度"))
                return response
            if re.search('.*?湿度', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'hum'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n目前的湿度"))
                return response
            if re.search('.*?浇水', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'water'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n正在浇水"))
                return response
            if re.search('.*?开.*?灯', content) or re.search('.*?灯.*?开', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = '1'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n灯已经开启"))
                return response
            if re.search('.*?关.*?灯', content) or re.search('.*?灯.*?关', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = '0'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n灯已经关闭"))
                return response
            if re.search('.*?再见.*?', content):
                mc.delete(fromUser + '_tl')
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u'拜拜~~~'))
                return response
            if re.search('.*?聊.*?', content) or re.search('.*?你好.*?', content) or re.search('.*?您好.*?',
                                                                                            content) or re.search(
                '.*?hi.*?', content) or re.search('.*?hello.*?', content) or re.search('.*?Hi.*?',
                                                                                           content) or re.search(
                '.*?Hello.*?', content):
                mc.set(fromUser + '_tl', 'tl')
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u'你好呀~~~'))
                return response
            mctl = mc.get(fromUser + '_tl')
            if mctl == 'tl':
                tl = myfun.func()
                res = tl.tuling(content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  res))
                return response
            weather = myfun.func()
            Weather_data = weather.Weather(content)
            response = make_response( reply % (fromUser, toUser, str(int(time.time())),  Weather_data))
            return response

        if msgType == 'voice':
            content = xml.find("Recognition").text
            if type(content).__name__ == "unicode":
                content = content.encode('UTF-8')
            if re.search('.*?状况', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'state'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n目前的状况"))
                return response
            if re.search('.*?温度', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'tem'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n目前的温度"))
                return response
            if re.search('.*?湿度', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'hum'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n目前的湿度"))
                return response
            # Watering.humidity()
            if re.search('.*?浇水', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = 'water'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"\n正在浇水"))
                return response
            if re.search('.*?开.*?灯', content) or re.search('.*?灯.*?开', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = '1'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"灯已经开启"))
                return response
            if re.search('.*?关.*?灯', content) or re.search('.*?灯.*?关', content):
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                content = '0'
                mysql.add_data(time_now, msgId, fromUser, msgType, content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u"灯已经关闭"))
                return response
            # Watering.water()
            if re.search('.*?再见.*?', content):
                mc.delete(fromUser + '_tl')
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u'拜拜~~~'))
                return response
            if re.search('.*?聊.*?', content) or re.search('.*?你好.*?', content) or re.search('.*?您好.*?',
                                                                                            content) or re.search(
                '.*?hi.*?', content) or re.search('.*?hello.*?', content) or re.search('.*?Hi.*?',
                                                                                           content) or re.search(
                '.*?Hello.*?', content):
                mc.set(fromUser + '_tl', 'tl')
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  u'你好呀~~~'))
                return response
            mctl = mc.get(fromUser + '_tl')
            if mctl == 'tl':
                tl = myfun.func()
                res = tl.tuling(content)
                response = make_response( reply % (fromUser, toUser, str(int(time.time())),  res))
                return response
            weather = myfun.func()
            Weather_data = weather.Weather(content)
            response = make_response( reply % (fromUser, toUser, str(int(time.time())),  Weather_data))
            return response


if __name__ == '__main__':
    app.run()