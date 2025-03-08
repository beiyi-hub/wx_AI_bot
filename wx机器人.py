from wxauto import WeChat
import time
import requests
import jieba.analyse
import json
import re
import random
import os
import base64
from zhipuai import ZhipuAI
import threading
from threading import Thread



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
    system_prompt = setdir["system_prompt"]
    trigger_name = setdir["trigger"]
    absolute_path= setdir["absolute_path"]
    recognize_model = setdir["recognize_model"]
    recognize_key= setdir["recognize_key"]
    listen_list= setdir["listen_list"]


if sy_num == 1:
    system = system_prompt+"""
    [order]
    1. 使用以下格式进行回复，例如：我说：“咲子酱，你好呀”，你回答：“你好鸭/今天也要活力满满哦”这样的格式进行断句，注意！“/”代替。进行断句“，”不断句。
    2. 当需要使用联网搜索功能时，请总结需要搜索内容的关键词，例如查询国内热门的AI大模型，使用以下格式：“#search/国内 热门 Ai大模型/”（关键词尽量丰富，详细，具体）。
    3. 当需要使用识图功能时，请使用以下格式：“#recognize/图片地址/”（图片地址请使用图片的绝对路径）。
    4. 当有人对你提出指定问题时，你需要回复该sender时使用以下格式：“@“sender”回复内容”（sender为向你发送消息者的昵称，现在你需要单独回复他），例如：“@张三 收到请回复/”平常交流不需要使用@。
    """
    #5. 你可以使用微信特殊的emoji表情，例如:[旺柴]，[勾引]，[捂脸]，[调皮]，[ok]，[害羞]，[大哭]，[偷笑]，[快哭了]，[右哼哼]，[擦汗]，[疑问]，[嘿哈]，[敲打]。回复时如果需要使用表情，请自由在其中选择,但请不要每句话都使用，尽可能少的使用emoji表达你的情绪。





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


def memory(who,sender,msg,AI_msg):
    with open(
            "./memory/wx%s.txt" %who,
            "a",
            encoding="utf-8",
    ) as txt:
        timestamp = time.time()
        localtime = time.localtime(timestamp)
        current_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", localtime
        )
        txt.write(
            "[%s]%s:%s。" % (current_time,sender,msg)
        )
        txt.write(
            "\n你回复：%s\n\n"
            % AI_msg
        )
    temp_memory.append("{\"user_content\":\"[%s]%s:%s\",\"AI_content\":\"%s\"}" % (current_time,sender,msg,AI_msg))
    print(temp_memory)

def merge_contents(data):
    # 初始化一个新的列表来存储处理后的数据
    data = [data[0]] + [{"role": "user", "content": " "}] + data[1:]
    new_data = []
    # 用于临时存储连续相同role的内容
    temp_content = ""
    # 上一个role的值
    prev_role = None

    for item in data:
        current_role = item['role']
        current_content = item['content']

        # 如果当前content为空，则将其改为空格
        if not current_content.replace(" ", ''):
            if current_role == "user":
                current_content = "[特殊消息]"
            else:
                current_content = "呜呜，遇到未知错误..."

        # 如果当前role与上一个role相同，则合并content
        if current_role == prev_role:
            temp_content += current_content
        else:
            # 如果临时内容不为空，则将其作为一个新条目添加到新数据列表中
            if temp_content:
                new_data.append({'role': prev_role, 'content': temp_content})
            # 更新临时内容和上一个role的值
            temp_content = current_content
            prev_role = current_role

    # 添加最后一个临时内容（如果有）
    if temp_content:
        new_data.append({'role': prev_role, 'content': temp_content})
    return new_data

