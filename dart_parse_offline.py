# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import re
import os
import logging

from datetime import datetime, timedelta
from dart_util import *

URL_PREFIX = 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='

logging.basicConfig(filename='dart_parse.log', level=logging.DEBUG)


def report_parse(stock_cd, year, month, rcpno):
    unit = ''
    p_unit = re.compile(u'단위\s*:\s*(\w*)')

    logging.debug("======================================================")
    logging.debug("{}.{}.{}.{} start".format(stock_cd, year, month, rcpno))

    try:
        read_file_path = "html\{}.{}.{}.{}.html".format(stock_cd, year, month, rcpno)
        write_file_path = "parsed\{}.{}.{}.{}.txt".format(stock_cd, year, month, rcpno)

        item_list = []
        
        rfp = open(read_file_path, 'r', encoding='utf-8')
        wfp = open(write_file_path, 'w', encoding='utf-8')

        wfp.write("{}.{}.{}.{}\n".format(stock_cd, year, month, rcpno))
        
        soup = BeautifulSoup(rfp.read(), "html.parser")
        elements = soup.find_all(['p', 'table'])

        # 단위
        for e in elements:
            if p_unit.search(e.text) is not None:
                unit = p_unit.search(e.text).group(1)
                break

        wfp.write("{}\n".format(unit))

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
                        title_list = []
                        amt_list = []

                        # 병합된 cell 
                        if cols[0].has_attr('colspan'):
                            continue

                        try:
                            for item in cols[0].children:
                                if isinstance(item, NavigableString):
                                    title = clean_title(item)

                                    if len(title) > 0:
                                        title_list.append(title)

                                elif isinstance(item, Tag):
                                    title = clean_title(item.text)

                                    if item.name != 'br' and len(title) > 0:
                                        title_list.append(title)

                            for item in cols[1].children:
                                if isinstance(item, NavigableString):
                                    amt = clean_amt(item)

                                    if len(amt) > 0:
                                        amt_list.append(amt)

                                elif isinstance(item, Tag):
                                    amt = clean_amt(item.text)

                                    if item.name != 'br' and len(amt) > 0:
                                        amt_list.append(amt)

                            for i in range(len(title_list)):
                                try:
                                    item_list.append([title_list[i], amt_list[i]])
                                except IndexError:
                                    pass
                        except Exception as e:
                            logging.error('col' + e)
                    except Exception as e:
                        logging.error('row' + e)
                        
                # parsing 된 결과가 9row 이상일 경우 파일에 쓰고 break
                if len(item_list) >= 9:
                    for item in item_list:
                        wfp.write("{},{}\n".format(item[0], item[1]))
                    break
    except Exception as e:
        logging.error('item', 'e')

    logging.debug("{}.{}.{}.{} end".format(stock_cd, year, month, rcpno))

def main_proc():
    target_items = [item for item in os.listdir('html')]

    #target_items = ['000030.2001.12.20020401000085.html', '000020.2009.03.20090629000271.html']

    total_count = len(target_items)
    start_time = datetime.now()

    for idx, item in enumerate(target_items):
        stock_cd, year, month, rcpno, _ = item.split('.')
        report_parse(stock_cd, year, month, rcpno)

        if idx > 1 and (idx+1) % 10 == 0:
            end_time = datetime.now()
            gap_time_sec = (end_time - start_time).total_seconds()

            # 남은시간 : 지금까지 처리한 건당 평균시간(초) * 남은 건수
            avg_time_per = gap_time_sec / (idx+1)
            left_time = avg_time_per * (total_count-idx-1)
            estimated_end_time = end_time + timedelta(seconds=left_time)
            perc = round((idx+1)/total_count*100, 2)

            print("[{}/{}] 진행율 : {}%, 건당소요시간 : {}초, 예상종료일시 : {}".format(
                idx+1, total_count, perc, round(avg_time_per, 2), estimated_end_time.strftime('%m/%d %H:%M')))

    final_time = datetime.now()
    elapsed_time = final_time - start_time
    print("총 걸린시간 : {}".format(str(elapsed_time)))
    print("총 건수 : {}".format(total_count))

if __name__ == '__main__':
    main_proc()
