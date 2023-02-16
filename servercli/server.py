import json
import warnings
import pyshorteners as shr  #网址URL缩短

import websocket
from bs4 import BeautifulSoup

from httpcli.everyday_news import *
from httpcli.http_server import *
from httpcli.openai import *

# 读取本地的配置文件
current_path = os.path.dirname(__file__)
config_path = os.path.join(current_path, "../config/config.ini")
config = configparser.ConfigParser()  # 类实例化
shortener = shr.Shortener() # 类实例化（网址URL缩短）
config.read(config_path, encoding="utf-8")
ip = config.get("server", "ip")
port = config.get("server", "port")
admin_id = config.get("server", "admin_id")
menu = config.get("preset_reply","menu")
help = config.get("preset_reply","help")
video_list_room_id = config.get("server", "video_list_room_id")
blacklist_room_id = config.get("server", "blacklist_room_id")

# websocket._logging._logger.level = -99
requests.packages.urllib3.disable_warnings()
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

SERVER = f"ws://{ip}:{port}"
HEART_BEAT = 5005
RECV_TXT_MSG = 1
RECV_TXT_CITE_MSG = 49
RECV_PIC_MSG = 3
USER_LIST = 5000
GET_USER_LIST_SUCCSESS = 5001
GET_USER_LIST_FAIL = 5002
TXT_MSG = 555
PIC_MSG = 500
AT_MSG = 550
CHATROOM_MEMBER = 5010
CHATROOM_MEMBER_NICK = 5020
PERSONAL_INFO = 6500
DEBUG_SWITCH = 6000
PERSONAL_DETAIL = 6550
DESTROY_ALL = 9999
JOIN_ROOM = 10000
ATTATCH_FILE = 5003


# 'type':49 带引用的消息
def getid():
    return time.strftime("%Y%m%d%H%M%S")


def send(uri, data):
    base_data = {
        "id": getid(),
        "type": "null",
        "roomid": "null",
        "wxid": "null",
        "content": "null",
        "nickname": "null",
        "ext": "null",
    }
    base_data.update(data)
    url = f"http://{ip}:{port}/{uri}"
    res = requests.post(url, json={"para": base_data}, timeout=5)
    return res.json()


def get_member_nick(roomid, wxid):
    # 获取指定群的成员的昵称 或 微信好友的昵称
    uri = "api/getmembernick"
    data = {"type": CHATROOM_MEMBER_NICK, "wxid": wxid, "roomid": roomid or "null"}
    respJson = send(uri, data)
    return json.loads(respJson["content"])["nick"]


def get_personal_info():
    # 获取本机器人的信息
    uri = "/api/get_personal_info"
    data = {
        "id": getid(),
        "type": PERSONAL_INFO,
        "content": "op:personal info",
        "wxid": "null",
    }
    respJson = send(uri, data)
    if json.loads(respJson["content"])['wx_name']:
        wechatBotInfo = f"""
    
        WechatBot登录信息
    
        微信昵称：{json.loads(respJson["content"])['wx_name']}
        微信号：{json.loads(respJson["content"])['wx_code']}
        微信id：{json.loads(respJson["content"])['wx_id']}
        启动时间：{respJson['time']}
        """
    else:
        wechatBotInfo = respJson
    output(wechatBotInfo)


def get_chat_nick_p(roomid):
    qs = {
        "id": getid(),
        "type": CHATROOM_MEMBER_NICK,
        "content": roomid,
        "wxid": "ROOT",
    }
    return json.dumps(qs)


def debug_switch():
    qs = {
        "id": getid(),
        "type": DEBUG_SWITCH,
        "content": "off",
        "wxid": "ROOT",
    }
    return json.dumps(qs)


def handle_nick(j):
    data = j.content
    i = 0
    for d in data:
        output(f"nickname:{d.nickname}")
        i += 1


def hanle_memberlist(j):
    data = j.content
    i = 0
    for d in data:
        output(f"roomid:{d.roomid}")
        i += 1


def get_chatroom_memberlist():
    qs = {
        "id": getid(),
        "type": CHATROOM_MEMBER,
        "wxid": "null",
        "content": "op:list member",
    }
    return json.dumps(qs)


