#!/usr/bin/env python
import pymysql
from lxml import html

import requests

if __name__ == '__main__':

    # 打开数据库连接
    db = pymysql.connect('localhost', 'root', '123456', 'test')
    # 创建一个游标对象
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE `大厨艺` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        `分类名称` VARCHAR ( 255 ) COMMENT '分类名称',
        `项目名称` VARCHAR ( 255 ) COMMENT '项目名称',
        `代谢当量` FLOAT(10, 1) COMMENT '代谢当量',
        `千卡` FLOAT(10, 1) COMMENT '千卡',
    PRIMARY KEY ( `id` )
    )
    ''')

    category_url = 'http://www.dachuyi.com/yundong/{}/'
    # 共 14 个分类
    for i in range(1, 15):
        category_response = requests.get(category_url.format(i)).text
        category_html = html.etree.HTML(category_response)
        # 分类名称
        分类名称 = category_html.xpath("string(//*[@class='fl area_gp']/*[@class='pdt20']/*[@class='h2txt'])")
        print('分类名称', 分类名称)
        # 当前分类所有运动项目
        a_list = category_html.xpath("//*[@class='fl area_gp']//a/@href")
        for a in a_list:
            # print('运动项目 URL', a)
            a_response = requests.get(a).text
            a_html = html.etree.HTML(a_response)
            项目名称 = a_html.xpath("string(//*[@class='title'])")
            print('项目名称', 项目名称)
            代谢当量 = float(a_html.xpath("string(//*[@class='ydheader']/p[4]/em[1])")[:-3])
            体重 = int(a_html.xpath("string(//*[@class='ydheader']/p/em[1])")[:-2])
            千卡_每小时 = int(a_html.xpath("string(//*[@class='ydheader']/p/em[2])"))
            千卡 = round(千卡_每小时 / 体重, 1)

            # 执行 SQL
            # 使用预处理语句创建表
            sql = '''
            INSERT INTO 大厨艺 (
                分类名称,
                项目名称,
                代谢当量,
                千卡
            )
            VALUE ( %s, %s, %s, %s )
            '''
            cursor.execute(sql, (
                分类名称,
                项目名称,
                代谢当量,
                千卡))
            db.commit()

    # 关闭游标
    cursor.close()
    # 关闭数据库连接
    db.close()
