import requests
import json
from urllib import parse
import os
from urllib.parse import urlparse


def search_bilibili_videos(keyword, page=1, page_size=10, order='totalrank'):
    """
    通过关键词搜索B站视频
    :param keyword: 搜索关键词
    :param page: 页码（默认第1页）
    :param page_size: 每页数量（默认10条）
    :param order: 排序方式（默认totalrank综合排序）
      可选参数:
        - totalrank 综合排序
        - click 最多点击
        - pubdate 最新发布
        - dm 最多弹幕
        - stow 最多收藏
    :return: 包含视频信息的列表
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "Referer": "https://www.bilibili.com/",
        "Origin": "https://www.bilibili.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "cookie": "buvid4=6EA0DE30-0936-BDD0-6109-3CA7F5B023B781499-024010612-jkaxalXiQPg32MPHDUeIkg%3D%3D; DedeUserID=1858299186; DedeUserID__ckMd5=b5321366086f7318; enable_web_push=DISABLE; header_theme_version=CLOSE; buvid_fp_plain=undefined; CURRENT_BLACKGAP=0; LIVE_BUVID=AUTO9317328011296423; PVID=1; fingerprint=637ccb413c8e1be3ede37917c276ee3d; buvid_fp=637ccb413c8e1be3ede37917c276ee3d; _uuid=F8F87BC6-B229-6E16-19BB-B310D95FF832856629infoc; CURRENT_QUALITY=80; home_feed_column=5; buvid3=D5CBA1FC-AA46-F522-E1F8-33BEED27FDC572623infoc; b_nut=1739278972; browser_resolution=1488-738; enable_feed_channel=ENABLE; SESSDATA=a7e1c481%2C1757497642%2Ce16ef%2A32CjD8GRolHuqSCsCmiEn-gIKLlC_CQ-TrIHMap9ZUE0t7XTpEWxgA78IWWZjJQISXh9YSVjBGNklKUnZQR2RHRTNMYVF0UnlqazQxU3JjcGJxRktOVDBDaVc1UDdJRjFUTERaam1jRWxpMWVLVGpaZHREMVh0c2w5TTVlWXZKUVlpT21OUUdHVHNRIIEC; bili_jct=8d2fce0d6ab77879fe1c43f6c589987f; sid=6cg7dzgr; rpdid=|(ukmR|)|mJY0J'u~RkumYlu); bp_t_offset_1858299186=1045237848338333696; b_lsid=87C252109_195A353494C; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDI0NjIyMDYsImlhdCI6MTc0MjIwMjk0NiwicGx0IjotMX0.aU-DAdG8EwSG6xNqYpDkD8W6vcnUWK418aO3y-t-7vA; bili_ticket_expires=1742462146; CURRENT_FNVAL=4048"
    }

    # 编码关键词
    encoded_keyword = parse.quote(keyword)

    api_url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={encoded_keyword}&page={page}&page_size={page_size}&order={order}"

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data["code"] == 0:
            video_list = []
            for item in data["data"]["result"]:
                video_info = {
                    "title": item["title"].replace("<em class=\"keyword\">", "").replace("</em>", ""),
                    "up主": item["author"],
                    "播放量": item["play"],
                    "弹幕量": item["danmaku"],
                    "时长": item["duration"],
                    "发布时间": item["pubdate"],
                    "视频链接": f"https://www.bilibili.com/video/{item['bvid']}",
                    "封面图": item["pic"],
                    "综合得分": item["rank_score"]
                }
                video_list.append(video_info)
            return video_list
        else:
            print(f"搜索失败：{data['message']}")
            return None

    except Exception as e:
        print(f"请求异常：{str(e)}")
        return None




def save_image_from_url(url, save_dir='./images', filename=None):
    """
    通过URL保存图片到本地
    :param url: 图片URL地址
    :param save_dir: 保存目录（默认当前目录下的images文件夹）
    :param filename: 自定义文件名（默认使用URL中的文件名）
    :return: 保存后的完整文件路径
    """
    try:
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)

        # 设置请求头（模拟浏览器访问）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

        # 发送HTTP GET请求
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()  # 检查HTTP错误

        # 自动识别文件名和格式
        if not filename:
            # 从URL中提取文件名
            path = urlparse(url).path
            filename = os.path.basename(path)

            # 处理无扩展名的情况
            if '.' not in filename:
                # 根据Content-Type自动添加扩展名
                content_type = response.headers.get('content-type', '').split('/')[-1]
                if content_type in ['jpeg', 'png', 'gif', 'webp']:
                    filename = f'image.{content_type}'
                else:
                    filename = 'image.jpg'  # 默认格式

        # 构建保存路径
        save_path = os.path.join(save_dir, filename)

        # 分块写入文件（适用于大文件）
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 过滤保持连接的空白块
                    f.write(chunk)

        print(f"图片已保存至：{os.path.abspath(save_path)}")
        return save_path

    except requests.exceptions.RequestException as e:
        print(f"下载失败：{str(e)}")
        return None
    except IOError as e:
        print(f"文件写入失败：{str(e)}")
        return None

def result(keyword):
    # 基本搜索
    search_word = keyword.strip()
    results = search_bilibili_videos(search_word, page_size=20)

    if results:
        print(f"\n找到 {len(results)} 条结果：")
        for idx, video in enumerate(results[:5], 1):  # 显示前5条结果
            print(f"\n【结果{idx}】")
            print(f"标题：{video['title']}")
            print(f"UP主：{video['up主']}")
            print(f"播放：{video['播放量']} | 时长：{video['时长']}")
            print(f"链接：{video['视频链接']}")

        # 保存完整结果
        with open(f"./B站搜索/bilibili_search_{search_word}.json", "w", encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n完整结果已保存至：bilibili_search_{search_word}.json")