def get_personal_detail(wxid):
    qs = {
        "id": getid(),
        "type": PERSONAL_DETAIL,
        "content": "op:personal detail",
        "wxid": wxid,
    }
    return json.dumps(qs)


def send_wxuser_list():
    """
    获取微信通讯录用户名字和wxid
    获取微信通讯录好友列表
    """
    qs = {
        "id": getid(),
        "type": USER_LIST,
        "content": "user list",
        "wxid": "null",
    }
    return json.dumps(qs)


def handle_wxuser_list(self):
    output("启动完成")


def heartbeat(msgJson):
    output(msgJson["content"])


def on_open(ws):
    # 初始化
    ws.send(send_wxuser_list())


def on_error(ws, error):
    output(f"on_error:{error}")


def on_close(ws):
    output("closed")

def destroy_all():
    qs = {
        "id": getid(),
        "type": DESTROY_ALL,
        "content": "none",
        "wxid": "node",
    }
    return json.dumps(qs)


# 消息发送函数
def send_msg(msg, wxid="null", roomid=None, nickname="null"):
    # if ".jpg" in msg or ".png" in msg:
    #     msg_type = PIC_MSG
    if roomid:
        msg_type = AT_MSG
    else:
        msg_type = TXT_MSG
    if roomid is None:
        roomid = "null"
    qs = {
        "id": getid(),
        "type": msg_type,
        "roomid": roomid,
        "wxid": wxid,
        "content": msg,
        "nickname": nickname,
        "ext": "null",
    }
    output(f"发送消息: {qs}")
    return json.dumps(qs)


def welcome_join(msgJson):
    output(f"收到消息:{msgJson}")
    if "邀请" in msgJson["content"]["content"]:
        roomid = msgJson["content"]["id1"]
        nickname = msgJson["content"]["content"].split('"')[-2]
    # ws.send(send_msg(f'欢迎新进群的老色批',roomid=roomid,wxid='null',nickname=nickname))


def handleMsg_cite(msgJson):
    # 处理带引用的文字消息
    msgXml = (
        msgJson["content"]["content"]
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
    )
    soup = BeautifulSoup(msgXml, "lxml")
    msgJson = {
        "content": soup.select_one("title").text,
        "id": msgJson["id"],
        "id1": msgJson["content"]["id2"],
        "id2": "wxid_fys2fico9put22",
        "id3": "",
        "srvid": msgJson["srvid"],
        "time": msgJson["time"],
        "type": msgJson["type"],
        "wxid": msgJson["content"]["id1"],
    }
    handle_recv_msg(msgJson)


