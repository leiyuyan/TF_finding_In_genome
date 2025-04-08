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

def down_load_uniprot(url,Name,Matrix_ID,Uniprot_ID):
    '''
    下载uniprot id对应的序列
    :param url: uniprot id对应的url
    :return: 序列
    '''
    while True:
        try:
            response = requests.get(url)
            webpage_content = response.text
            print('connect success!!!')
            break
        except:
            print(f'{url} connect again!!!')
            time.sleep(0.1)
    modified_list = []
    for line in webpage_content.split('\n'):
        line = line.strip()
        if line.startswith('>'):
            uniprot_id = f">{Name}@@@{Matrix_ID}@@@{Uniprot_ID}\t{line.strip('>')}"
            modified_list.append(uniprot_id)
        else:
            modified_list.append(line)

    return '\n'.join(modified_list)

def craw(url,q_tf_information,q_uniprot_sequence):
    while True:
        try:
            response = requests.get(url)
            webpage_content = response.text
            print('connect success!!!')
            break
        except:
            print(f'{url} connect again!!!')
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
    print(Tf_information_dict)
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
    q_tf_information.put(Tf_information_line)# 第十个元素是uniprot id，如果存在，就下载序列
    
    # 下载序列
    if Tf_information_dict['Uniprot ID'] != 'Na':
        url_uniprot = f"https://rest.uniprot.org/uniprotkb/{Tf_information_dict['Uniprot ID']}.fasta"
        uniprot_protein_sequence = down_load_uniprot(url_uniprot,Tf_information_dict['Name'],Tf_information_dict['Matrix ID'],Tf_information_dict['Uniprot ID'])
        q_uniprot_sequence.put(uniprot_protein_sequence)

def err_call_back(err):
    print(f'出错啦~ error：{str(err)}')# 可以找出错误，否者pool.apply_async不知道哪里出错了


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
    # 创建进程池
    pool = Pool(processes=threads)
    #apply_async异步提交任务，主进程不会阻塞等待子进程完成任务后才继续执行
    # q = queue.Queue() # 不能当作参数传入pool.apply_async()，否则会报错,无法理解，这种方式，经过测试时可以的
    #queue.Queue 是线程安全的，但在多进程中，每个进程都有自己的内存空间，因此 queue.Queue 不适合在多进程间共享数据。
    # 在你的代码中，q = queue.Queue() 是在主进程中创建的，但子进程无法直接访问主进程的内存空间，这会导致子进程无法向队列中添加数据。
    #改进方法 可以使用 multiprocessing.Manager().Queue() 来创建一个可以在多进程间共享的队列。这时，可以当作参数传入到函数中
    manager = Manager()
    q_tf_information = manager.Queue()
    q_uniprot_sequence = manager.Queue()
    for url in URL_list:
        pool.apply_async(craw, args=(url,q_tf_information,q_uniprot_sequence,), error_callback=err_call_back) # 不需要返回值，所以不需要results 将AsyncResult装起来，AsyncResult.get()会阻塞得到某个任务的reture值
    # 所有的url推到进程池中，关闭池，没有在池中的任务等待直到池中有新的资源；进程池不再接受新的任务。主进程不会阻塞等待子进程完成任务后才继续执行
    pool.close()
    # 等待所有任务完成，主进程阻塞
    pool.join()

    # 得到所有的结果
    unipro_url_list = []# https://rest.uniprot.org/uniprotkb/A0A060D7H5.fasta
    print(f"抓取到{q_tf_information.qsize()}个信息, meme文件中URL的数量一共是{len(URL_list)}")
    print(f"抓取到{q_uniprot_sequence.qsize()}uniprot蛋白质信息, meme文件中URL的数量一共是{len(URL_list)}")

    with open(os.path.join(outdir, 'jarspar_tf_protein_sequence.fasta'), 'w') as outfile_handle:
        while True:
            if q_uniprot_sequence.qsize() == 0:
                break
            else:
                outfile_handle.write(q_uniprot_sequence.get()+'\n')

    with open(os.path.join(outdir, 'jarspar_mapping_uniprot.xls'), 'w') as outfile_handle:
        print('\t'.join(['Name','Matrix ID','Class','Family','Collection','Taxon','Species','Data Type','Validation','Uniprot ID','Source','Comment']),file=outfile_handle)
        while True:
            if q_tf_information.qsize() == 0:
                break
            else:
                outfile_handle.write(q_tf_information.get()+'\n')

    end_time = time.time()
    print('耗时', end_time - stat_time)


