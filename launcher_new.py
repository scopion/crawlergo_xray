#!/usr/bin/python3
# coding: utf-8
import os
import queue
import simplejson
import threading
import warnings
from fake_useragent import UserAgent
import datetime
import json
import logging
import time
import requests
import subprocess
import pymysql
import hmac
import hashlib
import base64



ua = UserAgent(path="fake_ua.json")
warnings.filterwarnings(action='ignore')
session = requests.session()


def post(data, webhook):
	"""
    发送消息（内容UTF-8编码）
    :param data: 消息数据（字典）
    :return: 返回发送结果
    """
	# data = json.dumps(data)
	try:
		print(data)
		print(webhook)
		response = session.post(webhook, data=data)
		print(response.text)
	except requests.exceptions.HTTPError as exc:
		logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
		raise
	except requests.exceptions.ConnectionError:
		logging.error("消息发送失败，HTTP connection error!")
		raise
	except requests.exceptions.Timeout:
		logging.error("消息发送失败，Timeout error!")
		raise
	except requests.exceptions.RequestException:
		logging.error("消息发送失败, Request Exception!")
		raise
	else:
		try:
			result = response.json()
		except:
			logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
			return {'errcode': 500, 'errmsg': '服务器响应异常'}
		else:
			return result


def is_not_null_and_blank_str(content):
	if content and content.strip():
		return True
	else:
		return False


