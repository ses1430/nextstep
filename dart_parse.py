#-*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

URL_PREFIX = 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='
URL_FILE = 'url.txt'

driver = webdriver.Chrome('chromedriver')
p = re.compile('\d{14}')

f = open(URL_FILE, 'r')
report_urls = [item.strip() for item in f.readlines()]
f.close()

cnt = len(report_urls)

for idx, line in enumerate(report_urls):
    stock_cd, quater, rcpno = line.split(',')
    url = URL_PREFIX + rcpno
    driver.get(url)
    file_name = '.'.join([p.search(url).group(), 'txt'])

    with open('\\'.join([stock_cd, file_name]), 'w') as fp:
        def dual_print(val):
            print(val)
            fp.write("{}\n".format(val))

        print("{},{},{}".format(idx, stock_cd, url))
        fp.write("{},{},{}\n".format(stock_cd, quater, url))

        try:
            driver.find_element_by_link_text(u'III. 재무에 관한 사항').click()
            driver.switch_to_frame('ifrm')
            soup = BeautifulSoup(driver.page_source, "html.parser")

            unit = 1
            try:
                unit_tbl = soup.find('table', {'class':'nb'})
                unit_txt = unit_tbl.tbody.tr.td.text

                if u'천만원' in unit_txt:
                    unit = 10000000
                elif u'백만원' in unit_txt:
                    unit = 1000000
                elif u'십만원' in unit_txt:
                    unit = 100000
                elif u'만원' in unit_txt:
                    unit = 10000
                elif u'천원' in unit_txt:
                    unit = 1000
                elif u'백원' in unit_txt:
                    unit = 100
                elif u'십원' in unit_txt:
                    unit = 10

                fp.write("{}\n".format(unit))
            except:
                fp.write("{}\n".format(unit))

            data_tbl = soup.find('table', {'border':'1'})

            if len(data_tbl.tbody.find_all('tr')) < 5:
                while True:
                    tbl = soup.find_next('table', {'border':'1'})
                    if len(tbl.tbody.find_all('tr')) > 5:
                        data_tbl = tbl
                        break

            rows = data_tbl.tbody.find_all('tr')
            for row in rows:
                cols = row.find_all('td')

                col_title = re.sub('[\s\t]+', '', cols[0].text.encode('utf-8').strip())
                col_val = re.sub('[\s\t]+,\(\)]', '', cols[1].text.encode('utf-8').strip())

                if len(col_title) > 3:
                    fp.write("{}, {}\n".format(col_title, col_val))

        except Exception as e:
            pass
