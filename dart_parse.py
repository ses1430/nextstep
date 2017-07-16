#-*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime, timedelta
from time import sleep
from dart_util import *

URL_PREFIX = 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='
KOSPI_URL_FILE = 'url_kospi.txt'
KOSDAQ_URL_FILE = 'url_kosdaq.txt'

def report_parse(driver, gubun, stock_cd, quarter, rcpno):
    unit = ''
    p_unit = re.compile(u'단위\s*:\s*(\w*)')
    p_rcpno = re.compile('\d{14}')

    try:
        file_name = "{}\{}.{}.{}.txt".format(gubun, stock_cd, quarter, rcpno)
        url = URL_PREFIX + rcpno
        driver.get(url)

        item_list = []

        with open(file_name, 'w') as fp:
            #print("{},{},{}".format(stock_cd, quarter, url))
            fp.write("{},{},{}\n".format(stock_cd, quarter, url))

            try:
                driver.find_element_by_partial_link_text(u'재무에 관한 사항').click()
            except NoSuchElementException as ex:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                new_rcpno = p_rcpno.search(soup.find('select', {'id':'family'}).find_all('option')[1].attrs['value']).group(0)
                url = URL_PREFIX + new_rcpno
                driver.get(url)
                driver.find_element_by_partial_link_text(u'재무에 관한 사항').click()

            driver.switch_to_frame('ifrm')
            soup = BeautifulSoup(driver.page_source, "html.parser")
            elements = soup.find_all(['p', 'table'])

            # 단위
            for e in elements:
                if not e.has_attr('border') and p_unit.search(e.text) is not None:
                    unit = p_unit.search(e.text).group(1)
                    break

            #print("{}{}".format(unit))
            fp.write("{}\n".format(unit))

            # 재무제표
            for e in elements:

                item_list.clear()

                # border 속성이 있고 10줄 이상인 표를 찾음
                if e.name == 'table' and e.has_attr('border'):

                    # thead 가 없으면 그만큼 header를 건너뛴다
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

                        # 병합된 cell 이거나, 셀에 색상이 입혀져 있으면 건너뛴다
                        if cols[0].has_attr('colspan') or cols[0].has_attr('backgroud-color'):
                            continue

                        # 1개 항목만 들어있는 row
                        if len(cols[0].find_all('br')) == 0:
                            title = clean_title(cols[0].text) # 쓸데없는 문자 제거

                            # title이 있을때만 금액 가져오기
                            if len(title) > 0:
                                amt = clean_amt(cols[1].text)

                                # title, amt이 모두 있을때만 쓰기
                                if len(amt) > 0:
                                    item_list.append([title, amt])
                        # 2개 이상의 항목이 들어있는 row
                        else:
                            try:
                                title_list = [clean_title(item) for item in cols[0].children if item.name != 'br']
                                amt_list = [clean_amt(item) for item in cols[1].children if item.name != 'br']

                                for i in range(len(title_list)):
                                    try:
                                        item_list.append([title_list[i], amt_list[i]])
                                    except IndexError:
                                        item_list.append([title_list[i], '-'])
                            except TypeError:
                                pass

                    # parsing 된 결과가 10row 이상일 경우 파일에 쓰고 break
                    if len(item_list) > 10:
                        for item in item_list:
                            #print("{}, {}".format(title, amt))
                            fp.write("{},{}\n".format(item[0], item[1]))

                        break
    except Exception as e:
        print(e)

def main_proc(gubun):
    _driver = webdriver.Chrome('chromedriver')

    if gubun == 'KOSPI':
        fp = open(KOSPI_URL_FILE, 'r')
    elif gubun == 'KOSDAQ':
        fp = open(KOSDAQ_URL_FILE, 'r')

    target_items = [item.strip() for item in fp.readlines()]
    fp.close()

    #target_items = {'015750,2002.12,20040813000066'}

    total_count = len(target_items)
    start_time = datetime.now()

    for idx, item in enumerate(target_items):
        stock_cd, quarter, rcpno = item.split(',')
        report_parse(_driver, gubun, stock_cd, quarter, rcpno)
        print("{},{},{}".format(stock_cd, quarter, rcpno))
        sleep(1)

        if idx > 1 and (idx+1) % 10 == 0:
            end_time = datetime.now()
            gap_time_sec = (end_time - start_time).total_seconds()

            # 남은시간 : 지금까지 처리한 건당 평균시간(초) * 남은 건수
            left_time = gap_time_sec / (idx+1) * (total_count-idx+1)
            estimated_end_time = end_time + timedelta(seconds=left_time)
            perc = round((idx+1)/total_count*100, 2)

            print("[{}/{}] 진행율 : {}%  예상종료일시 : {}".format(idx+1, total_count, perc, estimated_end_time.strftime('%m/%d %H:%S')))

if __name__ == '__main__':
    main_proc('KOSDAQ')
