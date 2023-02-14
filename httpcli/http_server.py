import datetime
import os
import re
import requests
from httpcli.output import *
import configparser
import random
import http.client, urllib, json
from zhdate import ZhDate as lunar_date

# 读取本地的配置文件
current_path = os.path.dirname(__file__)
config_path = os.path.join(current_path, "../config/config.ini")
config = configparser.ConfigParser()  # 类实例化
config.read(config_path, encoding="utf-8")
History_text_key = config.get('apiService',"History_text_key")
History_url = config.get("apiService", "history_url")
md5_url = config.get("apiService", "md5_url")
dog_url = config.get("apiService", "dog_url")
fart_url = config.get("apiService", "fart_url")
girl_videos_url = config.get("apiService", "girl_videos_url")
weather_url = config.get("apiService", "weather_url")
smile_url = config.get("apiService", "smile_url")
zodiac_url = config.get("apiService", "zodiac_url")
allow_token = config.get("apiService", "allow_token")
constellation_url = config.get("apiService", "constellation_url")
morning_url = config.get("apiService", "morning_url")
ai_reply_url = config.get("apiService", "ai_reply_url")
after_work_time = config.get("server", "after_work_time")
salary_day = config.get("server", "salary_day")
threatbook_key = config.get("apiService", "threatbook_key")
threatbook_url = config.get("apiService", "threatbook_url")


# 豆豆猜拳 石头剪刀布
def Paper_Scissor_Rock(keyword=None):
    # 创建一个剪刀石头布的列表
    list_game = ["剪刀","石头","布"]
    list_happy = ["😁嘿嘿","😆哈哈","🤣吼吼","🤪略略","😘么么"]
    list_sad = ["😒哼！","😞唉……","😣啊！！","😭呜呜呜","😲啊？？","🤮Tu了","🤡我是消愁","🤬奈奈滴"]
    # 采集玩家的出招
    player = keyword
    print('我出'+player)
    # 电脑随机出招
    computer = random.choice(list_game)
    msg = '\n\n═══🐻 vs. 🧑🏻═══\n\n'
    msg += "🔔豆豆出了"+computer+'\n'

    if player == computer:
        msg += "✳️平局，再来一次吧！"
    elif (player == list_game[0] and computer == list_game[1]) or (player == list_game[1] and computer == list_game[2]) or (player == list_game[2] and computer == list_game[0]):
        msg += f"✅豆豆赢了！\n\n豆豆说：{random.choice(list_happy)}"
    else:
        msg += f"✅你赢了！\n\n豆豆说：{random.choice(list_sad)}"
    return msg

# 获取历史的今天事件（文字版 tianapi.com）
def get_history_event_text():
    output("Get History Today event (text)")
    conn = http.client.HTTPSConnection('apis.tianapi.com')  #接口域名
    # api需要的key、请求的日期
    params = urllib.parse.urlencode({'key':History_text_key,'date':time.strftime('%m%d')})
    headers = {'Content-type':'application/x-www-form-urlencoded'}
    msg = '\n'
    try:
        conn.request('POST','/lishi/index',params,headers)
        tianapi = conn.getresponse()
        result = tianapi.read() # 读取数据
        data = result.decode('utf-8') # 调整编码
        dict_data = json.loads(data).get('result').get('list')  # 从json格式转换为dict格式，并读取数据
        for event in dict_data:
            msg += event.get('lsdate')+'\n'+event.get('title')+'\n\n'
    except Exception as e:
        msg = "历史上的今天接口调用出错，错误信息：{}".format(e)
    return msg    


# 获取历史的今天事件（图片版）
def get_history_event():
    output("Get History Today event")
    try:
        resp = requests.get(
            History_url,
            timeout=5,
            verify=False,
        )
        if resp.status_code == 200:
            path = os.path.abspath("./img")
            img_name = int(time.time() * 1000)
            # 以时间轴的形式给图片命名
            with open(f"{path}\\{img_name}.jpg", "wb+") as f:
                # 写入文件夹
                f.write(resp.content)  # 如果这句话一直报错，很有可能是你的网址url不对
                # 关闭文件夹
                f.close()
            video_path = os.path.abspath(f"{path}\\{img_name}.jpg")
            msg = video_path.replace("\\", "\\\\")
        else:
            msg = "历史上的今天接口调用超时"
    except Exception as e:
        msg = "历史上的今天接口调用出错，错误信息：{}".format(e)
    return msg


