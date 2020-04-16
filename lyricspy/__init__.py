from bs4 import BeautifulSoup
import urllib3
from urllib.parse import quote_plus
import re
import json

http = urllib3.PoolManager()

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

class letras():
    def letra(self, query, **kwargs):
        tr = 'a'
        query = query.replace('www.letras', 'm.letras')
        r = http.request("get",query, fields=dict(**kwargs))
        soup = BeautifulSoup(r.data, "html.parser")
        a = soup.find('div', "lyric-cnt g-1")
        if a is None:
            a = soup.find('div', "lyric-tra_l")
            tr = soup.find('div', "lyric-tra_r")
        b = ''
        for i in a.find_all('p'):
            b += i.get_text()
        c = soup.find("div", "lyric-title g-1")
        musica = c.find('h1').get_text()
        autor = c.find('a').get_text()
        ret = {'autor': autor, 'musica': musica, 'letra': b.replace('\n\n\n', '\n\n'), 'link': query}
        if 'a' not in tr:
            b = ''
            for i in tr.find_all('p'):
                b += i.get_text()
            ret['traducao'] = b.replace('\n\n\n', '\n\n')
    
        return ret
    
    
    def auto(self, query, limit=4):
        result = []
        n = 0
        for i in self.search(query):
            a = self.letra(i)
            result.append(a)
            n += 1
            if n == limit:
                break
    
        return result

    def search(self, query):
        r = http.request('get', 'https://studiosolsolr-a.akamaihd.net/letras/app2/',fields=dict(q=query))
        a = json.loads(r.data.decode('utf-8'))
        x = []
        n = 0
        for i in a['highlighting']:
            if 'mus' in i:
                g = a['response']['docs'][n]
                x.append(f"https://www.letras.mus.br/{g['dns']}/{g['url']}")
            n += 1
        return x

class muximatch():
    def letra(self, query, **kwargs):
        r = http.request('get',query, headers=headers)
        data = r.data
        return self.parse(data, query)
    
    def search(self, q):
        r = http.request('get', f'https://www.musixmatch.com/pt-br/search/{q}', headers=headers)
        data = r.data
        soup = BeautifulSoup(data, "html.parser")
        b = soup.find_all('li', {'class':'showArtist showCoverart'})
        res = []
        for i in b[1:]:
            res.append('https://www.musixmatch.com'+i.find('a',{'class':'title'}).get('href'))
        return res
    
    def auto(self, query, limit=4):
        result = []
        n = 0
        for i in self.search(quote_plus(query)):
            if re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', i) and not '/translation' in i and not '/artist' in i:
                try:
                    a = self.letra(i)
                    result.append(a)
                    n += 1
                except AttributeError:
                    pass
                if n == limit:
                    break
    
        return result
    
    def parce_tr(self, url):
        if not '/' in url[-1]:
            url = url+'/'
        get = f'{url}traducao/portugues'
        r = http.request('get', get, headers=headers)
        data = r.data
        soup = BeautifulSoup(data, "html.parser")
        x = soup.find_all('div', {'class':'col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6'})
        n = 0
        for i in x:
            if i.find('img'):
                break
            n += 1
        b = soup.find_all('div', {'class':'mxm-translatable-line-readonly'})
        c = []
        for i in b:
            d = i.find_all('div', {'class':'col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6'})
            c.append(d[n].get_text())
        trad = '\n'.join([x for x in c])
        if x:
            return trad, x[n].get_text().split(' ',2)[-1]
    
    def parse(self, data, url):
        soup = BeautifulSoup(data, "html.parser")
        autor = soup.find('a', {'class':'mxm-track-title__artist mxm-track-title__artist-link'})
        b = ''
        x = soup.find_all('span', {'class':['lyrics__content__ok','lyrics__content__warning','lyrics__content__error']})
        musica = str(soup.find('h1', {'class': 'mxm-track-title__track'})).split('</small>')[1].replace('</h1>','')
        ret = {'autor': autor.get_text(), 'musica': musica, 'link': url, 'inst':False}
        for i in x:
            b += i.get_text()
        if b != '':
            ret['letra'] = b
        else:
            ret['inst'] = True
        if soup.find('i', {'class':'translations flag br-flag'}):
                ret['traducao'], ret['tr_name'] = self.parce_tr(url)
        return ret
