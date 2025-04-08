import requests
import time
from concurrent.futures import ThreadPoolExecutor
import queue
import argparse
import os
from bs4 import BeautifulSoup
import sys
sys.path.append('/data03/home/yanleiyu/miniconda3/envs/epigenetics/lib/python3.9/site-packages')

def get_url_list(mem_file):
    '''
    从MEME文件中提取URL列表
    :param mem_file: MEME文件路径
    :return: URL列表
    '''
    URL_list = []
    infile_handle = open(mem_file,'r')
    for line_meme in infile_handle:
        line_meme = line_meme.strip()
        if line_meme.startswith('URL'):
            URL_list.append(line_meme.split()[1])
    return URL_list


def craw(url,q):
    while True:
        try:
            response = requests.get(url)
            webpage_content = response.text
            print('connect success!!!')
            break
        except:
            print('connect again!!!')
            time.sleep(0.1)
    # 解析 HTML
    soup = BeautifulSoup(webpage_content, 'html.parser')
    # 查找表格
    table = soup.find('table', {'class': 'table table-hover', 'id': 'matrix-detail'})
    # 提取行数据
    Tf_information_dict = {}
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            key = tds[0].get_text(strip=True).replace(':', '').strip()
            value = tds[1].get_text(strip=True)
            if value == '':
                value = 'Na'
            Tf_information_dict[key] = value
            
    # 打印结果print(Tf_information_dict)
    Tf_information_line = '\t'.join([\
                                    Tf_information_dict['Name'],\
                                    Tf_information_dict['Matrix ID'],\
                                    Tf_information_dict['Class'],\
                                    Tf_information_dict['Family'],\
                                    Tf_information_dict['Collection'],\
                                    Tf_information_dict['Taxon'],\
                                    Tf_information_dict['Species'],\
                                    Tf_information_dict['Data Type'],\
                                    Tf_information_dict['Validation'],\
                                    Tf_information_dict['Uniprot ID'],\
                                    Tf_information_dict['Source'],\
                                    Tf_information_dict['Comment']\
                                        ])
    q.put(Tf_information_line)# 第十个元素是uniprot id，如果存在，就下载序列

if __name__ == '__main__':
    # parameter parse
    my_parser = argparse.ArgumentParser(allow_abbrev=False, add_help=True, prefix_chars='-',description='Help information')  #allow_abbrev: allow to abbreviate argv or not
    my_parser.add_argument('--input', '-i', type=str,required=False, help='the meme file of jarspar database')
    my_parser.add_argument('--outdir', '-o', type=str, default='./', required=False, help='output directory:')
    my_parser.add_argument('--theads', '-t', type=int, default=150, required=False,help='the maximum theads allowed to run for user')
 
    args = my_parser.parse_args()  # class argsparse namespace

    infile = os.path.abspath(args.input)
    outdir = os.path.abspath(args.outdir)
    threads = args.theads


    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print("Create output directory:"+ outdir)
    else:
        print("Exist output directory:"+ outdir)

    stat_time = time.time()
    # first step,get the all urls in the meme file
    URL_list = get_url_list(infile)
    print('URL_list的数量',len(URL_list))

    # second step,get the information about TF of the urls
    q = queue.Queue()
    pool = ThreadPoolExecutor(max_workers=threads)
    for url in URL_list:
        pool.submit(craw, url, q)
    pool.shutdown()

    end_time = time.time()
    print('q.size',q.qsize())
    print('耗时', end_time - stat_time)


