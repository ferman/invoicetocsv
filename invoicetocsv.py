import glob
from tqdm.auto import tqdm
import re
import requests
import pdfplumber
import pandas as pd
from collections import namedtuple

Inv = namedtuple('Inv', 'sold_to_text job_address_text invoice quantity um item description t price per amt')

for current_pdf_file in tqdm(glob.glob("invoices/*.pdf")):
  with pdfplumber.open(current_pdf_file) as my_pdf:
    page = my_pdf.pages[0]
    text = page.extract_text()
    sold_to = (10, 160, 200, 200)  # left, bottom, right, top
    job_address = (200, 160, 400, 200)  # left, bottom, right, Distance of top of line from top of page
    sold_to_text = page.crop(sold_to).extract_text()
    job_address_text = page.crop(job_address).extract_text()
#    print(sold_to_text)
#    print(job_address_text)
    
#    print(text)
    
    inv_data = re.compile(r'(\d{4}-\d{6})')
    
    inv_line_re = re.compile(r'(?P<Quantity>\d+)\s(?P<UM>EA)\s+(?P<Item>.\S+)\s+(?P<Description>.*\S+)\s+(?P<T>Y)\s+(?P<Price>\d+.\d+)\s+(?P<Per>EA)\s+(?P<Amount>\d+.\d+)')
    
    line_items = []
    for line in text.split('\n'):
    
        if inv_data.match(line):
            invoice, *inv_page = line.split()
    
        line = inv_line_re.search(line)
        if line:
            quantity = line.group(1)
            um = line.group(2)
            item = line.group(3)
            description = line.group(4)
            t = line.group(5)
            price = line.group(6)
            per = line.group(7)
            amt = line.group(8)
            line_items.append(Inv(sold_to_text, job_address_text, invoice, quantity, um, item, description, t, price, per, amt))
    		
    df = pd.DataFrame(line_items)
    df.head()
    df.to_csv('inv_lines.csv', mode='a', header=not bool(df.index.size))  # append to CSV file, write header only if file is empty
