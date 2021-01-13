import random
import re

import httpx

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.37'}
class Musixmatch:
    def __init__(self, usertoken:[str, list]):
        self.token = usertoken
        self.http = httpx.Client(http2=True)

    def search(self, q, limit):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = self.http.get('https://apic.musixmatch.com/ws/1.1/macro.search', params=dict(
            app_id='android-player-v1.0',
            usertoken=utoken,
            q=q,
            page=0,
            page_size=limit+1,
            format='json'
        ), headers=headers)
        return a.json()

    def lyrics(self, id):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = self.http.get('https://apic.musixmatch.com/ws/1.1/macro.subtitles.get', params=dict(
            app_id='android-player-v1.0',
            usertoken=utoken,
            track_id=id,
            format='json'
        ), headers=headers)

        return a.json()

    def translation(self, id, lang):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = self.http.get('https://apic.musixmatch.com/ws/1.1/crowd.track.translations.get', params=dict(
            app_id='android-player-v1.0',
            usertoken=utoken,
            selected_language=lang,
            track_id=id,
            part='user',
            format='json'
        ), headers=headers)
        return a.json()

    def auto(self, q, lang, limit=5):
        print(limit)
        a = self.search(q, limit)
        res = a['message']['body']['macro_result_list']['track_list'] if limit != 1 else [a['message']['body']['macro_result_list']['best_match']]
        ret = []
        for i in res:
            id = i['track']['track_id'] if 'track' in i else i['id']
            b = self.lyrics(id)
            letra = b['message']['body']['macro_calls']['track.lyrics.get']['message']['body']['lyrics']['lyrics_body']
            l = {'letra':letra}
            c = self.translation(id, lang)
            tr = letra
            for i in c['message']['body']['translations_list']:
                escape = re.escape(i['translation']['snippet'])
                tr = re.sub(f'^{escape}$', i['translation']['description'], tr, flags=re.M)
            b['translate'] = tr
            ret.append(b)
        return ret
