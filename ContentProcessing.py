import json
import requests
import time

with open("./set.json", "r", encoding="utf-8") as setting:  # 读取长期保存的设置
    set_info = setting.read()
    setdir = json.loads(set_info)
    user_api = setdir["chat_url"]
    user_key = setdir["chat_key"]
    user_chat_model = setdir["chat_model"]
    absolute_path= setdir["absolute_path"]


with open("./系统提示词.txt", "r", encoding="utf-8") as setting:
    system_prompt = setting.read()


headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + user_key
}

memory = ""


class ContentProcessing:
    def __init__(self, system_prompt=system_prompt):
        self.system_prompt = system_prompt
        self.long_term_memory = []  # 存储历史摘要
        self.short_term_memory = []  # 存储原始对话
        self.SHORT_MEMORY_LIMIT = 20  # 触发摘要的消息条数

    def add_message(self, role, content):
        """添加新消息到短期记忆，自动触发摘要"""
        self.short_term_memory.append({"role": role, "content": content})

        # 达到限制时生成摘要
        if len(self.short_term_memory) >= self.SHORT_MEMORY_LIMIT:
            self.summarize_memory("")

    def summarize_memory(self,who):
        global memory
        """使用大模型生成摘要"""
        # 构造摘要请求
        data={
            "model": user_chat_model,
            "messages":[
                {"role": "system", "content": "你是一个高效的摘要生成器"},
                {"role": "user", "content":
                    f"请将以下对话浓缩为保持核心信息的摘要（保留数字、关键实体和结论）内容控制在100字以内：\n"
                    f"{self.short_term_memory}"}],
            "stream": True,
        }
        # 调用API生成摘要
        response = requests.post(url=user_api, headers=headers, stream=True, data=json.dumps(data))
        lines = response.text.strip().split("\n")
        # 遍历每一行
        summary=""
        for line in lines:
            if line.startswith("data: "):
                json_str = line[6:]
                if json_str == "[DONE]":
                    continue
                try:
                    data = json.loads(json_str)
                    if "choices" in data and len(data["choices"]) > 0:
                        if "delta" in data["choices"][0] and "content" in data["choices"][0]["delta"]:
                            summary += data["choices"][0]["delta"]["content"]
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误: {e}")
        print(summary)
        if who == "":
            # 更新记忆系统
            self.long_term_memory.append(summary)
            self.short_term_memory = []  # 清空短期记忆

            # 保留最后3条对话保持连续性（可选）
            if len(self.short_term_memory) > 3:
                self.short_term_memory = self.short_term_memory[-3:]
        if who != "":
            with open(
                    "./memory/wx%s.txt" % who,
                    "a",
                    encoding="utf-8",
            ) as txt:
                timestamp = time.time()
                localtime = time.localtime(timestamp)
                current_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", localtime
                )
                txt.write(current_time + summary + "\n")
    def get_full_context(self):
        """构造完整上下文"""
        context = []

        # 添加系统提示和长期记忆
        if self.long_term_memory:
            long_term_str = "【长期记忆】\n" + "\n".join(
                f"- {summary}" for summary in self.long_term_memory)
            context.append({"role": "system", "content": f"{self.system_prompt}\n{long_term_str}"})
        else:
            context.append({"role": "system", "content": self.system_prompt})

        # 添加短期记忆
        context.extend(self.short_term_memory)
        return context

    def query_model(self, user_input):
        """完整的请求流程"""
        # 添加用户输入
        self.add_message("user", user_input+"【回答用户问题前必须思考】")
        messages = self.get_full_context()
        with open("record_talk.txt","a", encoding="utf-8") as txt:
            txt.write(user_input + "\n")
            txt.write(json.dumps(messages, ensure_ascii=False) + "\n")

        print(messages)
        data = {
            "model": user_chat_model,
            "messages": messages,
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

        # 添加助手回复
        self.add_message("assistant", assistant_reply)
        return assistant_reply
