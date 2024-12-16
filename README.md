# 简介

本项目是基于wxaotu实现的AI智能体机器人，不需要通过任何复杂的渠道与技术，只需准备一台备用电脑和一个空的微信账号就可以将AI机器人接入微信。
机器人拥有智能断句输出，中短期记忆能力，联网搜索模块，图像识别能力，可以提取或解读图片内容，可以发送本地图片（可以当表情包使用）。
![68e7067bbfa2b4d40cd3b5116ebbcb2](https://github.com/user-attachments/assets/31fd1e78-c70d-48e5-93b0-3397a7b482a0)

# 准备

  ### 1.安装必要的库：
  打开命令行（win+r，输入cmd并回车），先cd到本项目根目录，然后输入以下命令：
  
  pip install -r requirements.txt
  
  ### 2.配置AI大模型与你目标AI的设定
  打开wx机器人.py源代码，在下图位置进行配置
  ![image](https://github.com/user-attachments/assets/26011602-d29b-497f-b148-479ac0dc03b9)
  推荐以下两个平台获取大模型配置
  
  https://bigmodel.cn/console/overview
  或
  https://cloud.siliconflow.cn/i/zp70SCoe（该平台模型更全一点）
  
  如果连大模型怎么调用api都不清楚，这里就不详细展开了，自行百度或前往相关平台的开发文档进行了解。
  
  ### 3.添加监听对象列表
  把你想调用AI回复的群聊或对象加到该监听列表，一定注意名字正确且不重复。
  ![image](https://github.com/user-attachments/assets/8bb81844-7af7-4444-a650-4fb64f310018)

  ### 4.添加表情包库（如不需要可以将n改为其他值）
  ![image](https://github.com/user-attachments/assets/bf512660-8a89-4f6b-b55f-7aa788bb144e)
  每次对话都会从本地表情包库中随机选择表情包进行发送（可以理解为句话）

# 开始

  登录你需要接入AI回复的微信账号，程序会自动搜索监听对象，并打开独立小窗，打开后挂后台即可，
  使用AI触发词测试，正常回复后就可以使用啦，每次唤醒AI，默认回复三次对话。

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
