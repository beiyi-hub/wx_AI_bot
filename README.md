# 简介

本项目是基于wxaotu实现的AI智能体机器人，不需要通过任何复杂的渠道与技术，只需准备一台备用电脑和一个空的微信账号就可以将AI机器人接入微信。
机器人拥有智能断句输出，中短期记忆能力，联网搜索模块，图像识别能力，可以提取或解读图片内容，可以发送本地图片（可以当表情包使用）。
![68e7067bbfa2b4d40cd3b5116ebbcb2](https://github.com/user-attachments/assets/31fd1e78-c70d-48e5-93b0-3397a7b482a0)

# 准备

  ### 1.安装必要的库：
  打开命令行（win+r，输入cmd并回车），先cd到本项目根目录，然后输入以下命令：
  
  pip install -r requirements.txt
  （如有问题，就一个一个进行pip）
  
  ### 2.配置AI大模型与你目标AI的设定
  打开set.json配置信息，添加监听对象，如果当前聊天模型拥有视觉，则recognize_model可以为空。
  ![image](https://github.com/user-attachments/assets/27010bf6-90a1-4ddc-9e50-71e469145c7a)
  推荐以下两个平台获取大模型配置
  
  https://phapi.furina.chat/panel
  或
  https://cloud.siliconflow.cn/i/zp70SCoe
  
  如果连大模型怎么调用api都不清楚，这里就不详细展开了，自行搜索或前往相关平台的开发文档进行了解。
 

  ### 3.添加表情包库（如不需要可以将n改为其他值）
  ![image](https://github.com/user-attachments/assets/d1bed6b0-47fa-45f2-818c-64f86855ff3e)

  每次对话都会根据情绪随机从本地表情包库中选择表情包进行发送

  表情包名字需要以以下情感命名，可以自行修改
  ![image](https://github.com/user-attachments/assets/2d0c2e49-fcdd-4f85-bea4-4c01f1523408)


# 开始

  登录你需要接入AI回复的微信账号，程序会自动搜索监听对象，并打开独立小窗，打开后挂后台即可，
  使用AI触发词测试，正常回复后就可以使用啦，每次唤醒AI，默认回复三次对话（方便控制机器人在群里时是否发言）。

# 补充
  ### 1.在使用搜索时加上“详细”二字可以让AI输出完整搜索内容。
  ### 2.识图时会短暂控制微信自动保存图片，在此期间请不要操作电脑。

# 最后
下面为wxauto项目源地址，如有需要可前往了解学习

[wxauto项目链接](https://github.com/cluic/wxauto)

同时感谢幻日大佬Qbot项目提供的灵感

[Qbot项目链接](https://github.com/TIGillusion/Qbot)

如有发现问题或改进建议，请联系开发者QQ：1901182260

目前为第一版，后续会逐渐加入各种功能。

如果觉得有用还请帮忙点个star啦，拜托这对我真的很有用，感谢支持！
