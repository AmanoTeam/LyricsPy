from bs4 import BeautifulSoup
import urllib3
from urllib.parse import quote_plus
import re

http = urllib3.PoolManager()

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

def letra(query, **kwargs):
    r = http.request('get',query, headers=headers)
    data = r.data
    return parse(data, query)

def search(q):
    r = http.request('get', f'https://www.musixmatch.com/pt-br/search/{q}', headers=headers)
    data = r.data
    soup = BeautifulSoup(data, "html.parser")
    b = soup.find_all('li', {'class':'showArtist showCoverart'})
    res = []
    for i in b[1:]:
        res.append('https://www.musixmatch.com'+i.find('a',{'class':'title'}).get('href'))
    return res

def auto(query, limit=4):
    result = []
    n = 0
    for i in search(quote_plus(query)):
        if re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', i) and not '/translation' in i and not '/artist' in i:
            try:
                a = letra(i)
                result.append(a)
                n += 1
            except AttributeError:
                pass
            if n == limit:
                break

    return result

def parce_tr(url):
    if not '/' in url[-1]:
        url = url+'/'
    get = f'{url}traducao/portugues'
    r = http.request('get', get, headers=headers)
    data = r.data
    soup = BeautifulSoup(data, "html.parser")
    x = soup.find_all('div', {'class':'col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6'})
    n = 0
    for i in x:
        if i.get_text() == 'Tradução para Portugues':
            break
        n += 1
    b = soup.find_all('div', {'class':'mxm-translatable-line-readonly'})
    c = []
    for i in b:
        d = i.find_all('div', {'class':'col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6'})
        c.append(d[n].get_text())
    trad = '\n'.join([x for x in c])
    return trad

def parse(data, url):
    soup = BeautifulSoup(data, "html.parser")
    autor = soup.find('a', {'class':'mxm-track-title__artist mxm-track-title__artist-link'})
    b = ''
    x = soup.find_all('span', {'class':['lyrics__content__ok','lyrics__content__warning','lyrics__content__error']})
    for i in x:
        b += i.get_text()
    musica = str(soup.find('h1', {'class': 'mxm-track-title__track'})).split('</small>')[1].replace('</h1>','')
    ret = {'autor': autor.get_text(), 'musica': musica, 'letra': b, 'link': url}
    if soup.find('i', {'class':'translations flag br-flag'}):
            ret['traducao'] = parce_tr(url)
    return ret
