import requests
from urllib.parse import urlencode
import os
from hashlib import md5
import re

# 根据 offset 得到每一个 ajax 请求返回的 json
def get_json(offset):
    base_url = 'https://www.toutiao.com/api/search/content/?'
    params = {
        'aid':'24',
        'app_name':'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'en_qc':'1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis'
    }
    url = base_url + urlencode(params)
    headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    "Referer":"https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D",
    "X-Requested-With":"XMLHttpRequest",
    'Cookie':'ttcid=da67946b23aa43d6ac326f777dd59fe812; csrftoken=6f135e43a191f0b167a48c389eeba813; s_v_web_id=verify_kno812c2_7ES6Luq3_l4zU_4XeR_AoQs_gCzvJDVEpXUe; ttwid=1%7CxhN7KFemQ_1d_4TmXRXpBnmK0Gv0kKL9eNh6iqqrYmE%7C1618815503%7C7a69e13d9cbef5caea030dbe368b80007da59c7d7e9c06515a43c805b62c41ec; tt_webid=6952759632059336222; csrftoken=6f135e43a191f0b167a48c389eeba813; __ac_nonce=0607e3d54009a36457118; __ac_signature=_02B4Z6wo00f01op2uqgAAIDBQspztk72PSqKUr4AAMLvdsa8Sypz0.haweREk1iEfSW9ehRW.e8ycbXY1eb3I4zNXKuSU4ATN1bpTaIW.IqDagLfCE7VDg3e5up-lEGl8K56Y5hZBbU96Uky6c; __tasessionId=jen9hdn7a1618907905634; tt_scid=uxdiRzrZvM8-KjRx95VrFLd6NPWZ.t555xOXwTcx1AVmgIpylM5.oOgFfwemTfG2ef88; MONITOR_WEB_ID=verify_kno812c2_7ES6Luq3_l4zU_4XeR_AoQs_gCzvJDVEpXUe'
  }

    try:
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Errors', e.args)
        return None

# 根据 json 提取出相应内容的标题、图片链接
def get_images(json):
    if json.get('data'):
        for item in json.get('data'):
            title = item.get('title')
            images = item.get('image_list')
            if images == None:
                continue
            for image in images:
                origin_image = re.sub("list.*?pgc-image", "large/pgc-image", image.get('url'))#获取大图片
                yield {
                    'title': title,
                    'image': origin_image
                }

# 根据 item 中的 title 创建文件夹，图片的名称可以用其内容的 MD5 值，防止重复
# 这里有个小问题，那就是在 windows 路径下创建文件夹是不可以有英文的':'，这些标题大多是中文符号，但是偶尔也会含有
# 英文的':',这样会导致创建文件夹失败，所以要将windows下不允许的英文符号(\/:*?"<>|)转换成相应的中文标点
def save_images(item):
    title = item.get('title')
    intab = r'\/:*?"<>|'
    outtab = '、、：-？“《》-'
    trantab = str.maketrans(intab, outtab)
    # 将windows下不允许的英文符号(\/:*?"<>|)转换成相应的中文标点
    img_path = 'C:/Users/lenovo/Desktop/开发工具与移动编程/爬取今日头条街拍图/街拍图片/' + title.translate(trantab)
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(img_path, md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('已经下载', file_path)
    except requests.ConnectionError:
        print('下载失败')

def main(offset):
    json = get_json(offset)
    for item in get_images(json):
        # print(item)
        save_images(item)
    print("图片下载完毕")

if __name__ == '__main__':
    offsets = ([x * 20 for x in range(1,3)])
    main(offsets)

