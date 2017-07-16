#-*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import re
from time import sleep
from dart_util import get_quarter_from_rcpno

STOCK_CD_FILE = 'kosdaq_stock_cd.txt'
URL_FILE = 'url_kosdaq.txt'

DART_URL_HOME = 'https://dart.fss.or.kr'
p_quarter = re.compile('\d{4}\.\d{2}')
p_rcpno = re.compile('\d{14}')

def get_report_info(driver, fp, stock_cd):
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
                rcpno = p_rcpno.search(td['href']).group()

                try:
                    quarter = p_quarter.search(list(td.children)[2].string).group()
                except:
                    quarter = get_quarter_from_rcpno(rcpno)

                print("{},{},{}".format(stock_cd, quarter, rcpno))
                fp.write("{},{},{}\n".format(stock_cd, quarter, rcpno))

            if len(rows) < 15:
                break

            # 각 페이지별로 interval 1초
            sleep(1)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    _driver = webdriver.Chrome('chromedriver')

    stock_cd_list = []

    # 종목코드 불러오기
    fp = open(STOCK_CD_FILE, 'r')
    stock_cd_list = [item.strip() for item in fp.readlines()[49:]]
    fp.close()

    with open(URL_FILE, 'w') as fp:
        #get_report_info(_driver, fp, '007390')

        for stock_cd in stock_cd_list:
            get_report_info(_driver, fp, stock_cd)
            sleep(1) # 각 report별로 interval
