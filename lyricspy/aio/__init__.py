from bs4 import BeautifulSoup
import aiohttp
from urllib.parse import quote_plus
import re
import json
from .. import parce_let, parce

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

class letras():
    async def letra(self, query, **kwargs):
        query = query.replace('www.letras', 'm.letras')
        async with aiohttp.ClientSession() as session:
            r = await session.get(query, params=dict(**kwargs))
            data = await r.read()
        ret = parce_let(data, query)
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

    async def search(self, query):
        async with aiohttp.ClientSession() as session:
            r = await session.get('https://studiosolsolr-a.akamaihd.net/letras/app2/', params=dict(q=query))
            a = json.loads(await r.read())
        x = []
        n = 0
        for i in a['highlighting']:
            if 'mus' in i:
                g = a['response']['docs'][n]
                x.append(f"https://www.letras.mus.br/{g['dns']}/{g['url']}")
            n += 1
        return x
    
class muximatch():
    async def letra(self, query, **kwargs):
        async with aiohttp.ClientSession() as session:
            r = await session.get(query, headers=headers)
            data = await r.read()
        return parce(data, query)
    
    async def search(self, q):
        async with aiohttp.ClientSession() as session:
            r = await session.get(f'https://www.musixmatch.com/pt-br/search/{q}', headers=headers)
            data = await r.read()
        soup = BeautifulSoup(data, "html.parser")
        b = soup.find_all('li', {'class':'showArtist showCoverart'})
        res = []
        for i in b[1:]:
            res.append('https://www.musixmatch.com'+i.find('a',{'class':'title'}).get('href'))
        return res
    
    async def auto(self, query, limit=4):
        result = []
        n = 0
        r = await self.search(quote_plus(query))
        for i in r:
            if re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', i) and not '/translation' in i and not '/artist' in i:
                try:
                    a = await self.letra(i)
                    result.append(a)
                    n += 1
                except AttributeError:
                    pass
                if n == limit:
                    break
    
        return result