class FeishuChatbot(object):
	def __init__(self, webhook, secret=None, ):
		super(FeishuChatbot, self).__init__()
		self.headers = {'Content-Type': 'application/json; charset=utf-8'}
		self.times = 0
		self.start_time = time.time()
		self.webhook = webhook
		self.secret = secret
		self.timestamp = int(self.start_time)
		self.string_to_sign = '{}\n{}'.format(self.timestamp, secret)
		self.hmac_code = hmac.new(self.string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
		# 对结果进行base64处理
		self.sign = base64.b64encode(self.hmac_code).decode('utf-8')

	def send_text(self, msg):
		data = {"msg_type": "text", "timestamp": self.timestamp, "sign": self.sign}
		if is_not_null_and_blank_str(msg):
			data["content"] = {"text": msg}
		else:
			logging.error("text类型，消息内容不能为空！")
			raise ValueError("text类型，消息内容不能为空！")
		logging.debug('text类型：%s' % data)
		return post(json.dumps(data), self.webhook)


def getmysqlconn():
	config = {
		'host': '127.0.0.1',
		'port': 3306,
		'user': 'root',
		'passwd': '1n',
		'db': 'dataasset',
		'charset': 'utf8',
		'cursorclass': pymysql.cursors.DictCursor
	}
	conn = pymysql.connect(**config)
	return conn


def getsubdomains(conn):
	cursor = conn.cursor()
	results = ""
	sql = """select domain from subdomainasset where type = 'A' or type = 'CNAME'"""
#	sql = """select domain from subdomainasset where domain like type = 'A' or type = 'CNAME'"""
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
	except:
		# Rollback in case there is any error
		conn.rollback()
		print('select fail,rollback')
	return results


def get_random_headers():
	headers = {'User-Agent': ua.random}

	return headers


def appasset(conn, prodaddress):
	cursor = conn.cursor()
	updateTime = datetime.datetime.now()
	# 数据表加字段
	sql = "insert into appasset(prodaddress,updateTime) values(%s,%s) " \
		  "on duplicate key update prodaddress=VALUES(prodaddress),updateTime=VALUES(updateTime)"
	values = (prodaddress, updateTime)
	try:
		# print 'update product sql start'
		# 执行sql语句
		n = cursor.execute(sql, values)
		# print n
		# 提交到数据库执行
		conn.commit()
	# print ('update dept success')
	except Exception as e:
		print(e)
		# Rollback in case there is any error
		conn.rollback()
		print('update fail,rollback')


def getasset(conn):
	sql = "SELECT * FROM `appasset` where status = 'false'"
	cursor = conn.cursor()
	try:
		# 执行sql语句
		cursor.execute(sql)
		# 提交到数据库执行
		results = cursor.fetchall()
	except:
		# Rollback in case there is any error
		print('select EMPLID fail,rollback')
	# print (len(EMPLIDS))
	return results


def clearcraw():
    try:
        f = open('crawl_result.txt','w')
        f.truncate(0)
    finally:
        f.close()

def savecraw(result):
    try:
        f = open('crawl_result.txt','a')
        f.write(str(result) + '\n')
    finally:
        f.close()

def cleardomain():
    try:
        f = open('sub_domains.txt','w')
        f.truncate(0)
    finally:
        f.close()

def savedomain(subdomain):
    try:
        f = open('sub_domains.txt','a')
        f.write(subdomain + '\n')
    finally:
        f.close()

def geturl(cmd):
    sp = subprocess.Popen(cmd, shell=True)
    return sp.communicate()


def crawlergo(target):
	#cmd = ["./crawlergo", "-c", "/usr/bin/google-chrome","-t", "20","-f","smart","--fuzz-path", "--custom-headers",json.dumps(get_random_headers()),"--push-to-proxy", "http://127.0.0.1:7777/", "--push-pool-max", "10", "--output-mode", "json", target]
	cmd = ["./crawlergo", "-c", "/usr/bin/google-chrome","-m","5","-t", "5","-f","smart", "--push-to-proxy", "http://127.0.0.1:7777/", "--push-pool-max", "3", "--output-mode", "console", target]
	rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print ('正在启动crawlergo爬取'+data1+'链接，请稍等...')
	rsp.communicate()
	savecraw(target)
    #try:
	#	result = simplejson.loads(output.decode().split("--[Mission Complete]--")[1])
	#   print(result)
	#except Exception as e:
	#	print(e)
	print("[crawl ok]")


def rad(data1):
	target = data1
	cmd = ["./rad","--target",target,"--http-proxy","http://127.0.0.1:7777"]
	rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#print ('查漏补缺，启动rad爬取'+data1+'链接，请稍等...')
	rsp.communicate()


if __name__ == '__main__':
	cmd = 'httpx -l sub_domains.txt > targets.txt'
	cmd2 = "echo '' > /opt/crawlergo_x_XRAY/nohup.out"

	geturl(cmd2)
	conn = getmysqlconn()
	cleardomain()
	subdomains = getsubdomains(conn)
	for i in subdomains:
		#print(i)
		subdomain = i.get('domain')
		savedomain(subdomain)
	print("sub_domains")
	geturl(cmd)
	print("targets.txt")
	clearcraw()

	# xray_out = '/opt/crawlergo_x_XRAY/proxy.html'
	# print('xray漏扫结果输出文件位置：'+xray_out)
	# xray_cmd = ["./xray/xray","webscan","--listen","127.0.0.1:7777","--html-output",xray_out]
	# xray_rsp = subprocess.Popen(xray_cmd,shell=False)
	# time.sleep(5)
	file = open("targets.txt")
	# t = threading.Thread(target=request0)
	# t.start()
	for text in file.readlines():
		data1 = text.strip('\n')
		appasset(conn, data1)
		print(data1+"更新数据库")
		#rad(data1)
		#print("rad ok ")
		crawlergo(data1)
	# tclose=1


	webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/7edb5c6d541"
	secret = "64wV1ZdSc"
	xiaoding = FeishuChatbot(webhook, secret=secret)
	at = "<at user_id=\"ou_d1b9e4b325\">名字</at>"

	xray = "/opt/crawlergo_x_XRAY/proxy.html"
	if os.path.exists(xray):
		msg = "xray发现漏洞，请尽快查看处理" + at
	else:
		msg = "域名安全扫描完成，xray扫描未发现漏洞"
	# xiaoding.send_text(msg=msg, is_at_all=True)
	at_mobiles = ['13']
	xiaoding.send_text(msg=msg)
	unrecoed = getasset(conn)
	if len(unrecoed) > 0:
		msg = "存在未备案APP资产，请前往备案" + at
		xiaoding.send_text(msg=msg)