def handle_recv_msg(msgJson):
    if "wxid" not in msgJson and msgJson["status"] == "SUCCSESSED":
        output(f"消息发送成功")
        return
    output(f"收到消息:{msgJson}")
    msg = ""
    keyword = msgJson["content"].replace("\u2005", "")
    if "@chatroom" in msgJson["wxid"]:
        roomid = msgJson["wxid"]  # 群id
        senderid = msgJson["id1"]  # 个人id
    else:
        roomid = None
        nickname = "null"
        senderid = msgJson["wxid"]  # 个人id
    nickname = get_member_nick(roomid, senderid)
    if roomid: # 这里是群消息的回复
        if keyword == "豆豆在吗":
            msg = "豆豆在的"
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword == "test" and senderid in admin_id.split(","):
            msg = "Server is Online"
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))           
        elif keyword == "菜单" and roomid not in blacklist_room_id.split(","):
            msg = menu.replace(r'\n','\n')
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword == "帮助" and roomid not in blacklist_room_id.split(","):
            msg = help.replace(r'\n','\n')
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword.startswith("豆豆猜拳"):
            if keyword == "豆豆猜拳 我出石头" or keyword == "豆豆猜拳 我出剪刀" or keyword == "豆豆猜拳 我出布" or keyword == "豆豆猜拳，我出石头" or keyword == "豆豆猜拳，我出剪刀" or keyword == "豆豆猜拳，我出布":
                keyword = keyword[7:] #切片，只要出招内容
                msg = Paper_Scissor_Rock(keyword)
            else:
                msg = "\n\n═══🐻 vs. 🧑🏻═══\n\n要玩豆豆猜拳，请发送:\n【豆豆猜拳 我出XX】\n（XX为剪刀/石头/布）"
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword.startswith("豆豆画图"):
            if len(keyword) <= 5:
                msg = "\n\n═════🖌🐻🖌═════\n\n🔲1.使用方法\n发送：[豆豆画图 图片描述]\n举例：\n▫️豆豆画图 一只柴犬正在微笑\n▫️豆豆画图 猫站在长城上\n▫️豆豆画图 rainy city,cyberpunk style,mainly in pink\n\n🔲2.图片清晰度\n▫️默认图片清晰度为256像素，可以在图片描述中附加[size=512]或[size=1024]分别获得512像素与1024像素的清晰度。\n▫️256像素直接返回图片，512像素与1024像素返回储存有图片的网址URL（有效时间1小时）\n\n💡Powered by\n©️ DALL·E·2 @openai.com"
                ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
            else:
                keyword = keyword[5:]   #切片，只要图片描述
                if "size=512" in keyword:
                    keyword = keyword.replace("size=512","")
                    keyword_img_size = "512x512"
                elif "size=1024" in keyword:
                    keyword = keyword.replace("size=1024","")
                    keyword_img_size = "1024x1024"
                else:
                    keyword_img_size = "256x256"    #默认大小为256像素
                img_url = DALLE2_Server(keyword,keyword_img_size)    #从DALLE2获取图片url
                print(img_url)
                if '错误' in img_url or keyword_img_size == "512x512" or keyword_img_size == "1024x1024":
                    if '错误' not in img_url:
                        msg = f'\n\n═════🖌🐻🖌═════\n\n📝描述：{keyword}\n\n⏳URL：网址仅可保留1小时！\n\n{img_url}'
                    else:
                        msg = img_url
                    ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname)) #发送错误信息，或由于尺寸大仅发送url
                else:
                    msg = Imamge_download(img_url,api_token=None)    #下载图片
                    send_img_room(msg, roomid) #发送图片
        #OpenAI关键词触发
        elif keyword.startswith("豆豆"):  
            keyword = keyword.replace("豆豆", "")
            if keyword.startswith(" "):  
                keyword = keyword.replace(" ", "")
            elif keyword.startswith(","):  
                keyword = keyword.replace(",", "")
            elif keyword.startswith("，"):  
                keyword = keyword.replace("，", "")
            else : pass
            msg = OpenaiServer(keyword)
            ws.send(send_msg(msg, wxid=roomid))
        elif "早安" == keyword:
            msg = get_morning_info()
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif "发图" == keyword:
            msg = "D:\\img.png"
            ws.send(send_img_room(msg, roomid))
        elif keyword == "文案" and roomid not in blacklist_room_id.split(","):
            msg = get_chicken_soup()
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword == "彩虹屁":
            msg = get_rainbow_fart()
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword == "舔狗日记":
            msg = get_lick_the_dog_diary()
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword == "啥时放假":
            msg = When_holidays()
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif keyword == "历史上的今天":
            msg = get_history_event_text()
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        elif (
                "查询" in msgJson["content"]
                and "运势" in msgJson["content"]
                and roomid not in blacklist_room_id.split(",")
        ):
            msg = get_constellation_info(msgJson["content"].split("\u2005")[-1])
            ws.send(send_msg(msg, wxid=roomid))       
        # elif (
        #         keyword.startswith("md5解密")
        #         or keyword.startswith("md5")
        #         or keyword.startswith("MD5")
        #         or keyword.startswith("MD5解密")
        # ):
            # msg = get_md5(keyword)
            # if len(msg) > 2:
            #     ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
            # else:
            #     pass
        # elif keyword == "今日新闻" and senderid in admin_id.split(","):
        #     msg = get_history_event()
        #     send_img_room(msg, roomid)
        # elif (keyword == "今日资讯" or keyword == "安全资讯") and senderid in admin_id.split(
        #         ","
        # ):
        #     msg = get_safety_news()
        #     ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        # elif (
        #         keyword == "美女视频" or keyword == "视频" or keyword == "美女"
        # ) and roomid in video_list_room_id.split(","):
        #     msg = get_girl_videos()
        #     send_file_room(msg, roomid)
        # elif "查询" in msgJson["content"] and "天气" in msgJson["content"]:
        #     msg = get_today_weather(msgJson["content"].split("\u2005")[-1])
        #     ws.send(send_msg(msg, wxid=roomid))
        # elif "段子" == keyword:
        #     msg = get_Funny_jokes()
        #     ws.send(send_msg(msg, wxid=roomid))
        # elif "黄历" == keyword:
        #     msg = get_today_zodiac()
        #     ws.send(send_msg(msg, wxid=roomid))
        # elif "@疯狂星期四\u2005" in msgJson["content"] and keyword:
        #     msg = ai_reply(keyword)
        #     ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
        # elif (
        #         "摸鱼日历" == keyword or "摸鱼日记" == keyword
        # ) and roomid not in blacklist_room_id.split(","):
        #     msg = Touch_the_fish()
        #     ws.send(send_msg(msg, wxid=roomid))
        # elif "早报" == keyword or "安全新闻早报" == keyword:
        #     msg = get_freebuf_news()
        #     ws.send(send_msg(msg, wxid=roomid))
        # elif "查询ip" in keyword or "ip查询" in keyword:
        #     ip_list = (
        #         keyword.replace("ip", "")
        #             .replace("查询", "")
        #             .replace(":", "")
        #             .replace(" ", "")
        #             .replace("：", "")
        #     )
        #     reg = "((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}"
        #     ip_result = re.match(reg, str(ip_list))
        #     if ip_result is None:
        #         msg = "请输入ip查询，例：ip查询：127.0.0.1"
        #     elif len(ip_list) > 0 and ip_result.group():
        #         msg = search_ip(ip_result.group())
        #     else:
        #         msg = ""
        #     ws.send(send_msg(msg, wxid=roomid))
        # elif "历史上的今天" == keyword:
        #     msg = get_history_event()
        #     ws.send(send_msg(msg, wxid=senderid))

    else: #个人私聊
        if keyword == "test" and senderid in admin_id.split(","):
            msg = "Server is Online"
            ws.send(send_msg(msg, senderid))
        elif keyword == "菜单" and roomid not in blacklist_room_id.split(","):
            msg = "\n\n1.以【豆豆】开头说一个需求\n→提问ChatGPT\n\n2.发送【早安】\n→获取一句早安心语\n\n3.发送【文案】\n→获取一句朋友圈文案\n\n4.发送【彩虹屁】\n→获取一句彩虹屁\n\n5.发送【舔狗日记】\n→获取一句舔狗日记\n"
            ws.send(send_msg(msg, senderid))
        #OpenAI关键词触发
        elif keyword.startswith("豆豆"):
            msg = OpenaiServer(keyword.replace("豆豆", "")).replace("\n\n", "")
            ws.send(send_msg(msg, senderid))
        elif "早安" == keyword:
            msg = get_morning_info()
            ws.send(send_msg(msg, senderid))    
        elif keyword == "文案" and roomid not in blacklist_room_id.split(","):
            msg = get_chicken_soup()
            ws.send(send_msg(msg, senderid))
        elif keyword == "彩虹屁":
            msg = get_rainbow_fart()
            ws.send(send_msg(msg, senderid))
        elif keyword == "舔狗日记":
            msg = get_lick_the_dog_diary()
            ws.send(send_msg(msg, senderid))
        # elif keyword == "今日新闻":
        #     msg = get_history_event()
        #     send_img_room(msg, senderid)
        # elif keyword == "今日资讯":
        #     msg = get_safety_news()
        #     ws.send(send_msg(msg, roomid=roomid, wxid=senderid))
        # elif keyword == "美女视频" or keyword == "视频" or keyword == "美女":
        #     msg = get_girl_videos()
        #     send_file_room(msg, senderid)
        # elif "查询" in msgJson["content"] and "天气" in msgJson["content"]:
        #     msg = get_today_weather(msgJson["content"].split("\u2005")[-1])
        #     ws.send(send_msg(msg, wxid=senderid))
        # elif "段子" == keyword:
        #     msg = get_Funny_jokes()
        #     ws.send(send_msg(msg, wxid=senderid))
        # elif "黄历" == keyword:
        #     msg = get_today_zodiac()
        #     ws.send(send_msg(msg, wxid=senderid))
        # elif "查询" in msgJson["content"] and "运势" in msgJson["content"]:
        #     msg = get_constellation_info(msgJson["content"].split("\u2005")[-1])
        # elif "摸鱼日历" == keyword or "摸鱼日记" == keyword:
        #     msg = Touch_the_fish()
        #     ws.send(send_msg(msg, wxid=senderid))
        # elif "早报" == keyword or "安全新闻早报" == keyword:
        #     msg = get_freebuf_news()
        #     ws.send(send_msg(msg, wxid=senderid))
        else:
            msg = ai_reply(keyword)
            ws.send(send_msg(msg, wxid=senderid))


