#!/usr/bin/env python
import time

import xlsxwriter
from lxml import html

import requests

file_name = '健康百科'


def save_excel():
    excel = xlsxwriter.Workbook(file_name + '.xlsx')
    merge_format = excel.add_format({
        'bold': True,  # 字体加粗
        'border': 1,  # 单元格边框宽度
        'align': 'center',  # 水平居中
        'valign': 'vcenter',  # 垂直居中
        'fg_color': '#f4b084',  # 颜色填充
        'text_wrap': True  # 自动换行
    })
    file = open(file_name + '.txt')
    line = file.readline()
    sheet_dict = {}
    while line:
        excel_row = eval(line)
        # 类型
        first_col = excel_row[0]
        data_index = first_col + 'index'
        data_sheet = first_col + 'sheet'
        # 每个 sheet 下标
        if data_index in sheet_dict:
            i = sheet_dict[data_index]
        else:
            sheet_dict[data_index] = i = 0
        # 每个 sheet 实例
        if data_sheet in sheet_dict:
            sheet = sheet_dict[data_sheet]
        else:
            sheet_dict[data_sheet] = sheet = excel.add_worksheet(first_col)
        # 删除类型
        excel_row = excel_row[1:]
        for j in range(len(excel_row)):
            # 连续两行的 A 单元格合并为一格，B 单元格同理
            if i % 2:
                for char_i, char in enumerate(['A', 'B']):
                    sheet.merge_range('{}{}:{}{}'.format(char, i, char, i + 1), excel_row[char_i], merge_format)
            sheet.write(i, j, excel_row[j])
        # 更新索引
        sheet_dict[data_index] += 1
        line = file.readline()
    print('sheet-dict', sheet_dict)
    file.close()
    excel.close()


def parse_item(titles, item_type):
    result = []
    for title_index, title in enumerate(titles):
        # 标题
        title_text = title.xpath('string()')
        # 内容
        content_text = title.xpath('string(following-sibling::*)')
        result.extend([title_text, content_text])
        print('{} [{}]{} {} [{}]{}'.format(
            tab_name,
            index,
            item_name,
            '通俗版目录' if item_type else '专业版目录',
            title_index,
            title_text
        ))
    return result


if __name__ == '__main__':
    base_url = 'https://www.baikemy.com'

    # 标签
    page_tab = requests.get(base_url + '/disease/list/0/0').text
    tab_html = html.etree.HTML(page_tab)
    tabs = tab_html.xpath('//*[@class="nav_link"]/a')

    for tab_item in tabs:
        tab_name = tab_item.xpath('string()')
        tab_url = tab_item.xpath('@href')[0]
        page_text = requests.get(base_url + tab_url).text
        page_html = html.etree.HTML(page_text)
        # 类型
        type_info_list = page_html.xpath('//*[@class="typeInfo_Li"]/a')
        for index, item in enumerate(type_info_list):
            p_result_item = []
            s_result_item = []
            item_name = item.xpath('string()')
            if item_name != '更多':
                item_url = base_url + item.xpath('@href')[0]

                item_text = requests.get(item_url).text
                item_html = html.etree.HTML(item_text)

                p_result_item.extend([tab_name, item_name, item_url])
                s_result_item.extend([tab_name, item_name, item_url])

                # 通俗版目录标题列表
                p_titles = item_html.xpath('//*[@class="p_directory_flag"]')
                p_result_item.extend(parse_item(p_titles, 1))
                # 专业版目录标题列表
                s_titles = item_html.xpath('//*[@class="s_directory_flag"]')
                s_result_item.extend(parse_item(s_titles, 0))

                # 追加写入
                data_text = open(file_name + '.txt', 'a')
                data_text.write(str(p_result_item) + '\n')
                data_text.write(str(s_result_item) + '\n')
                data_text.close()

                time.sleep(1)
    # 保存数据至 Excel
    save_excel()