# 获取舔狗日记
def get_lick_the_dog_diary():
    output("Get Lick the dog diary")
    msg = '\n'
    try:
        resp = requests.get(
            dog_url,
            timeout=5,
            verify=False,
        )
        if resp.status_code == 200 and resp.json()["code"] == 200:
            msg += resp.json()["newslist"][0]["content"]
        else:
            msg += "舔狗日记接口调用超时"
    except Exception as e:
        msg += "舔狗日记接口调用出错，错误信息：{}".format(e)
    return msg


# 获取今天的天气
def get_today_weather(self):
    output("Get Today Weather")
    try:
        city_list = re.findall("查询(.*?)天气", self)
        if len(city_list) > 0:
            city = city_list[0]
            resp = requests.get(weather_url + str(city), timeout=5, verify=False)
            if resp.status_code == 200 and "errcode" not in resp.text:
                msg = f'今日{city}的天气\n日期：{resp.json()["date"]}\n当前温度：{resp.json()["tem"]}\n最高气温：{resp.json()["tem_day"]}\n最低气温：{resp.json()["tem_night"]}\n风向：{resp.json()["win"]}\n风速：{resp.json()["win_meter"]}\n天气：{resp.json()["wea"]}\n湿度：{resp.json()["humidity"]}\n\nBy zhizhuo\n更新时间：{resp.json()["update_time"]}'
            elif "errcode" in resp.text and resp.json()["errcode"] == 100:
                output(f'天气查询接口出错，请稍后重试,接口状态{resp.json()["errmsg"]}')
                msg = resp.json()["errmsg"].replace("city", "城市中")
            else:
                msg = f"天气查询接口出错，请稍后重试,接口状态{resp.status_code}"
        else:
            msg = "语法错误，请输入查询xx天气"
    except Exception as e:
        output(f"ERROR: {e}")
        msg = "天气查询接口出错，ERROR:{}".format(e)
    return msg


# 获取彩虹屁
def get_rainbow_fart():
    output("Get Rainbow fart")
    msg = '\n'
    try:
        resp = requests.get(
            fart_url,
            timeout=4,
            verify=False,
        )
        if resp.status_code == 200 and resp.json()["code"] == 200:
            msg += resp.json()["newslist"][-1]["content"]
        else:
            msg += "彩虹屁接口调用超时"
    except Exception as e:
        msg += "彩虹屁接口调用出错，错误信息：{}".format(e)
    return msg


# 获取文案
def get_chicken_soup():
    output("Get Chicken soup")
    msg = '\n'
    try:
        resp = requests.get(
            "https://api.oick.cn/dutang/api.php", timeout=5, verify=False
        )
        if resp.status_code == 200:
            msg += resp.text.replace('"', "")
        else:
            msg += "文案接口请求超时"
    except Exception as e:
        msg = "文案接口调用出错，错误信息：{}".format(e)
    return msg


# md5解密接口
def get_md5(self):
    output("Get MD5 Clear")
    try:
        md5_list = self.split(":")
        md5_list = self.split("：")
        md5_list = self.split(" ")
        if len(md5_list) > 1 and len(md5_list[1]) > 5:
            pmd5_url = str(md5_url) + str(md5_list[1])
            resp = requests.get(pmd5_url, timeout=5, verify=False)
            if resp.status_code == 200 and len(resp.json()["result"]) > 0:
                msg = "\n密文：{}\nMD5解密结果为：{}".format(
                    str(md5_list[1]),
                    resp.json()["result"]["{}".format(str(md5_list[1]))],
                )
            elif resp.status_code != 200:
                msg = "MD5解密接口调用超时"
            else:
                msg = "MD5解密失败"
        else:
            msg = "请使用语句md5解密 密文"
            pass
    except Exception as e:
        msg = "PMD5解密接口调用出错，错误信息：{}".format(e)
    return msg


