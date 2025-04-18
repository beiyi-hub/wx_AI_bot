from wxauto import WeChat
import time
import requests
import json
import re
import random
import base64
from zhipuai import ZhipuAI
import threading
from threading import Thread
from bilibili_search import result
from bilibili_search import save_image_from_url
import special
import ContentProcessing

cp = ContentProcessing.ContentProcessing()
lock = threading.Lock()

wx = WeChat()
print('登录成功')


sy_num = 1

print("读取配置文件...")
with open("./set.json", "r", encoding="utf-8") as setting:  # 读取长期保存的设置
    set_info = setting.read()
    setdir = json.loads(set_info)
    user_api = setdir["chat_url"]
    user_key = setdir["chat_key"]
    user_chat_model = setdir["chat_model"]
    trigger_name = setdir["trigger"]
    absolute_path = setdir["absolute_path"]
    recognize_model = setdir["recognize_model"]
    recognize_key = setdir["recognize_key"]
    administrator = setdir["administrator"]
    listen_list = setdir["listen_list"]
    meme = setdir["meme"]


with open("./系统提示词.txt", "r", encoding="utf-8") as setting:
    system_prompt = setting.read()

system = system_prompt


"""
[order]
2. 当需要使用联网搜索功能时，请总结需要搜索内容的关键词，例如查询国内热门的AI大模型，使用以下格式：“#search/[国内 热门 Ai大模型]/”（关键词尽量丰富，详细，具体）联网搜索出来的内容需要精简，不要断句，一次性输出。
3. 当需要使用识图功能时，请使用以下格式：“#recognize#cut#图片地址#cut#”（图片地址请使用图片的绝对路径）。
4. 当有人@你时，你需要回复该时使用以下格式进行回复：“@“sender”回复内容”（sender为向你发送消息者的昵称，现在你需要单独回复他），例如：“@张三 收到请回复#cut#”,平常交流对话不需要使用@。
5. 情分析判断对话内容是否为针对你的，如果与你无关，请不要回复，或回复空内容。如果遇到不知道，不清楚的问题可以委婉的表达，例如：“呜，抱歉呢#cut#咱不是很清楚#cut#咱还在学习”，羊姐叫你闭嘴时，你可以说：“呜呜#cut#好叭，那人家闭嘴好了“并在随后的几次回答中回复空内容，直到羊姐让你说话为止。
 7. 请仔细辨别消息的发送者，例如：“【行己之道】说：抱抱你猫猫”，在这句话中只有最前面的名字“行己之道”才是消息发送者，是消息来源者为准，你只对喵内嘎称呼羊姐，你很纯情，面对其他人的骚扰你需要适当拒绝。
"""
    #5. 你可以使用微信特殊的emoji表情，例如:[旺柴]，[勾引]，[捂脸]，[调皮]，[ok]，[害羞]，[大哭]，[偷笑]，[快哭了]，[右哼哼]，[擦汗]，[疑问]，[嘿哈]，[敲打]。回复时如果需要使用表情，请自由在其中选择,但请不要每句话都使用，尽可能少的使用emoji表达你的情绪。




def filtration(content):
    if "think" in content:
        pattern = r'\```(.*?)\```'
        match = re.search(pattern, content.replace('\n', ''))
        think = match.group(1)
        n = content.replace('\n', '').replace(think, '').replace("```", '')
        return n
    else:
        return content.replace('\n', '')


