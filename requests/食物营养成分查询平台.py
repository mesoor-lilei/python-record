#!/usr/bin/env python
import json
import time

import pymysql
from lxml import html

import requests

if __name__ == '__main__':

    tr_type = ['食部(Edible)', '水分(Water)', '能量(Energy)', '蛋白质(Protein)', '脂肪(Fat)', '胆固醇(Cholesterol)', '灰分(Ash)',
               '碳水化合物(CHO)', '总膳食纤维(Dietary fiber)', '胡萝卜素(Carotene)', '维生素A(Vitamin)', 'α-TE', '硫胺素(Thiamin)',
               '核黄素(Riboflavin)', '烟酸(Niacin)', '维生素C(Vitamin C)', '钙(Ca)', '磷(P)', '钾(K)', '钠(Na)', '镁(Mg)', '铁(Fe)',
               '锌(Zn)', '硒(Se)', '铜(Cu)', '锰(Mn)', '碘(I)', '饱和脂肪酸(SFA)', '单不饱和脂肪酸(MUFA)', '多不饱和脂肪酸(PUFA)', '合计(Total)']
    detail_type = ['含量', '同类排名', '同类均值', '含量水平']

    # 拼接数据库字段
    tr_type_field = ''
    for type_item in tr_type:
        for detail_type_item in detail_type:
            tr_type_field_text = type_item + '_' + detail_type_item
            tr_type_field += '`{}` TEXT COMMENT "{}",'.format(tr_type_field_text, tr_type_field_text)

    # 打开数据库连接
    db = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='test')
    # 创建一个游标对象
    cursor = db.cursor()
    table = '''
    CREATE TABLE `食物营养成分查询平台` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        `大分类名称` VARCHAR ( 255 ) COMMENT '大分类名称',
        `分类名称` VARCHAR ( 255 ) COMMENT '分类名称',
        `食物名称` VARCHAR ( 255 ) COMMENT '食物名称',
        {}
    PRIMARY KEY ( `id` )
    )
    '''.format(tr_type_field)
    print('table', table)
    cursor.execute(table)
    # 提交
    db.commit()

    base_url = 'https://fq.chinafcd.org'
    data_url = 'https://fq.chinafcd.org/FoodInfoQueryAction!queryFoodInfoList.do?' \
               'categoryOne={}&categoryTwo={}' \
               '&foodName=0&pageNum={}&field=0&flag=0'

    # 大分类
    大分类s = html.etree.HTML(requests.get(base_url).text).xpath('//*[contains(@class, "food_box")]')

    for 大分类 in 大分类s:
        大分类名称 = 大分类.xpath('string(div/h3/a)')
        分类s = 大分类.xpath('ul/li/a')
        for 分类 in 分类s:
            分类名称 = 分类.xpath('string()')
            data_pid = 分类.xpath('@data_pid')[0]
            data_id = 分类.xpath('@data_id')[0]
            # 睡眠 1 秒
            time.sleep(1)
            json_data = json.loads(requests.get(data_url.format(data_pid, data_id, 1)).text)
            data = json_data['list']
            data_num = int(json_data['totalPages'])
            print('页数', data_num)
            # 页数大于 1 则分页获取数据
            if data_num > 1:
                for num in range(data_num - 1):
                    # 睡眠 1 秒
                    time.sleep(1)
                    data.extend(json.loads(requests.get(data_url.format(data_pid, data_id, num + 2)).text)['list'])
            for item in data:
                # 睡眠 1 秒
                time.sleep(1)
                trs = html.etree.HTML(requests.get(base_url + '/foodinfo/{}.html'.format(item[0])).text).xpath('//tr')
                # 删除表格标题
                trs.pop(0)
                字段名称_str = ''
                食物名称 = item[2]
                字段值 = [大分类名称, 分类名称, 食物名称]
                for tr_index, tr in enumerate(trs):
                    # 第一个 tr 多出一个 td 作为合并行
                    偏移量 = 0 if tr_index > 0 else 1
                    tds = tr.xpath('td')
                    字段名称 = tr_type[tr_index]
                    字段名称_str += '`{}_含量`,`{}_同类排名`,`{}_同类均值`,`{}_含量水平`,'.format(字段名称, 字段名称, 字段名称, 字段名称)
                    项目 = tds[0 + 偏移量].xpath('string()')
                    含量 = tds[1 + 偏移量].xpath('string()')
                    同类排名 = tds[2 + 偏移量].xpath('string()')
                    同类均值 = tds[3 + 偏移量].xpath('string()')
                    含量水平_ele = tds[4 + 偏移量].xpath('img/@alt')
                    含量水平 = 含量水平_ele[0] if 含量水平_ele else None
                    print(
                        '食物名称', 食物名称,
                        '字段名称', 字段名称,
                        '项目', 项目,
                        '含量', 含量,
                        '同类排名', 同类排名,
                        '同类均值', 同类均值,
                        '含量水平', 含量水平
                    )
                    字段值.extend([含量, 同类排名, 同类均值, 含量水平])
                字段占位符 = ('%s,%s,%s,%s,' * len(trs))[:-1]
                sql = 'insert into 食物营养成分查询平台 (大分类名称,分类名称,食物名称,{}) value (%s,%s,%s,{})'.format(字段名称_str[:-1], 字段占位符)
                # print('SQL', sql)
                cursor.execute(sql, tuple(字段值))
                # 提交
                db.commit()
    # 关闭游标
    cursor.close()
    # 关闭数据库连接
    db.close()