# 获取美女视频接口
def get_girl_videos():
    output("Get Girl Videos")
    try:
        resp = requests.get(girl_videos_url, timeout=5, verify=False)
        if resp.status_code == 200:
            videos_url = re.findall(
                '<video src="(.*?)" muted controls preload="auto"', resp.text, re.S
            )
            if len(videos_url) > 0:
                url = "http:" + str(videos_url[0])
                resp1 = requests.get(url, timeout=5, verify=False)
                path = os.path.abspath("./video")
                videos_name = int(time.time() * 1000)
                # 以时间轴的形式给图片命名
                with open(f"{path}\\{videos_name}.mp4", "wb+") as f:
                    # 写入文件夹
                    f.write(resp1.content)  # 如果这句话一直报错，很有可能是你的网址url不对
                    # 关闭文件夹
                    f.close()
                video_path = os.path.abspath(f"{path}\\{videos_name}.mp4")
                msg = video_path.replace("\\", "\\\\")
            else:
                msg = "ERROR：未识别到URL连接"
                output(msg)
        else:
            msg = "站点状态异常，访问请求：{}".format(resp.status_code)
    except Exception as e:
        output("ERROR：{}".format(e))
        msg = "视频接口调用出错，错误信息：{}".format(e)
    return msg


# 获取搞笑段子
def get_Funny_jokes():
    output("GET Funny jokes")
    try:
        content_num = random.randint(0, 9)
        resp = requests.get(
            smile_url + str(random.randint(1, 8715)), timeout=5, verify=False
        )
        if resp.status_code == 200 and resp.json()["code"] == 1:
            msg = (
                resp.json()["data"]["list"][content_num]["content"]
                + "\n\n更新时间："
                + resp.json()["data"]["list"][content_num]["updateTime"]
            )
        else:
            msg = f"ERROR：接口请求请求异常，接口状态：{resp.status_code},错误信息：{resp.json()['msg']}"
            output(msg)
    except Exception as e:
        output(f"ERROR：{e}")
        msg = f"搞笑段子接口调用出错，ERROR：{e}"
    return msg


# 获取今日黄历
def get_today_zodiac():
    output("GET today zodiac")
    try:
        resp = requests.get(
            zodiac_url + str(time.strftime("%Y%m%d")) + str(allow_token),
            timeout=5,
            verify=False,
        )
        if resp.status_code == 200 and resp.json()["code"] == 1:
            msg = f'当前日期：{resp.json()["data"]["date"]}\n本周第{resp.json()["data"]["weekDay"]}天\n属相：{resp.json()["data"]["chineseZodiac"]}\n节气：{resp.json()["data"]["solarTerms"]}\n农历：{resp.json()["data"]["lunarCalendar"]}\n宜：{resp.json()["data"]["suit"]}\n忌：{resp.json()["data"]["avoid"]}\n今年第{resp.json()["data"]["dayOfYear"]}天\n今年第{resp.json()["data"]["weekOfYear"]}周\n星座：{resp.json()["data"]["constellation"]}\n本月第{resp.json()["data"]["indexWorkDayOfMonth"]}个工作日'
        else:
            msg = f"ERROR：接口请求请求异常，接口状态：{resp.status_code},错误信息：{resp.json()['msg']}"
            output(msg)
    except Exception as e:
        output(f"ERROR：{e}")
        msg = f"搞笑段子接口调用出错，ERROR：{e}"
    return msg


# 获取早安寄语
def get_morning_info():
    output("Get morning info")
    msg = '\n'
    try:
        resp = requests.get(morning_url, timeout=5, verify=False)
        if resp.status_code == 200 and resp.json()["code"] == 200:
            msg += resp.json()["data"]["content"]
        else:
            msg += f"未获取到早安寄语，接口返回信息：{resp.json()}"
    except Exception as e:
        output(f"ERROR：{e}")
        msg += f"早安寄语接口调用出错，ERROR：{e}"
    return msg


# 获取星座运势
def get_constellation_info(self):
    output("Get constellation info")
    msg = "\n"
    try:
        constellation_list = re.findall("查询(.*?)运势", self)
        if len(constellation_list) > 0:
            resp = requests.get(
                constellation_url + constellation_list[0],
                timeout=5,
                verify=False,
            )
            if resp.status_code == 200 and resp.json()["code"] == 200:
                msg = f"星座：{constellation_list[0]}"
                for i in range(0, len(resp.json()["newslist"])):
                    msg = f"\n{resp.json()['newslist'][i]['type']}：{resp.json()['newslist'][i]['content']}"
            else:
                msg = f"ERROR：接口请求请求异常，错误信息：{resp.json()['msg']}"
                output(msg)
        else:
            msg = "语法错误，请输入查询xx座运势"
    except Exception as e:
        output(f"ERROR：{e}")
        msg = f"星座运势接口调用出错，ERROR：{e}"
    return msg


