import re
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup


http = httpx.Client(http2=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}


class Genius:
    @staticmethod
    def search(q, per_page=4):
        r = http.get("https://genius.com/api/search/multi?", params=dict(q=q, per_page=per_page))
        a = r.json()
        hits = [hit['result'] for section in a['response']['sections'] for hit in section['hits'] if
                hit['index'] == 'lyric']
        return hits

    @staticmethod
    def letra(url, remove=True):
        r = http.get(url)
        ret = parse_gen(r.text, url, remove)
        return ret

    def auto(self, q, limit=4, remove=True):
        a = self.search(q, per_page=limit)
        reslts = []
        for i in a:
            b = self.letra(i['url'], remove)
            reslts.append(b)
        return reslts


def parse_gen(data, query, remove):
    soup = BeautifulSoup(data, "html.parser")
    autor = soup.find('a', {'class': 'Link-h3isu4-0 dpVWpH SongHeader__Artist-sc-1b7aqpg-8 DYpgM'})
    if not autor:
        autor = soup.find('h1', {'class': 'header_with_cover_art-primary_info-title'})
    print(autor)
    autor = autor.get_text()
    musica = soup.find('h1', {'class': 'SongHeader__Title-sc-1b7aqpg-7'})
    print(musica)
    try:
        musica = musica.get_text()
    except:
        pass
    ret = soup.find("div", {'class': ['lyrics', 'Lyrics__Container-sc-1ynbvzw-2 jgQsqn']}).get_text()
    if remove:
        ret = re.sub('(\[.*?\])*', '', ret)
        ret = re.sub('\n{2}', '\n', ret)
    ret = {'autor': autor, 'musica': musica, 'letra': ret.strip("\n"), 'link': query}
    return ret


class Letras:
    @staticmethod
    def letra(query, **kwargs):
        query = query.replace('www.letras', 'm.letras')
        r = http.get(query, params=dict(**kwargs))
        ret = parse_let(r.text, query)
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

    @staticmethod
    def search(query):
        r = http.get('https://studiosolsolr-a.akamaihd.net/letras/app2/', params=dict(q=query))
        a = r.json()
        x = []
        n = 0
        for i in a['highlighting']:
            if 'mus' in i:
                g = a['response']['docs'][n]
                x.append(f"https://www.letras.mus.br/{g['dns']}/{g['url']}")
            n += 1
        return x


def parse_let(data, query):
    tr = None
    soup = BeautifulSoup(data, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    a = soup.find('div', "lyric-cnt g-1")
    # Songs with translation
    if a is None:
        a = soup.find('div', "lyric-tra_l")
        tr = soup.find('div', "lyric-tra_r")
    b = "\n\n".join(i.get_text() for i in a.find_all('p'))
    c = soup.find("div", "lyric-title g-1")
    musica = c.find('h1').get_text()
    autor = c.find('a').get_text()
    ret = {'autor': autor, 'musica': musica, 'letra': b, 'link': query}
    if tr is not None:
        b = "\n\n".join(i.get_text() for i in a.find_all('p'))
        ret['traducao'] = b
    return ret


def parse_tr(url):
    if '/' not in url[-1]:
        url = url + '/'
    get = f'{url}traducao/portugues'
    r = http.get(get, headers=headers)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    x = soup.find_all('div', {'class': 'col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6'})
    n = 0
    for i in x:
        if i.find('img'):
            break
        n += 1
    b = soup.find_all('div', {'class': 'mxm-translatable-line-readonly'})
    c = []
    for i in b:
        d = i.find_all('div', {'class': 'col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6'})
        c.append(d[n].get_text())
    trad = '\n'.join([x for x in c])
    if x:
        return trad, x[n].get_text().split(' ', 2)[-1]


def parse(data, url):
    soup = BeautifulSoup(data, "html.parser")
    autor = soup.find('a', {'class': 'mxm-track-title__artist mxm-track-title__artist-link'})
    x = soup.find_all('span', {'class': ['lyrics__content__ok', 'lyrics__content__warning', 'lyrics__content__error']})
    musica = str(soup.find('h1', {'class': 'mxm-track-title__track'})).split('</small>')[1].replace('</h1>', '')
    ret = {'autor': autor.get_text(), 'musica': musica, 'link': url, 'inst': False}
    b = "\n".join([i.get_text() for i in x])
    if b:
        ret['letra'] = b
    else:
        ret['inst'] = True
    if soup.find('i', {'class': 'translations flag br-flag'}):
        ret['traducao'], ret['tr_name'] = parse_tr(url)
    return ret


class Musixmatch:
    @staticmethod
    def letra(query):
        r = http.get(query, headers=headers)
        data = r.text
        return parse(data, query)

    @staticmethod
    def search(q):
        r = http.get(f'https://www.musixmatch.com/pt-br/search/{q}', headers=headers)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        b = soup.find_all('li', {'class': 'showArtist showCoverart'})
        res = []
        for i in b[1:]:
            res.append('https://www.musixmatch.com' + i.find('a', {'class': 'title'}).get('href'))
        return res

    def auto(self, query, limit=4):
        result = []
        for i, res in enumerate(self.search(quote_plus(query))):
            if re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', res) and '/translation' not in res and '/artist' not in res:
                try:
                    a = self.letra(res)
                    result.append(a)
                except AttributeError:
                    pass
                if i + 1 == limit:
                    break

        return result


# For compat
muximatch = Musixmatch
genius = Genius
letras = Letras