def on_message(ws, message):
    j = json.loads(message)
    resp_type = j["type"]
    # switch结构
    action = {
        CHATROOM_MEMBER_NICK: handle_nick,
        PERSONAL_DETAIL: handle_recv_msg,
        AT_MSG: handle_recv_msg,
        DEBUG_SWITCH: handle_recv_msg,
        PERSONAL_INFO: handle_recv_msg,
        TXT_MSG: handle_recv_msg,
        PIC_MSG: handle_recv_msg,
        CHATROOM_MEMBER: hanle_memberlist,
        RECV_PIC_MSG: handle_recv_msg,
        RECV_TXT_MSG: handle_recv_msg,
        RECV_TXT_CITE_MSG: handleMsg_cite,
        HEART_BEAT: heartbeat,
        USER_LIST: handle_wxuser_list,
        GET_USER_LIST_SUCCSESS: handle_wxuser_list,
        GET_USER_LIST_FAIL: handle_wxuser_list,
        JOIN_ROOM: welcome_join,
    }
    action.get(resp_type, print)(j)


# websocket.enableTrace(True)
ws = websocket.WebSocketApp(
    SERVER, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close
)


def bot():
    ws.run_forever()


# 全局自动推送函数
def auto_send_message_room(msg, roomid):
    output("Sending Message")
    data = {
        "id": getid(),
        "type": TXT_MSG,
        "roomid": "null",
        "content": msg,
        "wxid": roomid,
        "nickname": "null",
        "ext": "null",
    }
    url = f"http://{ip}:{port}/api/sendtxtmsg"
    res = requests.post(url, json={"para": data}, timeout=5)
    if (
            res.status_code == 200
            and res.json()["status"] == "SUCCSESSED"
            and res.json()["type"] == 555
    ):
        output("消息成功")
    else:
        output(f"ERROR：{res.text}")


def send_file_room(file, roomid):
    output("Sending Files")
    data = {
        "id": getid(),
        "type": ATTATCH_FILE,
        "roomid": "null",
        "content": file,
        "wxid": roomid,
        "nickname": "null",
        "ext": "null",
    }
    url = f"http://{ip}:{port}/api/sendattatch"
    res = requests.post(url, json={"para": data}, timeout=5)
    if res.status_code == 200 and res.json()["status"] == "SUCCSESSED":
        output("文件发送成功")
    else:
        output(f"ERROR：{res.text}")


def send_img_room(msg, roomid):
    output("Sending Photos")
    data = {
        "id": getid(),
        "type": PIC_MSG,
        "roomid": "null",
        "content": msg,
        "wxid": roomid,
        "nickname": "null",
        "ext": "null",
    }
    url = f"http://{ip}:{port}/api/sendpic"
    res = requests.post(url, json={"para": data}, timeout=5)
    if res.status_code == 200 and res.json()["status"] == "SUCCSESSED":
        output("图片发送成功")
    else:
        output(f"ERROR：{res.text}")