def post_AI(who,msg):
    global temp_memory
    print("即将执行AI回复请求")
    # message=[]
    # message.append({"role": "user", "content": msg})
    turl = user_api
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + user_key
    }
    keywords = jieba.analyse.extract_tags(msg, topK=5)
    s_memory = get_memory("./memory/wx%s.txt" %who, keywords)
    temp_memory_content=""
    if len(temp_memory) >=5:
        temp_memory=temp_memory[-5:]
    for i in temp_memory:
        temp_memory_content+=i+"\n"
    print(s_memory)
    print("-----------------------------记忆收集完成-------------------------------")
    data = {
        "model": user_chat_model,
        #"messages": merge_contents([{"role": "system", "content":system +"[memory](模糊 无时效性)\n%s\n" % s_memory }]+ message),
        "messages": [{"role": "system", "content":system + "[memory](模糊 无时效性)\n%s\n" % s_memory+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+msg},
                     {"role": "user", "content":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+temp_memory_content+msg}],
        "stream": False,
    }
    response = requests.post(turl, headers=headers, json=data)
    print(response.text)
    if response.status_code == 200:
        print("请求成功")
    #print(response.text)
    temp_tts_list = []
    processed_d_data1 = ''
    try:
        a = json.loads(response.text)
        for i in a["choices"]:
            processed_d_data1 += i["message"]["content"]
            print(processed_d_data1)
        if "think" in processed_d_data1:
            try:
                pattern = r'\```(.*?)\```'
                match = re.search(pattern, processed_d_data1.replace('\n', ''))
                think = match.group(1)
                n = processed_d_data1.replace('\n', '').replace(think, '').replace("```", '')
                print(n)
                return n
            except Exception as e:
                print(e)
                return "哎呀，服务器出了点故障，等一下下"
        else:
            n = processed_d_data1.replace('\n', '')
            return n
    except Exception as e:
        print("发生错误：", e)
    print(processed_d_data1)



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
                {"role": "system", "content": system + "[memory](模糊 无时效性)\n%s\n" % memory},
                {"role": "user",
                 "content": [
                     {"type": "text",
                      "text": system_prompt + "用户给你发送了一张图片，请你分析后做出回应（系统提示）"},
                     {"type": "image_url",
                      "image_url": {
                          "url": f"data:image/png;base64,{img_base}"
                      }}]}],
            "stream": False,
        }
        processed_d_data1 = ''
        try:
            response = requests.post(url, headers=headers, json=data)
            a = json.loads(response.text)
            print(a)
            for i in a["choices"]:
                processed_d_data1 += i["message"]["content"]
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
    s_prompt = AI_temp_msg.replace("/", "").replace("#search","")
    search_result = search(s_prompt)
    print(search_result)
    return search_result

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
             "content": "请使用“无情感”，“开心”，“生气”，“难过”，“吃惊”，'冷漠','疑惑'，‘慌乱’，‘否认’，‘无语’其中之一判断以下句子的情感或意图，总结成一个情感，无需做出解释。只回复情感，两到三个字" + decoded},
        ],
        "stream": False,
    }
    processed_d_data1 = ''
    response = requests.post(turl, headers=headers, json=data)
    a = json.loads(response.text)
    print(a)
    for i in a["choices"]:
        processed_d_data1 += i["message"]["content"]
        print(processed_d_data1)
    if "think" in processed_d_data1:
        try:
            pattern = r'\```(.*?)\```'
            match = re.search(pattern, processed_d_data1.replace('\n', ''))
            think = match.group(1)
            n = processed_d_data1.replace('\n', '').replace(think, '').replace("```", '')
            print(n)
            return n
        except Exception as e:
            print(e)
            return "哎呀，服务器出了点故障，等一下下"
    res_content1 = response.text
    parsed_data = json.loads(res_content1)
    # 提取 content 字段的值
    content = parsed_data["choices"][0]["message"]["content"]
    res_content2 = content
    print(content)
    return res_content2

def send_meme(who,emotion):
    files = [f"{absolute_path}\迷迷的表情包库\%s.gif"%emotion]
    if random.randrange(1,3)==2:
        print("即将发送表情包")
        wx.SendFiles(filepath=files, who=who)





for i in listen_list:
    wx.AddListenChat(who=i, savepic=True)

wait = 4  # 设置1秒查看一次是否有新消息
record_number=0
record_msg=""
temp_msg = []
content=""
temp_img=""
temp_memory=["",""]

status=True
def main():
    global record_number
    global content
    global temp_img
    global record_msg
    global status
    global start_time
    global temp_memory
    try:
        msgs = wx.GetListenMessage()   # 获取监听到的消息
        for chat in msgs:
            who = chat.who  # 获取聊天窗口名（人或群名）
            one_msgs = msgs.get(chat)  # 获取消息内容
            # 回复收到
            for msg in one_msgs:
                msgtype = msg.type  # 获取消息类型
                content = msg.content  # 获取消息内容，字符串类型的消息内容
                sender = msg.sender
                record_msg=""
                if msgtype == 'friend' and "微信图片" in content:
                    temp_img=content
                    print(temp_img)
                    print("收到图片")
                if f"@{trigger_name}" in content:
                    record_number = 3
                if trigger_name in content or random.randrange(1,10)==0:         #触发AI回复的名字
                    record_number = 3
                if msgtype == 'friend' and msgtype!='sys'and record_number>0 and "微信图片" not in content and status==True:
                    status=False
                    print(f'【{sender}】：{content}')
                    record_number-=1
                    print("好友消息")
                    msg_content_list=[]
                    if temp_img !="":
                        msg_content = post_AI(who, "%s说：%s\n%s" % (sender, record_msg+content, temp_img))
                    if temp_img == "":
                        msg_content = post_AI(who, "%s说：%s" % (sender, record_msg+content))
                    if "/" not in msg_content:                     #使用/对回复内容进行分割，并依次断句输出
                        chat.SendMsg(msg_content)
                    else:
                        start_time = time.time()
                        if record_msg!=msg_content:
                            if "think" in msg_content:
                                keyword = "```"
                                pattern = f"{keyword}(.*?)```"
                                temp_msg = msg_content.replace("\n", "")
                                match = re.search(pattern, temp_msg)
                                think = match.group(1)
                                temp_msg = temp_msg.replace(think, "").replace("```", "")
                                msg_content=temp_msg
                            record_msg = msg_content
                            if "#search" in msg_content:
                                search_result = networking(msg_content)
                                if "详细" in msg_content:
                                    chat.SendMsg(search_result)
                                msg_content = post_AI(who,"以下是你通过搜索获得的信息，请你根据prompt进行总结回复我：\n%s\n" % search_result)
                            if "#recognize" in msg_content:
                                msg_content= recognize_img(content, temp_img)
                                print("已识别图片")
                                temp_img=""
                            msg_content_list = msg_content.split("/")
                            len_msg = len(msg_content_list)
                            print(msg_content_list)
                            while len_msg > 0:
                                chat.SendMsg(msg_content_list[-len_msg])
                                len_msg -= 1
                                time.sleep(random.randrange(1,5))
                            # emotion=analyze(msg_content)
                            # send_meme(who,emotion)
                        memory(who, sender,content, msg_content)          #将消息记录到本地，作为记忆以供后续使用
                    print("------------------------结束一轮对话----------------------------")
                else:
                    print("未触发回复")
        time.sleep(wait)
    except Exception as e:
        print(e)
        print("未获取新消息")
        pass

