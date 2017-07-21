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

def download_html(driver, gubun, stock_cd, quarter, rcpno):

    file_name = "html\{}.{}.{}.html".format(stock_cd, quarter, rcpno)
    url = URL_PREFIX + rcpno
    driver.get(url)

    item_list = []
    p_rcpno = re.compile('\d{14}')

    with open(file_name, 'w', encoding='utf-8') as fp:
        
        try:
            driver.find_element_by_partial_link_text(u'재무에 관한 사항').click()
        except NoSuchElementException as ex:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            try:
                new_rcpno = p_rcpno.search(soup.find('select', {'id':'family'}).find_all('option')[1].attrs['value']).group(0)
            except NoSuchElementException as e:
                new_rcpno = p_rcpno.search(soup.find('select', {'id':'att'}).find_all('option')[1].attrs['value']).group(0)
            except Exception as e:
                return
                
            url = URL_PREFIX + new_rcpno
            driver.get(url)
            driver.find_element_by_partial_link_text(u'재무에 관한 사항').click()
        except NoSuchElementException as ex:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            new_rcpno = p_rcpno.search(soup.find('select', {'id':'att'}).find_all('option')[1].attrs['value']).group(0)
            url = URL_PREFIX + new_rcpno
            driver.get(url)
            driver.find_element_by_partial_link_text(u'재무에 관한 사항').click()

        driver.switch_to_frame('ifrm')
        fp.write(driver.page_source)

def main_proc(gubun):
    _driver = webdriver.Chrome('chromedriver')

    if gubun == 'KOSPI':
        fp = open(KOSPI_URL_FILE, 'r')
    elif gubun == 'KOSDAQ':
        fp = open(KOSDAQ_URL_FILE, 'r')

    target_items = [item.strip() for item in fp.readlines()[40250:]]
    fp.close()

    total_count = len(target_items)
    start_time = datetime.now()

    for idx, item in enumerate(target_items):
        stock_cd, quarter, rcpno = item.split(',')
        download_html(_driver, gubun, stock_cd, quarter, rcpno)
        sleep(1)

        if idx > 1 and (idx+1) % 10 == 0:
            end_time = datetime.now()
            gap_time_sec = (end_time - start_time).total_seconds()

            # 남은시간 : 지금까지 처리한 건당 평균시간(초) * 남은 건수
            avg_time_per = gap_time_sec / (idx+1)
            left_time = avg_time_per * (total_count-idx-1)
            estimated_end_time = end_time + timedelta(seconds=left_time)
            perc = round((idx+1)/total_count*100, 2)

            print("[{}/{}] 진행율 : {}%, 건당소요시간 : {}초, 예상종료일시 : {}".format(idx+1, total_count, perc, round(avg_time_per, 1), estimated_end_time.strftime('%m/%d %H:%M')))

    final_time = datetime.now()
    elapsed_time = final_time - start_time
    print("총 걸린시간 : {}".format(str(elapsed_time)))
    print("총 건수 : {}".format(total_count))

if __name__ == '__main__':
    #print('======================{}========================'.format('KOSDAQ START'))
    #main_proc('KOSDAQ')
    
    print('======================{}========================'.format('KOSPI START'))
    main_proc('KOSPI')
