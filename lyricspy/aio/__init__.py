import asyncio
import re
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from .. import parse_let, parse, parse_gen, headers


http = httpx.AsyncClient(http2=True)

loop = asyncio.get_event_loop()


class Genius:
    @staticmethod
    async def search(q, per_page=4):
        r = await http.get("https://genius.com/api/search/multi?", params=dict(q=q, per_page=per_page))
        a = r.json()
        hits = [hit['result'] for section in a['response']['sections'] for hit in section['hits'] if
                hit['index'] == 'lyric']
        return hits

    @staticmethod
    async def letra(url, remove):
        r = await http.get(url)
        data = r.text
        ret = await loop.run_in_executor(None, parse_gen, data, url, remove)
        return ret

    async def auto(self, q, limit=4, remove=True):
        a = await self.search(q, per_page=limit)
        ret = []
        for i in a:
            b = await self.letra(i['url'], remove)
            ret.append(b)
        return ret


class Letras:
    @staticmethod
    async def letra(query, **kwargs):
        query = query.replace('www.letras', 'm.letras')
        r = await http.get(query, params=dict(**kwargs))
        data = r.text
        ret = await loop.run_in_executor(None, parse_let, data, query)
        return ret

    async def auto(self, query, limit=4):
        result = []
        n = 0
        r = await self.search(query)
        for i in r:
            a = await self.letra(i)
            result.append(a)
            n += 1
            if n == limit:
                break

        return result

    @staticmethod
    async def search(query):
        r = await http.get('https://studiosolsolr-a.akamaihd.net/letras/app2/', params=dict(q=query))
        a = r.json()
        x = []
        n = 0
        for i in a['highlighting']:
            if 'mus' in i:
                g = a['response']['docs'][n]
                x.append(f"https://www.letras.mus.br/{g['dns']}/{g['url']}")
            n += 1
        return x


class Musixmatch:
    @staticmethod
    async def letra(query):
        r = await http.get(query, headers=headers)
        data = r.text
        return await loop.run_in_executor(None, parse, data, query)

    @staticmethod
    async def search(q):
        r = await http.get(f'https://www.musixmatch.com/pt-br/search/{q}', headers=headers)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        b = soup.find_all('li', {'class': 'showArtist showCoverart'})
        res = []
        for i in b[1:]:
            res.append('https://www.musixmatch.com' + i.find('a', {'class': 'title'}).get('href'))
        return res

    async def auto(self, query, limit=4):
        result = []
        n = 0
        r = await self.search(quote_plus(query))
        for i in r:
            if re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', i) and '/translation' not in i and '/artist' not in i:
                try:
                    a = await self.letra(i)
                    result.append(a)
                    n += 1
                except AttributeError:
                    pass
                if n == limit:
                    break

        return result


# For compat
muximatch = Musixmatch
genius = Genius
letras = Letras
