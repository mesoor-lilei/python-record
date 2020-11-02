#!/usr/bin/env python
import time

import pymysql
from lxml import html

import requests

if __name__ == '__main__':

    # 打开数据库连接
    db = pymysql.connect('localhost', 'root', '123456', 'test')
    # 创建一个游标对象
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE `异常心率` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        `名称` VARCHAR ( 255 ) COMMENT '名称',
        `类型` VARCHAR ( 255 ) COMMENT '类型',
        `病因` LONGTEXT COMMENT '病因',
        `症状` LONGTEXT COMMENT '症状',
        `诊断` LONGTEXT COMMENT '诊断',
        `预后` LONGTEXT COMMENT '预后',
        `治疗` LONGTEXT COMMENT '治疗',
        `描述` LONGTEXT COMMENT '描述',
    PRIMARY KEY ( `id` )
    )
    ''')

    base_url = 'https://www.msdmanuals.com'

    url = base_url + '/zh/home/heart-and-blood-vessel-disorders'
    response = requests.get(url).text
    html_result = html.etree.HTML(response)
    for i in range(1, 20):
        # 异常心率列表
        item = html_result.xpath("//*[@class='medicalsection__caption']")[i]
        类型 = item.xpath('string(a/text())').lstrip()
        li_list = item.xpath('./following-sibling::div[1]/ul/li')

        # print('异常心率列表 start')
        # print('结果', html.tostring(li_list[0]).decode())
        # print('异常心率列表 end')

        for li in li_list:
            # + 号按钮
            plus_btn_arr = li.xpath('./i[@class="medicalsection__icon medicalsection__plus--small"]')
            # + 号按钮不存在则无下级节点
            if not plus_btn_arr:
                continue
            plus_btn = plus_btn_arr[0]
            # print('结果', html.tostring(plus_btn).decode())
            click = base_url + li.xpath('./a/@href')[0]
            名称 = li.xpath('./a/text()')[0]
            print('URL', click)

            click_response = requests.get(click).text
            click_response_html = html.etree.HTML(click_response)
            # 去除 script 标签
            html.etree.strip_elements(click_response_html, 'script')
            try:
                article = click_response_html.xpath('//div[@class="topic__accordion"]')[0]
            except IndexError:
                # 跳过错误页面
                continue

            # print('结果', html.tostring(article).decode())

            description = ''
            病因 = ''
            症状 = ''
            诊断 = ''
            预后 = ''
            治疗 = ''
            for e in article:
                # print('结果', html.tostring(e).decode())
                classes = e.xpath('./@class')
                # class为空跳出循环
                if not classes:
                    continue
                class_text = classes[0]
                text = e.xpath('string()')
                text = '\n'.join(text.split())
                # print('文本描述', text)
                # print('HTML 描述', html.tostring(e).decode())
                # print('class', classes)
                # 拼接文本描述
                if 'para' in class_text or 'list' in class_text or 'HHead' in class_text:
                    description += text
                # 其它分类数据
                elif 'FHead' in class_text:
                    title = ''.join(e.xpath('./h2/text()'))
                    content = '\n'.join(e.xpath('string(div)').split())
                    # print('标题', title)
                    # print('内容', content)
                    if '病因' in title:
                        病因 = content
                    elif '症状' in title:
                        症状 = content
                    elif '诊断' in title:
                        诊断 = content
                    elif '预后' in title:
                        预后 = content
                    elif '治疗' in title:
                        治疗 = content

            # 执行 SQL
            # 使用预处理语句创建表
            sql = '''
            INSERT INTO 异常心率 (
                名称,
                类型,
                病因,
                症状,
                诊断,
                预后,
                治疗,
                描述
            )
            VALUE ( %s, %s, %s, %s, %s, %s, %s, %s )
            '''
            print('SQL', sql)
            print('参数', 名称, 类型, 病因, 症状, 诊断, 预后, 治疗, description)
            cursor.execute(sql, (名称, 类型, 病因, 症状, 诊断, 预后, 治疗, description))
            db.commit()
            # 清空数据
            description = ''
            病因 = ''
            症状 = ''
            诊断 = ''
            预后 = ''
            治疗 = ''
        time.sleep(10)

    # 关闭游标
    cursor.close()
    # 关闭数据库连接
    db.close()
