"""
@Project ：WechatBot 
@File    ：openai.py
@IDE     ：PyCharm 
@Author  ：zhizhuo
@Date    ：2023/2/1 16:03 
"""
import configparser
import os

import openai

from httpcli.output import *

current_path = os.path.dirname(__file__)
config_path = os.path.join(current_path, "../config/config.ini")
config = configparser.ConfigParser()  # 类实例化
config.read(config_path, encoding="utf-8")
openai_key = config.get("apiService", "openai_key")
openai.api_key = openai_key


def OpenaiServer(msg=None):
    print("即将发送给ChatGPT的消息是：",msg)
    try:
        if msg is None:
            output(f'ERROR：msg is None')
            msg = ""
        else:
            start_time = time.time()
            print("正在请求openai.com……")
            question = msg
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=str(msg),
                temperature=0.6,
                max_tokens=600,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            end_time = time.time()
            msg ="Sent："+question[:9]+"…"+"\n"+"Cost："+str(int(end_time-start_time+2))+" seconds\n"+"Reply from ChatGPT：\n\r"
            msg += response.choices[0].text
            # msg += "\n\rCreate by openai server"
            return msg 
    except Exception as e:
        output(f"ERROR：{e.message}")
        msg = e.message
    return msg
