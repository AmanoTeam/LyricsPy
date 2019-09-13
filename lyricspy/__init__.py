import requests
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re
import urllib.parse
import googlesearch

def letra(query,limit=4):
    tr = 'a'
    query = query.replace('www.letras', 'm.letras')
    r = requests.get(query)
    soup = BeautifulSoup(r.text, "html.parser")
    a = soup.find('div', "lyric-cnt g-1")
    if a is None:
        a = soup.find('div', "lyric-tra_l")
        tr = soup.find('div', "lyric-tra_r")
    b = ''
    for i in a.find_all('p'):
        b += md(str(i))
    c = soup.find("div", "lyric-title g-1")
    musica = c.find('h1').get_text()
    autor = c.find('a').get_text()
    ret = {'autor': autor, 'musica': musica, 'letra': b.replace('\n\n\n','\n\n'), 'link': r.url}
    if 'a' not in tr:
        b = ''
        for i in tr.find_all('p'):
            b += md(str(i))
        ret['traducao'] = b.replace('\n\n\n','\n\n')

    return ret


def auto(query, limit=4):
    result = []
    query = urllib.parse.quote(query)
    n = 0
    for i in googlesearch.search('site:letras.mus.br ' + query):
        if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', i):
            try:
                a = letra(i)
                result.append(a)
                n += 1
            except:
                pass
        if n == limit:
            break

    return result
