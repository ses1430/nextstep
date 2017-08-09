import pandas as pd
import logging
from time import sleep

def_columns = ['종목코드', '년월', '매출액', '영업이익', '순이익', '연결순이익', '자산총계', '부채총계', '자본총계']

def get_data_from_sejongdata(gubun, stock_cd):
    '''세종데이터로부터 재무제표를 긁어오는 함수
    gubun : 0-주재무재표, 1-IFRS(연결), 2-IFRS(별도)
    stock_cd : 종목코드(6자리)
    '''
    url = 'http://www.sejongdata.com/business_include_fr/table_main{}_bus_01.html?no={}&gubun=1'.format(gubun, stock_cd)
    df1 = pd.read_html(url)[1].T
    df1[0] = df1[0].str.replace(r'[^\d]', '')
    df1 = df1.drop(df1.index[[0]])
    
    sleep(0.5)
        
    url = 'http://www.sejongdata.com/business_include_fr/table_main{}_bus_01.html?no={}&gubun=2'.format(gubun, stock_cd)
    df2 = pd.read_html(url)[1].T
    df2[0] = df2[0].str.replace(r'[^\d]', '')
    df2 = df2.drop(df2.index[[0]])
    
    df = pd.concat([df1, df2])
    df = df.dropna(thresh=7)
    df.insert(0, 'cd', stock_cd)
    
    df.columns = def_columns
    
    return df
    
mylogger = logging.getLogger()
mylogger.setLevel(logging.INFO)

if not mylogger.hasHandlers():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    mylogger.addHandler(stream_hander)

df = pd.DataFrame(columns=def_columns)

with open('stock_cd.txt', 'r') as fp:
    for idx, stock in enumerate(fp):
        df = df.append(get_data_from_sejongdata('0', stock.strip()))
        if (idx+1)%10 == 0:
            mylogger.info(idx+1)
            
        sleep(1)
        
    df.to_csv('result.csv', index=False, quotechar="'")