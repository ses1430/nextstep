# -*- coding: utf-8 -*-
import re


def get_quarter_from_rcpno(rcpno):
    year = int(rcpno[0:4])
    month = rcpno[4:6]

    if month in ('01', '02', '03'):
        quarter = str(year-1) + '.' + '12'
    elif month in ('04', '05', '06'):
        quarter = str(year) + '.' + '03'
    elif month in ('07', '08', '09'):
        quarter = str(year) + '.' + '06'
    elif month in ('10', '11', '12'):
        quarter = str(year) + '.' + '09'

    return quarter


def clean_title(title):
    result = re.sub('[\s\[\]\,ㆍ]', '', title.strip())  # 쓸데없는 문자 제거
    #result = re.sub('\([&\sa-zA-Z]\)', '', result)    # 괄호안 제거 (영문, 특수문자)
    return result


def clean_amt(amt):
    result = re.sub('[\(\)\[\],]', '', amt.strip())
    result = re.sub('[△Δ]', '-', result)

    # 숫자가 없으면 빈값 리턴
    if re.sub('[\d]', '', result) == result:
        return ''
    # -, 숫자가 아닌 다른 값이 포함되어 있으면 빈값 리턴
    elif re.search('[^-0-9]', result) is not None:
        return ''
    else:
        return result
