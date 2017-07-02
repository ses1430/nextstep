#-*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class Report(object):
    def __init__(self, stock_cd, year, quarter, url_string):
        self.stock_cd = stock_cd
        self.year = year
        self.quarter = quarter
        self.url_string = url_string

    def __str__(self):
        return "{}, {}, {}, {}".format(self.stock_cd, self.year, self.quarter, self.url_string)

def get_all_report_urls(stock_cd):
    urls = []

    driver = webdriver.Chrome('chromedriver')
    driver.get('https://dart.fss.or.kr/')
    driver.find_element_by_id('textCrpNm').send_keys(stock_cd)
    driver.find_element_by_id('date7').click()
    driver.find_element_by_id('publicTypeButton_01').click()
    driver.find_element_by_id('publicType1').click()
    driver.find_element_by_id('publicType2').click()
    driver.find_element_by_id('publicType3').click()

    for i in range(1,5):
        print(i)
        driver.execute_script("search({})".format(i))

        WebDriverWait(driver, timeout=5).until(lambda b: b.find_element_by_class_name('table_list'))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.find('div', {'class':'table_list'}).table.tbody.find_all('tr')

        for row in rows:
            td = row.find_all('a', href=True)[1]
            urls.append(td['href'])

    return urls

if __name__ == '__main__':
    urls = get_all_report_urls('005930')
    for url in urls:
        print (url)
