# Author: Hoichun H. Ng
# Version: Python 3.7.4
# Coding: UTF-8

import re
import requests
import types
import json
import sys
import os
from requests.exceptions import RequestException
from urllib.parse import unquote


class WebsiteIndexException(Exception):
    pass


# 读取输入文件中的网址列表
def read_input_file(input_file):
    f = open(input_file, 'r')
    input_list = []
    for line in f:
        input_list.append(line)
    f.close()

    return input_list


# 下载完整网页文本
def get_web_page(url):
    try:
        # 添加头部信息
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        new_response = requests.get(url, headers=head)
        # print(new_response.status_code)  # for test only

        if new_response.status_code >= 400 or new_response.status_code < 200:
            raise WebsiteIndexException
        return new_response.text
    except RequestException:
        sys.stderr.write('Error|' + url.rstrip() + ':this page is not accessible.\n')
        return None
    except WebsiteIndexException:
        sys.stderr.write('Error|' + url.rstrip() + ':this page returns %i\n' % new_response.status_code)
        return None


# 解析网页
def parse_page(html):
    info = {}  # 提取信息汇总 (type: dict)

    phone_number = r'[^0-9A-Za-z\_](\d{7,8}|\d{11})[^0-9A-Za-z\_]'
    names = r'(姓名|name)(:|：)(.+?)(,|，|。|;|；|“|”|"|\r|\n)'
    urls = r'(\b|,|\.|，|。|;|；)网址(:|：)([\t ]*)(https?://.*?)(,|，|。|;|；|“|”|"|\s)'
    shared_links = r'^(.*链接.*提取码.*?)([\r|\n]*)$'

    phone = re.findall(phone_number, html)  # 内容一：电话/手机号码
    origin_name = re.findall(names, html, flags=re.I)  # 内容二：姓名
    origin_url = re.findall(urls, html, flags=re.I)  # 内容三：网址/URL
    origin_shared = re.findall(shared_links, html, flags=re.M)  # 内容四：链接&提取码
    name = []
    url = []
    shared = []
    for item in origin_name:
        name.append(item[2])
    for item in origin_url:
        url.append(item[3])
    for item in origin_shared:
        shared.append(item[0])

    info['phone'] = phone
    info['name'] = name
    info['url'] = url
    info['shared'] = shared
    # print(phone)  # for test only

    return info


# 将抓取的内容保存到文件
def write_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False))
        f.close()


def main():
    input_list = read_input_file(sys.argv[1])  # 读取网址列表
    output_folder = sys.argv[2]  # 输出文件存储路径

    # 处理并存储URLDecode后的输出文件名
    output_names = []
    for web_page in input_list:
        last_slash = web_page.rfind('/')
        if last_slash == -1:
            last_slash = web_page.rfind('\\')
        output_names.append(unquote(web_page[last_slash+1:].rstrip()))  # URLDecode Process
    # print(output_names)  # for test only

    for url in input_list:
        status_code = {}
        html = get_web_page(url.rstrip())  # 下载网页

        if not html:  # 异常处理：删除已存在的同名输出文件
            if os.path.exists(output_folder + '/' + output_names[input_list.index(url)]):
                os.remove(output_folder + '/' + output_names[input_list.index(url)])
            continue

        result = parse_page(html)  # 解析网页，获取关键信息
        write_file(result, output_folder + '/' + output_names[input_list.index(url)])  # 将信息写入名字对应的文件


if __name__ == '__main__':
    main()

exit(0)




