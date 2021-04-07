# -*- coding:UTF8 -*-
 
import re
import os
import time
import requests
import json
from pprint import pprint
from index_decode import decode_index_data

download_path = './manhua'
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://manga.bilibili.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    "cookie": ""#填写样式 SESSDATA=xxxxxxxxxxxxxxxxxxx; 在浏览器f12打开开发者工具，复制 Application- Cookies - https://www.bilibili.com/ - SESSDATA 进行填写
}
headers_cdn = {
    'Host': 'manga.hdslb.com',
    'Origin': 'https://manga.bilibili.com',
}


def download_manga_all(comic_id: int):
    url = "https://manga.bilibili.com/twirp/comic.v2.Comic/ComicDetail?device=pc&platform=web"
    res = requests.post(url,
                        json.dumps({
                            "comic_id": comic_id
                        }), headers=headers)
    data = json.loads(res.text)['data']
    comic_title = data['title']
    root_path = os.path.join(download_path, comic_title)
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    for ep in data['ep_list']:
        if not ep['is_locked']:
            print('downloading ep:', ep['short_title'], ep['title'])
            download_manga_episode(ep['id'], root_path)
            pass
        pass
    pass


def download_manga_episode(episode_id: int, root_path: str):
    res = requests.post('https://manga.bilibili.com/twirp/comic.v1.Comic/GetEpisode?device=pc&platform=web',
                        json.dumps({
                            "id": episode_id
                        }), headers=headers)
    data = json.loads(res.text)
    # comic_title = data['data']['comic_title']
    short_title = data['data']['short_title']
    # title = comic_title + '_' + short_title + '_' + data['data']['title']
    title = short_title + '_' + data['data']['title']
    comic_id = data['data']['comic_id']
    print('正在下载：', title)

    # 获取索引文件cdn位置
    res = requests.post('https://manga.bilibili.com/twirp/comic.v1.Comic/GetImageIndex?device=pc&platform=web',
                        json.dumps({
                            "ep_id": episode_id
                        }), headers=headers)
    data = json.loads(res.text)
    index_url = 'https://manga.hdslb.com' + data['data']['path']
    print('获取索引文件cdn位置:', index_url)
    # 获取索引文件
    res = requests.get(index_url)
    # 解析索引文件
    pics = decode_index_data(comic_id, episode_id, res.content)
    # print(pics)
    ep_path = os.path.join(root_path, title)
    if not os.path.exists(ep_path):
        os.makedirs(ep_path)
    for i, e in enumerate(pics):
        url = get_image_url(e)
        print(i, url)
        if os.path.exists(os.path.join(ep_path, str(i) + '.jpg'))==False:#检查是否已下载过图片 
            res = requests.get(url)
            with open(os.path.join(ep_path, str(i) + '.jpg'), 'wb+') as f:
                f.write(res.content)
                pass
        else:
            print("发现已下载过图片,跳过下载")
        if i % 4 == 0 and i != 0:
            time.sleep(2)
            pass
        pass
    pass


def get_image_url(img_url):
    # 获取图片token
    res = requests.post('https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken?device=pc&platform=web',
                        json.dumps({
                            "urls": json.dumps([img_url])
                        }), headers=headers)
    data = json.loads(res.text)['data'][0]
    url = data['url'] + '?token=' + data['token']
    return url
    pass


if __name__ == "__main__":
    temp = input("请输入漫画主页链接(https://manga.bilibili.com/detail/mcxxx),要下载付费漫画需要先购买,然后按要求填写main.py第18行,请勿把自己的账号授权交给他人(这个应该不止授权下载付费漫画),但如果出现意外,可以尝试浏览器点登出b站账号看看能不能把授权弄失效:")
    if temp != "":
        temp2=""
        if re.search(r'^[0-9]+$', temp) != None:#输入漫画id可以下载
            pattern = re.compile(r'^[0-9]+$')# 查找数字
            temp2 = pattern.findall(temp)
            print("1")
        elif re.search(r'https:\/\/manga\.bilibili\.com\/mc([0-9]+)', temp) != None:#粘贴漫画主页链接可以下载
            pattern2 = re.compile(r'https:\/\/manga\.bilibili\.com\/mc([0-9]+)')
            temp2 = pattern2.findall(temp)
            print("2")
        elif re.search(r'https:\/\/manga\.bilibili\.com\/detail\/mc([0-9]+)', temp) != None:#粘贴漫画指定页数漫画可以下载
            pattern3 = re.compile(r'https:\/\/manga\.bilibili\.com\/detail\/mc([0-9]+)')
            temp2 = pattern3.findall(temp)
            print("3")
        print("解析到的漫画id:"+str(temp2))
        if temp2!="":
            download_manga_all(temp2[0])
            print('下载漫画完成')
        else:
            print('解析到的漫画id为空')
    else:
        print("输入内容为空")
    os.system("pause")
    pass
    # download_manga_all(25966)
    # download_manga_episode(448369, os.path.join(download_path, '辉夜大小姐想让我告白 ~天才们的恋爱头脑战~'))
    # get_image_url('/bfs/manga/f311955085404cab705e881d0a81204098967c1e.jpg')
    
