#-*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from time import sleep

URL_PREFIX = 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='
URL_FILE = 'url.txt'

driver = webdriver.Chrome('chromedriver')
p = re.compile(u'단위\s*:\s*(.*?)원')

f = open(URL_FILE, 'r')
items = [item.strip() for item in f.readlines()]
f.close()

for idx, item in enumerate(items):
    stock_cd, quater, rcpno = item.split(',')
    url = URL_PREFIX + rcpno

    sleep(3)
    driver.get(url)
    file_name = "result\{}.{}.{}.txt".format(stock_cd, quater, rcpno)

    with open(file_name, 'w') as fp:
        print("{},{},{},{}".format(idx, stock_cd, quater, url))
        fp.write("{},{},{}\n".format(stock_cd, quater, url))

        try:
            driver.find_element_by_link_text(u'III. 재무에 관한 사항').click()
            driver.switch_to_frame('ifrm')
            soup = BeautifulSoup(driver.page_source, "html.parser")

            elements = soup.find_all(['p', 'table'], limit=10)

            for e in elements:
                # 단위
                if not e.has_attr('border') and p.search(e.text) is not None:
                    unit = p.search(e.text).group(1)
                    print(unit)
                    fp.write("{}\n".format(unit))

                # 재무제표
                if e.has_attr('border') and len(e.find_all('tr')) > 10:

                    # thead 유무에 따라 순서를 바꿈
                    if e.thead is not None:
                        rows = e.tbody.find_all('tr')
                    else:
                        idx = 1

                        # rowspan이 있을 경우 그만큼 건너뛰기
                        if e.tbody.tr.td.has_attr('rowspan'):
                            idx = int(e.tbody.tr.td.attrs['rowspan'])

                        rows = e.tbody.find_all('tr')[idx:]

                    for r in rows:
                        cols = r.find_all('td')

                        title = re.sub('[\s\[\]ㆍ]', '', cols[0].text.strip())
                        amt = re.sub('[\s\(\),]', '', cols[1].text.strip())

                        print("{}, {}".format(title, amt))
                        fp.write("{},{}\n".format(title, amt))
                    break
        except Exception as e:
            pass