def get_memory(file_path, keywords, match_n=500, time_n=500, radius=100):
    """
    读取整个文件，搜索关键词，合并重叠文段，并返回两个排序的文段列表：
    1. 包含关键词个数排名前五的文段。
    2. 越靠近文段末尾的排在前面，同样返回五个，且不与第一个列表重复。

    :param file_path: 文件路径
    :param keywords: 关键词列表
    :param radius: 关键词附近要返回的文本字数
    :return: 关键词匹配记忆
    """
    # 读取整个文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write('')
        time.sleep(2)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    # 构建正则表达式，用于匹配任意一个关键词
    keywords_pattern = '|'.join(map(re.escape, keywords))
    matches = list(re.finditer(keywords_pattern, content))

    # 合并重叠的文段
    merged_blocks = []
    for match in matches:
        start_index = max(match.start() - radius, 0)
        end_index = min(match.end() + radius, len(content))
        # 检查是否与现有文段重叠
        overlap = False
        for block in merged_blocks:
            if start_index < block['end'] and end_index > block['start']:
                # 合并文段
                block['start'] = min(start_index, block['start'])
                block['end'] = max(end_index, block['end'])
                block['count'] += 1
                overlap = True
                break
        if not overlap:
            merged_blocks.append({'start': start_index, 'end': end_index, 'count': 1})

    # 提取文段文本并按关键词个数排序
    text_blocks = [{'text': content[block['start']:block['end']], 'count': block['count']} for block in merged_blocks]
    sorted_by_count = sorted(text_blocks, key=lambda x: x['count'], reverse=True)[:5]

    # 提取文段文本并按文段末尾位置排序
    text_blocks = [{'text': content[block['start']:block['end']], 'end': block['end']} for block in merged_blocks]
    sorted_by_end = sorted(text_blocks, key=lambda x: x['end'], reverse=True)

    # 移除与按关键词个数排序的文段重复的部分
    non_duplicate_sorted_by_end = [block for block in sorted_by_end if
                                   block['text'] not in [b['text'] for b in sorted_by_count]][:5]

    main_text = ''
    for per_text in non_duplicate_sorted_by_end:
        main_text += "--%s\n" % per_text["text"]
        if len(main_text) > match_n:
            break

    for per_text in sorted_by_count:
        main_text += "--%s\n" % per_text["text"]
        if len(main_text) > match_n + time_n:
            break
    return main_text[:match_n + time_n + 200]

record_numer=0
def post_AI(who,msg):
    global record_numer
    print("---------------------------即将执行AI回复请求--------------------------")
    reply = cp.query_model(msg)
    record_numer += 1
    if record_numer > 20:
        record_numer = 0
        cp.summarize_memory(who)
    if reply == "" or len(reply) > 400:
        reply = cp.query_model(msg)
    print("---------------------------AI回复请求完成--------------------------")
    return reply





