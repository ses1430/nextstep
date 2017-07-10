#-*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

test_url = 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20120330002755'
driver = webdriver.Chrome('chromedriver')
p = re.compile('\d{14}')
driver.get(test_url)

try:
    target = driver.find_element_by_link_text(u'III. 재무에 관한 사항')
    target.click()
    driver.switch_to_frame('ifrm')
    soup = BeautifulSoup(driver.page_source, "html.parser")

    tbl = soup.find('table', {'border':'1'})
    print(tbl)

    if len(tbl.tbody.find_all('tr')) < 5:
        count = 0
        while True:
            print(count)
            tbl = tbl.find_next_sibling('table', {'border':'1'})
            print(tbl)
            if len(tbl.tbody.find_all('tr')) > 5:
                data_tbl = tbl
                print(tbl)
                break
            count = count + 1

    rows = data_tbl.tbody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')

        col_title = re.sub('[\s\t]+', '', cols[0].text.encode('utf-8').strip())
        col_val = re.sub('[\s\t]+,\(\)]', '', cols[1].text.encode('utf-8').strip())

        if len(col_title) > 3:
            print("{}, {}\n".format(col_title, col_val))

except Exception as e:
    pass