# AI闲聊接口信息
def ai_reply(self):
    output("GET AI Reply")
    try:
        resp = requests.get(str(ai_reply_url) + str(self), timeout=5, verify=False)
        if resp.status_code == 200 and resp.json()["result"] == 0:
            msg = resp.json()["content"]
        else:
            msg = "你消息发送的太频繁了，慢一点"
    except Exception as e:
        output(f"ERROR：{e}")
        msg = f"AI对话机器人接口调用出错，ERROR：{e}"
    return msg


# 计算时间差函数
def diff_day(start_day, end_day):
    start_sec = time.mktime(time.strptime(start_day, "%Y-%m-%d"))
    end_sec = time.mktime(time.strptime(end_day, "%Y-%m-%d"))
    return int((end_sec - start_sec) / 86400)


def diff_hour(start_hour, end_hour):
    start_sec = time.mktime(time.strptime(start_hour, "%Y-%m-%d %H:%M:%S"))
    end_sec = time.mktime(time.strptime(end_hour, "%Y-%m-%d %H:%M:%S"))
    return [
        int((end_sec - start_sec) / 3600),
        int((end_sec - start_sec) / 60) - int((end_sec - start_sec) / 3600) * 60,
    ]


def get_time():
    if time.localtime().tm_hour < 12:
        return "上午好"
    elif time.localtime().tm_hour == 12:
        return "中午好"
    elif 12 < time.localtime().tm_hour < 18:
        return "下午好"
    else:
        return "晚上好"


# 啥时放假
def When_holidays():
    holiday_date_dict = {'Qing_Ming':"2023-04-05",'Lao_Dong':"2023-04-29",'Duan_Wu':"2023-06-22",'Zhong_Qiu':"2023-09-29",'Guo_Qing':"2023-10-01",'Yuan_Dan':"2024-01-01",'Chu_Xi':"2024-02-09"}
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    time_now = time.strftime("%Y-%m-%d")
    msg = f'\n【豆豆摸鱼办】提醒您：\n今天是{time.strftime("%m")}月{time.strftime("%d")}日 {week_list[int(datetime.date.today().isoweekday())-1]}\n════════════\n假期倒计时：\n🌿清明节：'+str(diff_day(time_now, holiday_date_dict.get('Qing_Ming')))+'天\n🛠劳动节：'+str(diff_day(time_now, holiday_date_dict.get('Lao_Dong')))+'天\n🚣‍♀️端午节：'+str(diff_day(time_now, holiday_date_dict.get('Duan_Wu')))+'天\n🥮中秋节：'+str(diff_day(time_now, holiday_date_dict.get('Zhong_Qiu')))+'天\n🇨🇳国庆节：'+str(diff_day(time_now, holiday_date_dict.get('Guo_Qing')))+'天\n💫元〇旦：'+str(diff_day(time_now, holiday_date_dict.get('Yuan_Dan')))+'天\n🏮除〇夕：'+str(diff_day(time_now, holiday_date_dict.get('Chu_Xi')))+'天\n════════════\n加油！打工人！'
    return msg


