#-*- coding: utf-8 -*-
from __future__ import print_function
import sys, os.path, re
from pdfminer.psparser import PSKeyword, PSLiteral, LIT
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
import logging
from tabula import convert_into

logging.basicConfig(level=logging.DEBUG)
current_path = os.getcwd()
pdf_path = os.path.join(current_path, 'pdf')
csv_path = os.path.join(current_path, 'csv')

# get full paths of pdf files
def get_pdf_files():
    return [item for item in os.listdir(pdf_path) if item.endswith('.pdf')]

# get pageno of pdf file
def get_pageno(pdf_file):
    logging.debug('get_pageno in...' + pdf_file)
    with open(pdf_file, 'rb') as fp:
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        pages = dict( (page.pageid, pageno) for (pageno,page) in enumerate(PDFPage.create_pages(doc)) )

        # Get the outlines of the document.
        outlines = doc.get_outlines()
        for (level,title,dest,a,se) in outlines:
            pageno = pages[dest[0].objid]
            # III. 재무에 관한 사항 페이지 찾기
            if title.startswith((u'III', u'Ⅲ')):
                return pageno

if __name__ == '__main__':
    pdf_files = get_pdf_files()

    for p in pdf_files:
        logging.debug(p)
        pageno = get_pageno(os.path.join(pdf_path, p))
        convert_into(os.path.join(pdf_path, p), os.path.join(pdf_path, p.replace('.pdf', '.csv')), output_format='csv', pages=[pageno+1, pageno+2], silent=True, multiple_tables=False)

    #convert_into('https://dart.fss.or.kr/pdf/download/pdf.do?rcp_no=20000814000482&dcm_no=89871', 'test.csv', output_format='csv')
