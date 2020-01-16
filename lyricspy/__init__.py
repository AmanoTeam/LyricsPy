from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re
import urllib3

def letra(query):
    tr = 'a'
    query = query.replace('www.letras', 'm.letras')
    http = urllib3.PoolManager()
    r = http.request("get",query)
    soup = BeautifulSoup(r.data, "html.parser")
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
    ret = {'autor': autor, 'musica': musica, 'letra': b.replace('\n\n\n', '\n\n'), 'link': r.url}
    if 'a' not in tr:
        b = ''
        for i in tr.find_all('p'):
            b += md(str(i))
        ret['traducao'] = b.replace('\n\n\n', '\n\n')

    return ret


def auto(query, limit=4):
    result = []
    n = 0
    for i in search(q='site:letras.mus.br ' + query):
        if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', i) and '/traducao.html' not in i:
            try:
                a = letra(i)
                result.append(a)
                n += 1
            except AttributeError:
                pass
        if n == limit:
            break

    return result

def search(q, **kwargs):
    a = []
    http = urllib3.PoolManager()
    rt = http.request("get","https://www.bing.com/search", fields=dict(q=q, **kwargs))
    soupt = BeautifulSoup(rt.data, "html.parser")
    results = soupt.find("ol", {"id":"b_results"})
    lists = results.findAll("li", {"class":"b_algo"})
    for item in lists:
        item_text = item.find("a").text
        item_href = item.find("a").attrs["href"]
        if item_text and item_href:
            a.append(item_href)
    return a

print(auto('oi', limit=1))
