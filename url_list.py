#-*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import re

DART_URL_HOME = 'https://dart.fss.or.kr'
STOCK_CD_FILE = 'stock_cd.txt'
URL_FILE = 'url.txt'
p = re.compile('\d{4}\.\d{2}')
p2 = re.compile('\d{14}')

driver = webdriver.Chrome('chromedriver')

stock_cd_list = []

fp = open(STOCK_CD_FILE, 'r')
stock_cd_list = [item.strip() for item in fp.readlines()]
fp.close()

with open(URL_FILE, 'w') as fp:
    for stock_cd in stock_cd_list:
        if not os.path.exists(stock_cd):
            os.makedirs(stock_cd)
        urls = []
        driver.get(DART_URL_HOME)
        driver.find_element_by_id('textCrpNm').send_keys(stock_cd)
        driver.find_element_by_id('date7').click()
        driver.find_element_by_id('publicTypeButton_01').click()
        driver.find_element_by_id('publicType1').click()
        driver.find_element_by_id('publicType2').click()
        driver.find_element_by_id('publicType3').click()

        try:
            for i in range(1,6):
                driver.execute_script("search({})".format(i))

                WebDriverWait(driver, timeout=5).until(lambda b: b.find_element_by_class_name('table_list'))

                soup = BeautifulSoup(driver.page_source, "html.parser")
                rows = soup.find('div', {'class':'table_list'}).table.tbody.find_all('tr')

                for row in rows:
                    td = row.find_all('a', href=True)[1]

                    try:
                        quater = p.search(list(td.children)[2].string).group()
                    except:
                        quater = 'Unknown'

                    rcpno = p2.search(td['href']).group()

                    print("{},{},{}".format(stock_cd, quater, rcpno))
                    fp.write("{},{},{}\n".format(stock_cd, quater, rcpno))

        except Exception as e:
            pass
