from requests import get
from bs4 import BeautifulSoup

row_data = []
url='https://en.wikipedia.org/wiki/List_of_Wikipedias'
headers = {'Accept-Encoding': 'identity'}
page = get(url, headers=headers)

soup = BeautifulSoup(page.text)
mylist=list()
tb = soup.find_all('table')[4]
for row in tb.find_all('tr'):
    cols = row.find_all('td')
    row_data.append([ele.text.strip() for ele in cols])

for row in row_data:
    if row:
        with open('lingwiki\\data\\wiki_lang_codes.txt', 'a', encoding='utf-8') as f:
            f.write(row[1] + '\n')