#!/data03/home/yanleiyu/miniconda3/envs/epigenetics/bin/python
import requests
import time
import queue
import os
from bs4 import BeautifulSoup

URL = 'http://jaspar.genereg.net/matrix/MA1809.2'
while True:
    try:
        response = requests.get(URL)
        webpage_content = response.text
        print('connect success!!!')
        break
    except:
        print('connect again!!!')
        time.sleep(0.1)
with open('test.txt','w') as outfile:
    outfile.write(webpage_content)

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
        
print(Tf_information_dict)
# 打印结果
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
print(Tf_information_line )

# {'Name': 'GLYMA-07G038400'}
# {'Matrix ID': 'MA1809.2'}
# {'Class': 'C3H zinc finger factors'}
# {'Family': 'GRF'}
# {'Collection': 'CORE'}
# {'Taxon': 'Plants'}
# {'Species': 'Glycine max'}
# {'Data Type': 'ChIP-seq'}
# {'Validation': '29985961'}
# {'Uniprot ID': 'I1KHB3'}
# {'Source': 'GSE152313'}
# {'Comment': 'Na'}




