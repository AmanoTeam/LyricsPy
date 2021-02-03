import random
import re

import httpx
from bs4 import BeautifulSoup

from asyncio import get_event_loop

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.37'}
class Musixmatch:
    def __init__(self, usertoken:[str, list]):
        self.token = usertoken
        self.http = httpx.AsyncClient(http2=True)

    async def search(self, q, limit):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = await self.http.get('https://apic.musixmatch.com/ws/1.1/macro.search', params=dict(
            app_id='android-player-v1.0',
            usertoken=utoken,
            q=q,
            page=0,
            page_size=limit+1,
            format='json'
        ), headers=headers)
        return a.json()

    async def lyrics(self, id):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = await self.http.get('https://apic.musixmatch.com/ws/1.1/macro.subtitles.get', params=dict(
            app_id='android-player-v1.0',
            usertoken=utoken,
            track_id=id,
            format='json'
        ), headers=headers)

        return a.json()

    async def translation(self, id, lang):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = await self.http.get('https://apic.musixmatch.com/ws/1.1/crowd.track.translations.get', params=dict(
            app_id='android-player-v1.0',
            usertoken=utoken,
            selected_language=lang,
            track_id=id,
            part='user',
            format='json'
        ), headers=headers)
        return a.json()

    async def auto(self, q, lang, limit=5):
        a = await self.search(q, limit)
        res = a['message']['body']['macro_result_list']['track_list'] if limit != 1 else [a['message']['body']['macro_result_list']['best_match']]
        ret = []
        for i in res:
            id = i['track']['track_id'] if 'track' in i else i['id']
            b = await self.lyrics(id)
            letra = b['message']['body']['macro_calls']['track.lyrics.get']['message']['body']['lyrics']['lyrics_body']
            l = {'letra':letra}
            c = await self.translation(id, lang)
            tr = letra
            for i in c['message']['body']['translations_list']:
                escape = re.escape(i['translation']['snippet'])
                tr = re.sub(f'^{escape}$', i['translation']['description'], tr, flags=re.M)
            b['translate'] = tr
            ret.append(b)
        return ret

    def parce(self, q):
        autor = q['message']['body']['macro_calls']['matcher.track.get']['message']['body']['track']['artist_name']
        musica = q['message']['body']['macro_calls']['matcher.track.get']['message']['body']['track']['track_name']
        letra = q['message']['body']['macro_calls']['track.lyrics.get']['message']['body']['lyrics']['lyrics_body']
        link = q['message']['body']['macro_calls']['track.lyrics.get']['message']['body']['lyrics']['backlink_url'].split('?')[0]
        traducao = q['translate']
        id = q['message']['body']['macro_calls']['matcher.track.get']['message']['body']['track']['track_id']
        ret = {'autor': autor, 'musica': musica, 'letra': letra, 'link': link, 'traducao':traducao, 'id':id}
        return ret

class Letras:
    def __init__(self):
        self.http = httpx.AsyncClient(http2=True)

    async def letra(self, query, **kwargs):
        link = query['link'].replace('www.letras', 'm.letras')
        r = await self.http.get(link, params=dict(**kwargs))
        tr = None
        soup = BeautifulSoup(r.text, "html.parser")
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
        query.update({'letra': b})
        if tr is not None:
            b = "\n\n".join(i.get_text() for i in a.find_all('p'))
            query.update({'traducao':b})
        else:
            query.update({'traducao':None})
        return query

    async def search(self, query):
        r = await self.http.get('https://studiosolsolr-a.akamaihd.net/letras/app2/', params=dict(q=query))
        a = r.json()
        x = []
        n = 0
        for i in a['highlighting']:
            if 'mus' in i:
                g = a['response']['docs'][n]
                g.update({'link':f"https://www.letras.mus.br/{g['dns']}/{g['url']}"})
                x.append(g)
            n += 1
        return x

    async def auto(self, query, limit=4):
        result = []
        n = 0
        for i in await self.search(query):
            a = await self.letra(i)
            result.append(a)
            n += 1
            if n == limit:
                break
        return result

    def parce(self, q):
        autor = q['art']
        musica = q['txt']
        letra = q['letra']
        link = q['link']
        traducao = q['traducao']
        id = q['id']
        ret = {'autor': autor, 'musica': musica, 'letra': letra, 'link': link, 'traducao':traducao, 'id':id}
        return ret
