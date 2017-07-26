# -*- coding: utf-8 -*-
import os

def summarize_year(target_year):
    print('=' * 30)
    print("{}년도 시작".format(target_year))
    print('=' * 30)
    all_files = os.listdir('parsed')

    target_files = [item for item in all_files if item.split('.')[1] == target_year]
    item_list = []
    read_tot_count = len(target_files)

    for idx, f in enumerate(target_files):
        stock_cd, year, month, rcpno, _ = f.split('.')

        with open(os.path.join('parsed', f), 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
            unit = lines[1].replace(',', '.').strip()

            try:
                for line in lines[2:]:
                    title = line.split(',')[0]
                    amt = line.split(',')[1]

                    txt = ','.join([stock_cd, year, month, unit, rcpno, title, amt])

                    item_list.append([year, txt])
            except IndexError:
                pass

        if (idx+1) % 1000 == 0:
            print("{}/{} 번째 READ 완료".format(idx+1, read_tot_count))

    filename = "{}.txt".format(target_year)
    fp = open(filename, 'w', encoding='utf-8')
    item_tot_count = len(item_list)

    for idx, item in enumerate(item_list):
        fp.write("{}".format(item[1]))

        if (idx+1) % 10000 == 0:
            print("{}/{} 번째 WRITE 완료".format(idx+1, item_tot_count))

if __name__ == '__main__':
    for target_year in range(2000, 2018):
        summarize_year(str(target_year))