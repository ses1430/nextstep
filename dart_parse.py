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
                if p_unit.search(e.text) is not None:
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
                        try:
                            cols = r.find_all('td')
                            valid_title_cnt = 0

                            # 병합된 cell 
                            if cols[0].has_attr('colspan'):
                                continue

                            # 1개만 들어있는 항목인지 체크
                            bool_sing_title = False
                            
                            if len(cols[0].find_all('br')) == 0 or len(cols[0].find_all('p', 'span')) == 1:
                                bool_single_title = True
                            else:
                                col_title_list = cols[0].children
                                
                                for item in col_title_list:
                                    if item.name == 'br':
                                        continue
                                    elif item.name in ('p', 'span') and len(clean_title(item.text)) > 0:
                                        valid_title_cnt = valid_title_cnt + 1
                                
                                if valid_title_cnt == 1:
                                    bool_single_title = True
                                else:
                                    bool_single_title = False
                                    
                            # 1개 항목만 들어있는 row일 경우
                            if bool_single_title == True:
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
                                    for item in cols[0].children:
                                        if isinstance(item, bs4.element.NavigableString):
                                            title_list.append(clean_title(item))
                                        elif isinstance(item, bs4.element.Tag):
                                            if item.name != 'br':
                                                title_list.append(clean_title(item.text))
                                                
                                    for item in cols[1].children:
                                        if isinstance(item, bs4.element.NavigableString):
                                            amt_list.append(clean_title(item))
                                        elif isinstance(item, bs4.element.Tag):
                                            if item.name != 'br':
                                                amt_list.append(clean_title(item.text))            

                                    for i in range(len(title_list)):
                                        try:
                                            item_list.append([title_list[i], amt_list[i]])
                                        except IndexError:
                                            item_list.append([title_list[i], '-'])
                                except Exception as e:
                                    continue
                        except Exception as e:
                            print(e)
                            
                    # parsing 된 결과가 9row 이상일 경우 파일에 쓰고 break
                    if len(item_list) >= 9:
                        for item in item_list:
                            #print("{}, {}".format(title, amt))
                            fp.write("{},{}\n".format(item[0], item[1]))
                        break
    except Exception as e:
        print(rcpno, e)

def main_proc(gubun):
    _driver = webdriver.Chrome('chromedriver')

    if gubun == 'KOSPI':
        fp = open(KOSPI_URL_FILE, 'r')
    elif gubun == 'KOSDAQ':
        fp = open(KOSDAQ_URL_FILE, 'r')

    target_items = [item.strip() for item in fp.readlines()]
    fp.close()

    target_items = {
    '017510,2012.06,20120810000103',
    '017510,2012.09,20121114000417',
    '017510,2012.12,20130401003200',
    '017510,2013.06,20130813000153',
    '017510,2013.09,20131114000780',
    '017510,2013.12,20140328000413',
    '017510,2014.03,20140513000090',
    '017510,2014.06,20140813000121',
    '017510,2014.09,20141113000314',
    '019660,2014.06,20140829001546',
    '022100,2017.03,20170512005033',
    '028150,1999.12,20000330000433',
    '032680,2015.03,20150529001036',
    '032680,2015.06,20150817001639',
    '032680,2015.09,20151207000331',
    '032680,2015.12,20160330003752',
    '032685,2015.03,20150529001036',
    '032685,2015.06,20150817001639',
    '032685,2015.09,20151207000331',
    '032685,2015.12,20160330003752',
    '036800,2015.03,20150515002283',
    '036800,2015.06,20150817001549',
    '036800,2015.09,20151209000161',
    '052190,2011.03,20110513001142',
    '053300,2015.06,20150817001054',
    '053300,2015.09,20151208000116',
    '053300,2015.12,20160330001372',
    '053300,2016.03,20160513000758',
    '053300,2016.06,20160812000160',
    '053300,2016.09,20161110000006',
    '053300,2016.12,20170331001587',
    '053300,2017.03,20170515002492',
    '058370,2011.09,20111114000714',
    '060150,2011.03,20110531000223',
    '060300,2010.03,20100525000076',
    '064760,2016.09,20161114000556',
    '065510,2015.09,20151113000526',
    '066590,2011.03,20110516001708',
    '072470,2012.09,20121114000837',
    '078130,2016.06,20160816001304',
    '078130,2016.09,20161114002009',
    '078130,2016.12,20170331005300',
    '083790,2013.03,20130530001130',
    '083790,2013.06,20130829000909',
    '092130,2011.12,20120214000016',
    '093380,2009.11,20100112000088',
    '095270,2016.09,20161114002446',
    '101730,2017.03,20170512006011',
    '109860,2016.06,20160816000982',
    '114190,2015.06,20150817000816',
    '114190,2015.09,20151116000261',
    '114190,2015.12,20160330001333',
    '114190,2016.03,20160516001796',
    '114190,2016.06,20160816001239',
    '114190,2016.09,20161111000700',
    '114190,2016.12,20170330001309',
    '114190,2017.03,20170515003289',
    '119500,2010.09,20101111000395',
    }

    total_count = len(target_items)
    start_time = datetime.now()

    for idx, item in enumerate(target_items):
        stock_cd, quarter, rcpno = item.split(',')
        report_parse(_driver, gubun, stock_cd, quarter, rcpno)
        #print("{},{},{}".format(stock_cd, quarter, rcpno))
        sleep(0.7)

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
    main_proc('KOSDAQ')
    #main_proc('KOSPI')
