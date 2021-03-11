#!/usr/bin/env python
import re
import time

import xlsxwriter
from lxml import html

import requests

file_name = '找药物'


def save_excel():
    excel = xlsxwriter.Workbook(file_name + '.xlsx')
    with open(file_name + '.txt') as file:
        drug_line = file.readline()
        sheet_dict = {}
        while drug_line:
            drug_row = eval(drug_line)
            # 类型
            first_col = drug_row[0]
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
            drug_row = drug_row[1:]
            for j in range(len(drug_row)):
                sheet.write(i, j, drug_row[j])
            # 更新索引
            sheet_dict[data_index] += 1
            drug_line = file.readline()
        excel.close()


if __name__ == '__main__':
    base_url = 'https://www.baikemy.com/medicine/'
    drug_dict = {
        'medicineList/0?medicineType=1': '中药',
        'medicineList/0?medicineType=2': '西药',
        'medicineList/1': '按疾病',
        'medicineList/2': '按科室',
        'medicineList/3': '儿童用药',
        'medicineList/4': '孕妇用药',
        'medicineList/5': '老人用药',
    }
    for drug_url in drug_dict:
        drugs = eval(requests.get(base_url + drug_url).text)['data']
        for drug_key in drugs:
            drug = drugs[drug_key]
            for drug_index, drug_item in enumerate(drug):
                time.sleep(1)
                row = [drug_dict[drug_url]]
                page_html = html.etree.HTML(requests.get(base_url + 'detail/' + str(drug_item['id'])).text)
                page_name = page_html.xpath('//*[@class="detail_name"]/text()')[0]
                page_info = page_html.xpath('string(//*[@class="name_info"])')
                # 删除换行符、合并多个空格、去除首尾空格
                page_info = re.sub(' +', ' ', re.sub('\n', ' ', page_info)).strip()
                row.extend([page_name, page_info])
                page_data = page_html.xpath('//*[@class="directory_flag"]')
                for data_item in page_data:
                    item_title = data_item.xpath('string()')
                    item_text = data_item.xpath('string(following-sibling::*)')
                    row.extend([item_title, item_text])
                print(row[:3])
                with open(file_name + '.txt', 'a') as f:
                    f.write(str(row) + '\n')
    save_excel()