# 摸鱼日历
def Touch_the_fish():
    # 获取每年除夕的阳历日期
    New_Year = (
        str(int(time.strftime("%Y")) + 1)
        + "-"
        + str(lunar_date(int(time.strftime("%Y")), 12, 30).to_datetime().month)
        + "-"
        + str(lunar_date(int(time.strftime("%Y")), 12, 30).to_datetime().day)
    )
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    time_now = time.strftime("%Y-%m-%d")
    timeNow = time.strftime("%Y-%m-%d %X")
    New_Year_Day = str(int(time.strftime("%Y")) + 1) + "-01-01"
    if int(time.strftime("%d")) > int(salary_day):
        if int(time.strftime("%m")) == 12:
            salary_Day = (
                    str(int(time.strftime("%Y"))+1)
                    + "-01-"
                    + str(salary_day)
            )
        else:
            salary_Day = (
                    str(int(time.strftime("%Y")))
                    + "-"
                    + str(int(time.strftime("%m")) + 1)
                    + "-"
                    + str(salary_day)
            )
    else:
        salary_Day = (
            str(int(time.strftime("%Y")))
            + "-"
            + str(int(time.strftime("%m")))
            + "-"
            + str(salary_day)
        )
    epidemic_Day = "2019-12-16"
    National_Day = str(int(time.strftime("%Y")) + 1) + "-10-01"
    after_work = f"{time_now} {after_work_time}:00"
    if (
        diff_hour(timeNow, after_work)[0] >= 0
        and diff_hour(timeNow, after_work)[1] >= 0
        and int(datetime.date.today().isoweekday()) < 6
    ):
        msg = f'【摸鱼办】提醒您：\n🍁今天是{time.strftime("%m")}月{time.strftime("%d")}日 {week_list[int(datetime.date.today().isoweekday())-1]}\n👨‍💻{get_time()}摸鱼人！工作再累，一定不要忘记喝水哦！希望此刻看到消息的人可以和我一起来喝一杯水。及时排便洗手，记得关门。一小时后我会继续提醒大家喝水，和我一起成为一天喝八杯水的人吧！\n══════════\n🚇距离下班还有：{diff_hour(timeNow, after_work)[0]}小时{diff_hour(timeNow, after_work)[1]}分钟\n💰距离发工资还有：{diff_day(time_now, salary_Day)}天\n🍁距离元旦还有：{diff_day(time_now, New_Year_Day)}天\n🏮距离除夕还有：{diff_day(time_now, New_Year)}天\n🚩距离国庆还有：{diff_day(time_now, National_Day)}天\n⌚距离疫情开始：{diff_day(epidemic_Day, time_now)}天\n══════════\n有事没事起身去茶水间，去厕所，去廊道走走别老在工位上坐着。上班是帮老板赚钱，摸鱼是赚老板的钱！最后，祝愿天下所有摸鱼人，都能愉快的渡过每一天💪'
    elif (
        int(datetime.date.today().isoweekday()) == 6
        or int(datetime.date.today().isoweekday()) == 7
    ):
        msg = "都双休日了还摸什么鱼，快滚去睡觉！"
    else:
        msg = "各部门请注意，下班时间已过！！！请滚，不要浪费电费，记得发日报！\n[Doge] over"
    return msg


# 恶意IP查询
def search_ip(ips):
    output(f"查询ip：{ips}")
    try:

        data = {
            "apikey": threatbook_key,
            "resource": ips,
        }

        resp = requests.post(
            threatbook_url,
            data=data,
            timeout=10,
            verify=False,
        )
        if resp.status_code == 200 and resp.json()["response_code"] == 0:
            # 查风险等级
            sec_level = resp.json()["data"]["{}".format(ips)]["severity"]
            # 查是否恶意IP
            is_malicious = resp.json()["data"]["{}".format(ips)]["is_malicious"]
            # 查可信度
            confidence_level = resp.json()["data"]["{}".format(ips)]["confidence_level"]
            # 查IP归属国家
            country = resp.json()["data"]["{}".format(ips)]["basic"]["location"][
                "country"
            ]
            # 查IP归属省份
            province = resp.json()["data"]["{}".format(ips)]["basic"]["location"][
                "province"
            ]
            # 查IP归属城市
            city = resp.json()["data"]["{}".format(ips)]["basic"]["location"]["city"]
            # 将IP归属的国家、省份、城市合并成一个字符串
            location = country + "-" + province + "-" + city
            # 查威胁类型
            judgments = ""
            for j in resp.json()["data"]["{}".format(ips)]["judgments"]:
                judgments += j + " "
            if is_malicious:
                is_malicious_msg = "是"
            else:
                is_malicious_msg = "否"
            msg = f"===================\n[+]ip：{ips}\n[+]风险等级：{sec_level}\n[+]是否为恶意ip：{is_malicious_msg}\n[+]可信度：{confidence_level}\n[+]威胁类型：{str(judgments)}\n[+]ip归属地：{location}\n更新时间：{resp.json()['data']['{}'.format(ips)]['update_time']}\n==================="
        else:
            msg = f"查询失败，返回信息：{resp.json()['verbose_msg']}"
            output(f"ERROR：{msg}")
    except Exception as e:
        output(f"ERROR: {e}")
        msg = f"查询出错请稍后重试，错误信息：{e}"
    return msg
