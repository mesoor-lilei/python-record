#!/usr/bin/env python
import time

from lxml import etree

import requests

base_url = 'https://www.ncbi.nlm.nih.gov'


def 获取某页面主节点(mesh_url):
    time.sleep(2)
    page_html = etree.HTML(requests.get(base_url + mesh_url).content)
    名称 = page_html.xpath('//*[@class="title"]/text()')[0]
    return page_html.xpath('//b[text()="' + 名称 + '"]')[0]


# 递归获取某节点下的子节点
def 递归(节点, node_data):
    mesh_list = 节点.xpath('following-sibling::ul')
    child = []
    for mesh_item in mesh_list:
        child_item = {}
        a_text = mesh_item.xpath('a/text()')[0]
        a_url = mesh_item.xpath('a/@href')[0]
        child_item['text'] = a_text
        child_item['url'] = a_url
        print('child_item', a_text, a_url)
        # 子节点
        uls = mesh_item.xpath('ul')
        if uls:
            child_item_child = []
            for ul in uls:
                child_item_child_item = {}
                ul_a_url = ul.xpath('a/@href')[0]
                ul_a_text = ul.xpath('a/text()')[0]
                child_item_child_item['text'] = ul_a_text
                child_item_child_item['url'] = ul_a_url
                # 此子节点存在下级节点
                if ul.xpath('text()'):  # 为空：[]、不为空：[' +']
                    递归(获取某页面主节点(ul_a_url), child_item_child_item)
                print('\tchild_item_child_item', ul_a_text, ul_a_url)
                child_item_child.append(child_item_child_item)
            child_item['child'] = child_item_child
        child.append(child_item)
    node_data['child'] = child


def append_data(data, index='1'):
    target_url = data['url']
    data['index'] = index

    time.sleep(2)
    page_html = etree.HTML(requests.get(base_url + target_url).content)

    # Entry Terms 根据文本内容定位节点
    entry_terms = page_html.xpath('//p[text()="Entry Terms:"]/following-sibling::ul[1]//text()')
    data['entryTerms'] = entry_terms

    # Tree Number 和 MeSH Unique ID
    texts = page_html.xpath('//*[@class="rprt abstract"]/p/text()')
    if texts:
        for text in texts:
            replace_keys = ['Tree Number(s): ', 'MeSH Unique ID: ']
            for replace_key in replace_keys:
                if replace_key in text:
                    data[replace_key] = text.replace(replace_key, '')
        print('已处理', data['text'])
    if 'child' in data:
        for target_index, target_item in enumerate(data['child']):
            append_data(target_item, index + '-' + str(target_index + 1))


if __name__ == '__main__':
    mesh_url = '/mesh/68002318'
    result_data = {'text': 'Cardiovascular Diseases', 'url': mesh_url}
    递归(获取某页面主节点(mesh_url), result_data)
    print('result_data', result_data)

    # 此处保留 URL 备份
    # result_data = eval(open('url.txt').read())
    append_data(result_data)
    # 保存数据至文件
    file = open('data.txt', 'w')
    file.write(str(result_data))
    file.close()
