import requests#http请求
import json#json数据处理
import urllib.request
import time#延时
import websocket#ws接口链接
import base64#请求体编码
import threading
import queue
from pygments import highlight#高亮
from pygments.lexers import JsonLexer#高亮
from pygments.formatters import TerminalFormatter#高亮
from colorama import init, Fore, Back, Style#高亮
import urllib.request
from mutagen.mp3 import MP3

def get_audio_duration(url):
    # 下载音频文件
    audio_file, headers = urllib.request.urlretrieve(url)
    
    # 获取音频文件的时长
    audio = MP3(audio_file)
    duration = audio.info.length
    
    return duration

#这里是语音回复的时长计算代码，用于拓展回复
'''
url = ""
audio_duration = get_audio_duration(url)
print(f"音频时长：{audio_duration} 秒")
'''

lingpai='0f2de7ac66727cd9f561f6abf3f1e202c5a06c2ae4'#换为你的白名单机器人令牌
pdid=433212507046281216#默认回复频道id，代码中为自动识别，可不填

init(autoreset=True)    #  初始化，并且设置颜色设置自动恢复
def addmsg(msg, color="white"):
    if color == "white":
        print(msg)
    elif color == "red":
        print("\033[31m" + msg + "\033[39m")
    elif color == "yellow":
        print("\033[33m" + msg + "\033[39m")
    elif color == "green":
        print("\033[32m" + msg + "\033[39m")
    elif color == "aqua":
        print("\033[36m" + msg + "\033[39m")

def colorprint(smg2,pcolor):
    if pcolor=='red':
      print(Fore.RED + smg2)
    elif pcolor=='bandg':
      print(Back.GREEN + smg2)
    elif pcolor=='d':
      print(Style.DIM + smg2)
    # 如果未设置autoreset=True，需要使用如下代码重置终端颜色为初始设置
    #print(Fore.RESET + Back.RESET + Style.RESET_ALL)  autoreset=True
    
def colorize_json(smg2,pcolor=''):
    json_data=smg2
    try:
        parsed_json = json.loads(json_data)  # 解析JSON数据
        formatted_json = json.dumps(parsed_json, indent=4)  # 格式化JSON数据

        # 使用Pygments库进行语法高亮
        colored_json = highlight(formatted_json, JsonLexer(), TerminalFormatter())

        print(colored_json)
    except json.JSONDecodeError as e:
        print(json_data)

false=False
data_queue = queue.Queue()
def on_message(ws, message):
    # 处理接收到的消息
    addmsg('收到消息',color='green')
    colorize_json(message)
    message=json.loads(message)
    if message["action"] =="push":#检测是否为消息
        if message["data"]["author"]["bot"] == false:#避免回复自己消息
            content = json.loads(message["data"]["content"])
            if "${@!448828939389894656}" in content['text']:#这里一定要换为你机器人的@消息段，否则将不能正常回复，格式:${@!你机器人的长id}
                #text=json.loads(content)
                print(content['text'])
                print(content['text'][23:])
                chatmessage=requests.get('https://api.lolimi.cn/api/ai/a?key=&msg='+content['text'][23:], stream=True)#获取第三方API的回复，注意：key参数请前往https://api.lolimi.cn/获取
                chatmessage=json.loads(chatmessage.text)
                print(chatmessage)
                url='https://a1.fanbook.mobi/api/bot/'+lingpai+'/sendMessage'
                headers = {'content-type':"application/json;charset=utf-8"}
                jsonfile=json.dumps({
                "chat_id":int(message["data"]["channel_id"]),
                "text": chatmessage['data']['output'],
                "reply_to_message_id":int(message["data"]["message_id"])
                })
                print(jsonfile)
                postreturn=requests.post(url,data=jsonfile,headers=headers)
                colorize_json(smg2=postreturn.text,pcolor='d')
def on_error(ws, error):
    # 处理错误
    addmsg("发生错误:"+str(error),color='red')
def on_close(ws):
    # 连接关闭时的操作
    addmsg("连接已关闭",color='red')
def on_open(ws):
    # 连接建立时的操作
    addmsg("连接已建立",color='green')
    # 发送心跳包
    def send_ping():
        print('发送：{"type":"ping"}')
        ws.send('{"type":"ping"}')
    send_ping()  # 发送第一个心跳包
    # 定时发送心跳包
    def schedule_ping():
        send_ping()
        # 每25秒发送一次心跳包
        websocket._get_connection()._connect_time = 0  # 重置连接时间，避免过期
        ws.send_ping()
        websocket._get_connection().sock.settimeout(70)
        ws.send('{"type":"ping"}')
    websocket._get_connection().run_forever(ping_interval=25, ping_payload='{"type":"ping"}', ping_schedule=schedule_ping)
# 替换成用户输入的BOT令牌
lingpai = lingpai
url = f"https://a1.fanbook.mobi/api/bot/{lingpai}/getMe"
# 发送HTTP请求获取基本信息
response = requests.get(url)
data = response.json()
def send_data_thread():
    while True:
        # 在这里编写需要发送的数据
        time.sleep(25)
        ws.send('{"type":"ping"}')
        addmsg('发送心跳包：{"type":"ping"}',color='green')
if response.ok and data.get("ok"):
    user_token = data["result"]["user_token"]
    device_id = "your_device_id"
    version_number = "1.6.60"
    super_str = base64.b64encode(json.dumps({
        "platform": "bot",
        "version": version_number,
        "channel": "office",
        "device_id": device_id,
        "build_number": "1"
    }).encode('utf-8')).decode('utf-8')
    ws_url = f"wss://gateway-bot.fanbook.mobi/websocket?id={user_token}&dId={device_id}&v={version_number}&x-super-properties={super_str}"
    threading.Thread(target=send_data_thread, daemon=True).start()
    # 建立WebSocket连接
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
else:
    addmsg("无法获取BOT基本信息，请检查令牌是否正确。",color='red')

#这里是发送音频的拓展代码
'''
xx='{"type": "voice","url": "","second": '+str(int(audio_duration))+',"isRead": false}'

url='https://a1.fanbook.mobi/api/bot/'+lingpai+'/sendMessage'
headers = {'content-type':"application/json;charset=utf-8"}
jsonfile=json.dumps({
"chat_id":int(pdid),
"text": xx
})
postreturn=requests.post(url,data=jsonfile,headers=headers)
colorize_json(smg2=postreturn.text,pcolor='d')
'''