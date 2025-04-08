import requests
import time
# 使用多进程
from multiprocessing import Pool,Lock,Manager
import queue
import argparse
import os
import sys
sys.path.append('/data03/home/yanleiyu/miniconda3/envs/epigenetics/lib/python3.9/site-packages')
from bs4 import BeautifulSoup

while True:
    try:
        response = requests.get('https://rest.uniprot.org/uniprotkb/A0A060D7H5.fasta')
        webpage_content = response.text
        print('connect success!!!')
        break
    except:
        print('connect again!!!')

with open('down_test.html','w') as outfile:
    outfile.write(webpage_content)









