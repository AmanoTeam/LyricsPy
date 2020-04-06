from bs4 import BeautifulSoup
from seleniumrequestshtml import Chrome
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument("--headless")
webdriver = Chrome(chrome_options=options)
session = webdriver.requests_session

def letra(query, **kwargs):
    r = session.get(query)
    data = r.html.html
    return parse(data, r.url)

def search(q):
    r = session.get(f'https://www.musixmatch.com/pt-br/search/{q}')
    data = r.html.html
    soup = BeautifulSoup(data, "html.parser")
    b = soup.find_all('li', {'class':'showArtist showCoverart'})
    res = []
    for i in b[1:]:
        res.append('https://www.musixmatch.com'+i.find('a',{'class':'title'}).get('href'))
    return res

def auto(query, limit=4):
    result = []
    n = 0
    for i in search(query):
        if re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', i) and not '/translation' in i and not '/artist' in i:
            print(i)
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
        url += '/'
    get = f'{url}traducao/portugues'
    r = session.get(get)
    data = r.html.html
    soup = BeautifulSoup(data, "html.parser")
    b = soup.find_all('div', {'class':'mxm-translatable-line-readonly'})
    c = []
    for i in b:
        d = i.find_all('div', {'class':'col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6'})
        print(d)
        return d
        c.append(d[0].get_text())
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