active = True
start_time= time.time()

def main2():
    global url1
    global start_time
    global headers1
    global a
    global status
    a=True
    while active==True:
        current_time = time.time()
        goal_time= current_time - start_time
        time.sleep(5)
        if goal_time >= 8:
            status=True
        elif time.strftime("%H", time.localtime()) == "21" and a==False:
            a=True
            print("今日新闻")
            content=networking("%s今日新闻"%time.strftime("%Y-%m-%d", time.localtime()))
            data = {
                "model": user_chat_model,
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": system + "\n" + content+"今天是%s,这是今日的新闻，请你总结给用户，不要做多余解释(系统提示音)"%time.strftime("%Y-%m-%d", time.localtime())
                    }
                ],
                "max_tokens": 500
            }
            url = user_api
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + user_key
            }
            processed_d_data1 = ''
            try:
                response = requests.post(url, headers=headers, json=data)
                a = json.loads(response.text)
                print(a)
                for i in a["choices"]:
                    processed_d_data1 += i["message"]["content"]
                    print(processed_d_data1)
                if "think" in processed_d_data1:
                    pattern = r'\```(.*?)\```'
                    match = re.search(pattern, processed_d_data1.replace('\n', ''))
                    think = match.group(1)
                    n = processed_d_data1.replace('\n', '').replace(think, '').replace("```", '')
                    print(n)
                else:
                    n = processed_d_data1.replace('\n', '')
                msg_content_list = n.split("/")
                len_msg = len(msg_content_list)
                print(msg_content_list)
                while len_msg > 0:
                    wx.SendMsg(msg_content_list[-len_msg], "Phantasm AI微信交流群")
                    len_msg -= 1
            except Exception as e:
                print(e)
        elif time.strftime("%H", time.localtime()) == "08" and a==True:
            a=False
            print("早安")
            data = {
                "model": user_chat_model,
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": system + "\n" +"%s现在是早上了，你想向你的北颐哥哥问候早安，请你自行组织语言(系统提示音)"
                    }
                ],
                "max_tokens": 500
            }
            url = user_api
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + user_key
            }
            processed_d_data1 = ''
            try:
                response = requests.post(url, headers=headers, json=data)
                a = json.loads(response.text)
                print(a)
                for i in a["choices"]:
                    processed_d_data1 += i["message"]["content"]
                    print(processed_d_data1)
                if "think" in processed_d_data1:
                    pattern = r'\```(.*?)\```'
                    match = re.search(pattern, processed_d_data1.replace('\n', ''))
                    think = match.group(1)
                    n = processed_d_data1.replace('\n', '').replace(think, '').replace("```", '')
                    print(n)
                else:
                    n = processed_d_data1.replace('\n', '')
                msg_content_list = n.split("/")
                len_msg = len(msg_content_list)
                print(msg_content_list)
                while len_msg > 0:
                    wx.SendMsg(msg_content_list[-len_msg],"Phantasm AI微信交流群")
                    len_msg -= 1
            except Exception as e:
                print(e)


def main3():
    while 1:
        try:
            main()
        except:
            continue

def start_threaded_tasks():
    thread1 = threading.Thread(target=main2)
    thread2 = threading.Thread(target=main3)

    thread2.start()
    thread1.start()

    thread2.join()
    thread1.join()

if __name__ == "__main__":
   start_threaded_tasks()



