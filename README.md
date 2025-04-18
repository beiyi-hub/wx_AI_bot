# 🤖 wx_AI_bot - 智能微信聊天机器人
# 介绍
![License](https://img.shields.io/badge/Version-1.0.0-blue) 
![Python](https://img.shields.io/badge/Python-3.8%2B-green)

基于Windows微信客户端的AI对话机器人，集成**TIG系列专业角色扮演模型**，支持联网搜索/B站视频解析/长短期记忆/语音合成等前沿功能，打造拟人化交互体验。

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

## 🌟 核心功能

### 🧠 智能对话系统
- **多场景触发机制**  
  `@机器人` / `关键词触发` / `随机互动` / `管理员介入` 多种响应模式
- **敏感内容过滤**  
  通过`pass`指令主动规避敏感话题
- **记忆管理系统**  
  `#重置` 指令可清除短期记忆（操作不可逆）
- **自定义AI人设**
 在角色提示词.txt文件中可以自定义AI角色设定，让AI的更符合你的想法，更个性化。

### 🔍 智能搜索系统
| 功能类型       | 能力说明                                                                 |
|----------------|--------------------------------------------------------------------------|
| **基础搜索**   | 实时新闻/百科查询/天气检索等常规搜索                                     |
| **B站搜索**    | 视频封面自动下载+链接解析，`*`符号触发多结果展示                         |
| **数据存储**   | 搜索结果自动保存至`B站搜索`文件夹                                        |

### 🎭 趣味交互
- **表情包系统**  
  支持情绪关键词匹配自定义表情库（可在set.json配置中禁用）
- **定时消息**  
  预设时间主动发送提醒/问候消息

## 🔊 语音合成配置指南

### 环境部署步骤
1. 下载 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 并解压
2. 准备参考音频文件（建议30s以上清晰人声）
3. 修改 `special.py` 中 `voice()` 函数的音频路径
4. 启动SoVITS后端服务

### 预训练模型资源
```plaintext
链接：https://www.123pan.com/s/UHp9-kqi8H.html  
（由B站大佬【白菜工厂1145号员工】提供）
```
> 📌 建议通过[B站教程](https://search.bilibili.com/all?keyword=SoVITS)学习模型训练

## 大模型API秘钥获取平台
前往该平台获取模型秘钥[幻宙 Phantasm API](https://phapi.furina.junmatec.cn/register?aff=QGjz)，注册完成后在主页添加令牌，选择TIG-system即可，随后复制秘钥到set.json文件中添加即可使用。
TIG系列模型由幻宙团队开发，模型目前仍在推广期，欢迎加入API平台官方QQ群610949175交流反馈。

## 🎮 指令手册

| 指令                        | 功能说明                          | 作用范围   |
|----------------------------|-----------------------------------|-----------|
| `#获取指令`                | 显示所有可用指令                  | 私聊      |
| `#获取当前群聊列表`        | 查看机器人已加入的群组            | 私聊      |
| `#休息` / `#继续`          | 全局暂停/恢复机器人响应           | 全场景    |
| `#重置`                    | 清除短期记忆（谨慎使用）          | 全场景    |

# ⚠️注意！
本程序基于wxauto开发，普通版wxauto在回复时会短暂占用键鼠，在此期间，请不要在微信客户端进行任何操作，会影响机器人回复。当然你也可以选择部署到服务器使用，关于wxauto更多信息可自行学习了解[wxauto项目](https://github.com/cluic/wxauto)

# 最后
感谢幻日大佬的[qbot](https://github.com/TIGillusion/Qbot)项目提供灵感与思路（程序作者为一名高中毕业生，接触编程时间不久，代码可能没有那么优雅，还请谅解）。
如果觉得项目不错，还请不要吝啬你手中的star哦，当然如果能帮助推广宣传那就更好啦（啾咪）❤️

# 使用
1.下载压缩包后，随便找个文件夹解压，随后调用终端输入以下指令安装必要的包（需要配置3.11版本python环境）

'python -m pip install -r requirements.txt'

2.点开set.json填入你获取的模型秘钥以及AI的唤醒词与管理员和默认回复群聊

3.点开系统提示词.txt文件填写修改你的角色人设

4.如有需要配置自定义表情包，不需要的话在set.json中的meme处填写false

5.语音合成详见上文，一般不影响程序运行

**走完以上步骤后即可启动使用啦**