def recognize_img(res_content,img_file):
    with open(img_file, 'rb') as img_file:
        img_base = base64.b64encode(img_file.read()).decode('utf-8')
    try:
        client = ZhipuAI(api_key="%s" % recognize_key)  # 填写自己的APIKey
        try:
            response = client.chat.completions.create(
                model="%s" % recognize_model,  # 填写需要调用的模型名称
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": img_base
                                }
                            },
                            {
                                "type": "text",
                                "text": res_content
                            }
                        ]
                    }])
            image_res = "%s" % response.choices[0].message.content
        except Exception as e:
            print(e)
            image_res = "图片识别失败"
            pass
        time.sleep(2)
        response2 = client.chat.completions.create(
            model=user_chat_model,  # 请填写您要调用的模型名称
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",
                 "content": res_content + "我向你发了张图片，因为你看不到，我就将内容总结给你了，现在请你就该图片内容，对我做出回应，内容限制在15字以内" + image_res},
            ],
            stream=True,
        )
        processed_d_data2 = ''
        for chunk in response2:
            processed_d_data2 += chunk.choices[0].delta.content
        print("已读取图片信息:%s" % image_res)
        print("已读取图片分析信息:%s" % processed_d_data2)
        return image_res, processed_d_data2
    except Exception as e:
        url = user_api
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + user_key
        }
        print("即将调用识图")
        data = {
            "model": user_chat_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",
                 "content": [
                     {"type": "text",
                      "text": system_prompt + "用户给你发送了一张图片，请你分析后做出回应（系统提示）"},
                     {"type": "image_url",
                      "image_url": {
                          "url": f"data:image/png;base64,{img_base}"
                      }}]}],
            "stream": True,
        }
        processed_d_data1 = ''
        try:
            response = requests.post(url, headers=headers, json=data)
            a = json.loads(response.text)
            print(a)
            lines = response.text.strip().split("\n")
            for line in lines:
                if line.startswith("data: "):
                    # 去掉 "data: " 前缀
                    json_str = line[6:]
                    # 如果是 "[DONE]"，跳过
                    if json_str == "[DONE]":
                        continue
                    try:
                        data = json.loads(json_str)
                        # 检查是否有 content 字段
                        if "choices" in data and len(data["choices"]) > 0:
                            if "delta" in data["choices"][0] and "content" in data["choices"][0]["delta"]:
                                processed_d_data1 += data["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError as e:
                        print(f"JSON 解析错误: {e}")
            print(processed_d_data1)
            pattern = r'\```(.*?)\```'
            match = re.search(pattern, processed_d_data1.replace('\n', ''))
            think = match.group(1)
            n = processed_d_data1.replace('\n', '').replace(think, '').replace("```", '')
            print(n)
            return n
        except Exception as e:
            print(e)
            return "哎呀，服务器出了点故障，等一下下"





def networking(AI_temp_msg):
    def search(query):
        """
        Searches the web for the specified query and returns the results.
        """
        response = requests.get(
            'https://api.openinterpreter.com/v0/browser/search',
            params={"query": query},
        )
        return response.json()["result"]
    pattern = r'\#search/(.*?)\/'
    match = re.search(pattern, AI_temp_msg.replace('\n', ''))
    think = match.group(1)
    s_prompt = think.replace("/", "").replace("#search","").replace("[","").replace("]","")
    search_result = search(s_prompt)
    print(search_result)
    return search_result

def search_bilibili(AI_temp_msg):
    pattern = r'\#bilibili/(.*?)\/'
    match = re.search(pattern, AI_temp_msg.replace('\n', ''))
    think = match.group(1)
    s_prompt = think.replace("/", "").replace("#search","").replace("[","").replace("]","")
    search_result = result(s_prompt)
    with open(f"./B站搜索/bilibili_search_{s_prompt}.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        print(data)
    return data

def analyze(decoded):
    turl = user_api
    print(decoded)
    print("情感分析中，请稍候...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + user_key
    }
    data = {
        "model": user_chat_model,
        "messages": [
            {"role": "user",
             "content": "请使用“得意”，“尴尬”，“记仇”，“开心”，“看戏”，“思考”，'玩手机','听完要死了'其中之一判断以下句子的情感或意图，总结成一个情感，无需做出多余解释。只回复例子中给出的" + decoded},
        ],
        "stream": True,
    }
    response = requests.post(url=user_api, headers=headers, stream=True, data=json.dumps(data))
    if response.status_code != 200:
        response = requests.post(url=user_api, headers=headers, stream=True, data=json.dumps(data))
    lines = response.text.strip().split("\n")
    assistant_reply = ""
    for line in lines:
        if line.startswith("data: "):
            json_str = line[6:]
            if json_str == "[DONE]":
                continue
            try:
                data = json.loads(json_str)
                if "choices" in data and len(data["choices"]) > 0:
                    if "delta" in data["choices"][0] and "content" in data["choices"][0]["delta"]:
                        assistant_reply += data["choices"][0]["delta"]["content"]
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}")
    print(assistant_reply)
    if "think" in assistant_reply:
        try:
            n = filtration(assistant_reply)
            return n
        except Exception as e:
            print(e)
            return "哎呀，服务器出了点故障，等一下下"


def send_meme(who,emotion):
    global meme
    if meme == "true":
        meme = True
    else:
        pass
    try:
        if meme == True:
            files = [f"{absolute_path}\表情包库\%s.png"%emotion]
            if random.randrange(1,3)==2:
                print("即将发送表情包")
                wx.SendFiles(filepath=files, who=who)
    except:
        pass




for i in listen_list:
    wx.AddListenChat(who=i, savepic=False)

wait = 4  # 设置1秒查看一次是否有新消息
record_number=0
record_msg=""
temp_msg = ""
content=""
temp_img=""
temp_msg_list=''
status=True

def main(msgs):
    global temp_msg
    global record_number
    global content
    global temp_img
    global record_msg
    global status
    global start_time
    global temp_msg_list
    global listen_list
    global short_term_memory
    try:
        for chat in msgs:
            who = chat.who  # 获取聊天窗口名（人或群名）
            one_msgs = msgs.get(chat)  # 获取消息内容
            # 回复收到
            for msg in one_msgs:
                msgtype = msg.type  # 获取消息类型
                content = msg.content  # 获取消息内容，字符串类型的消息内容
                sender = msg.sender
                if sender not in ["SYS", "Self"]:
                    a = f'【{sender}】说：{content},'
                    print(a)
                    if msgtype == 'friend' and "微信图片" in content:
                        temp_img = content
                        print(temp_img)
                        print("收到图片")
                    if (trigger_name[0] in content or random.randrange(1, 20) == 0) or (
                            administrator == sender and trigger_name[0] in content) or (
                            administrator == sender and random.randrange(1, 10) == 0):  # 触发AI回复的名字
                        record_number = 1
                    if who == administrator:
                        record_number = 2
                    if "#获取指令" in content and who == administrator:
                        chat.SendMsg(
                            "当前指令列表：\n1.#重置（重置短期记忆）\n2.#继续(继续参与回复)\n3.#休息(停止参与回复)\n4.#获取当前群聊列表")
                    if "#休息" in content and sender == administrator:
                        status = False
                        chat.SendMsg("溜了，溜了")
                    if "#获取当前群聊列表" in content and sender == administrator:
                        chat.SendMsg(
                            f"当前群聊列表{listen_list}\n可以使用以下指令修改群聊列表\n#删除群聊/群聊名\n#添加群聊/群聊名")
                    if "#删除群聊" in content and sender == administrator:
                        listen_list.remove(content.replace(content[:6], ""))
                        wx.RemoveListenChat(who=content[6:])
                        chat.SendMsg(f"已删除群聊/{content[6:]}\n当前群聊列表{listen_list}")
                    if "#添加群聊" in content and sender == administrator:
                        listen_list.append(content.replace(content[:6], ""))
                        wx.AddListenChat(who=content[6:], )
                        chat.SendMsg(f"已添加群聊/{content[6:]}\n当前群聊列表{listen_list}")
                    if "#继续" in content and sender == administrator:
                        status = True
                        chat.SendMsg("我来啦")
                    if "#重置" in content and sender == administrator:
                        cp.short_term_memory = []
                        chat.SendMsg("短期记忆已重置")
                    if ((msgtype == 'friend' and "微信图片" not in content and status == True and record_number > 0) or (
                                 trigger_name[0] in content and status == True)) and "#" not in content:
                        #msg.tickle()
                        record_number -= 1
                        print(record_number)
                        print("好友消息")
                        msg_content_list = []
                        temp_user_msg = content
                        if temp_img != "":
                            msg_content, = post_AI(who, "%s\n以上是历史群聊消息\n下面是用户[%s]对你说的：%s\n%s" % (temp_msg, sender, content, temp_img))
                        if temp_img == "":
                            msg_content = post_AI(who, "%s\n以上是历史群聊消息\n下面是用户[%s]对你说的：%s" % (temp_msg , sender, content))
                        if True:
                            start_time = time.time()
                            if "#voice" in msg_content:
                                print("收到语音")
                                voice_content = filtration(msg_content)
                                to_path = special.voice(voice_content.replace("#voice","").replace("/",""))
                                chat.SendFiles(filepath=to_path)
                                msg_content = ""
                            if "#bilibili" in msg_content:
                                chat.SendMsg("正在搜索bilibili，请耐心等待一下哦")
                                search_data = search_bilibili(filtration(msg_content))
                                if "*" in temp_user_msg:
                                    a = ""
                                    for i in range(5):
                                        a += f"{i + 1}.{search_data[i]['title']}\n"
                                        a += f"{i + 1}.{search_data[i]['视频链接']}\n\n"
                                    chat.SendMsg(a)
                                if "*" not in msg_content:
                                    image_url = search_data[0]["封面图"]
                                    save_path = save_image_from_url("https:" + image_url)
                                    chat.SendFiles(save_path)
                                    chat.SendMsg("视频标题:"+search_data[0]["title"])
                                    time.sleep(2)
                                    print(search_data[0]["视频链接"])
                                    chat.SendMsg(search_data[0]["视频链接"])
                                    #wx.SendUrlCard(search_data[0]["视频链接"],who)
                                # msg_content = post_AI(who, "%s\n[系统提示]说：你已经成功找到用户的需求内容并发送，请你对此做出回复，简短不用断句" % (temp_msg, sender))
                                # if "think" in msg_content:
                                #     msg_content=filtration(msg_content)
                                msg_content=""
                            if "#search" in msg_content:
                                chat.SendMsg("咱得搜一搜，请耐心等待一下哦")
                                search_result = networking(msg_content)
                                if "详细" in temp_user_msg:
                                    chat.SendMsg(search_result)
                                msg_content = post_AI(who,
                                                      "以下是你通过搜索获得的信息，请你根据prompt进行总结回复我：\n%s\n" % search_result)
                            if "#recognize" in msg_content:
                                msg_content = recognize_img(content, temp_img)
                                print("已识别图片")
                                temp_img = ""
                            else:
                                with lock:
                                    if "think" in msg_content:
                                        msg_content = filtration(msg_content)
                                    record_msg = msg_content
                                    msg_content = msg_content.replace(":","").replace(
                                        "：", "").replace("“", "").replace("”", "").replace("#pass#","")
                                    if "cut" in msg_content:
                                        msg_content_list = msg_content.split("#cut#")
                                        len_msg = len(msg_content_list)
                                        print(msg_content_list)
                                        c = 1
                                        while len_msg > 0:
                                            if c == 1:
                                                msg.quote(msg_content_list[-len_msg].replace("\"", ""))
                                                c -= 1
                                            else:
                                                chat.SendMsg(msg_content_list[-len_msg].replace("\"", ""))
                                            len_msg -= 1
                                    if "cut" not in msg_content:
                                        msg.quote(msg_content.replace("\"", ""))
                                    emotion = analyze(msg_content)
                                    send_meme(who,emotion)
                        print("------------------------结束一轮对话----------------------------")
                    else:
                        if len(temp_msg) >= 300:
                            temp_msg = temp_msg[-100:]
                        else:
                            temp_msg += a
                        print("未触发回复")
                print("未获取新消息")
        time.sleep(wait)
    except Exception as e:
        print(e)
        pass


active = True
start_time= time.time()
temp_time= time.time()

def main2():
    global url1
    global start_time
    global headers1
    global a
    global status
    a=True
    while active==True:
        current_time = time.time()
        time.sleep(5)
        if time.strftime("%H", time.localtime()) == "21" and a == False:
            a=True
            print("今日新闻")
            content = networking("今日新闻")
            processed_d_data1 = post_AI(administrator, content + "今天是%s,这是今日的新闻，你现在想总结给用户，不要做多余解释(系统提示音)" % time.strftime("%Y-%m-%d",
                                                                                                          time.localtime()))
            try:
                if "think" in processed_d_data1:
                    pattern = r'\```(.*?)\```'
                    match = re.search(pattern, processed_d_data1.replace('\n', ''))
                    think = match.group(1)
                    n = processed_d_data1.replace('\n', '').replace(think, '').replace("```", '')
                    print(n)
                else:
                    n = processed_d_data1.replace('\n', '')
                msg_content_list = n.split("#cut#")
                len_msg = len(msg_content_list)
                print(msg_content_list)
                while len_msg > 0:
                    wx.SendMsg(msg_content_list[-len_msg].replace("\"\"",""), "悠月纱(¬◡¬)✧")
                    len_msg -= 1
            except Exception as e:
                print(e)
        elif time.strftime("%H", time.localtime()) == "08" and a==True:
            f"现在是早上了，请你向{administrator}问候早安，自行组织语言(系统提示音)"
            a=False
            print("早安")
            processed_d_data1 = post_AI(administrator,f"现在是早上了，请你向{administrator}问候早安，自行组织语言(系统提示音)")
            try:
                if "think" in processed_d_data1:
                    pattern = r'\```(.*?)\```'
                    match = re.search(pattern, processed_d_data1.replace('\n', ''))
                    think = match.group(1)
                    n = processed_d_data1.replace('\n', '').replace(think, '').replace("```", '')
                    print(n)
                else:
                    n = processed_d_data1.replace('\n', '')
                msg_content_list = n.split("#cut#")
                len_msg = len(msg_content_list)
                print(msg_content_list)
                while len_msg > 0:
                    wx.SendMsg(msg_content_list[-len_msg].replace("我说",""),administrator)
                    len_msg -= 1
            except Exception as e:
                print(e)


def main3():
    global  msgs
    global temp_msgs
    temp_msgs = []
    while 1:
        try:
            msgs = wx.GetListenMessage()  # 获取监听到的消息
            if msgs == None:
                continue
        except:
            continue
        Thread(target=main, args=(msgs,)).start()



def start_threaded_tasks():
    thread1 = threading.Thread(target=main2)
    thread2 = threading.Thread(target=main3)

    thread2.start()
    thread1.start()

    thread2.join()
    thread1.join()

if __name__ == "__main__":
    start_threaded_tasks()



