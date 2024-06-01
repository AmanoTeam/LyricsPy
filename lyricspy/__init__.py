import random
import re
from typing import Union

import httpx
from bs4 import BeautifulSoup

__version__ = "3.0.0a0"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.37"
}


class Musixmatch:
    def __init__(self, usertoken: Union[str, list]):
        self.token = usertoken
        self.http = httpx.AsyncClient(http2=True)

    async def search(self, q, limit):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/macro.search",
            params={
                "app_id": "android-player-v1.0",
                "usertoken": utoken,
                "q": q,
                "page": 0,
                "page_size": limit + 1,
                "format": "json",
            },
            headers=headers,
        )
        return a.json()

    async def lyrics(self, id):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/macro.subtitles.get",
            params={
                "app_id": "android-player-v1.0",
                "usertoken": utoken,
                "track_id": id,
                "format": "json",
            },
            headers=headers,
            follow_redirects=True,
        )

        return a.json()

    async def spotify_lyrics(self, artist, track):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/macro.subtitles.get",
            params={
                "app_id": "android-player-v1.0",
                "usertoken": utoken,
                "q_artist": artist,
                "q_track": track,
                "format": "json",
            },
            headers=headers,
            follow_redirects=True,
        )

        return a.json()

    async def translation(self, id, lang, letra=None):
        utoken = random.choice(self.token) if type(self.token) is list else self.token
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/crowd.track.translations.get",
            params={
                "app_id": "android-player-v1.0",
                "usertoken": utoken,
                "selected_language": lang,
                "track_id": id,
                "part": "user",
                "format": "json",
            },
            headers=headers,
        )
        print(a.url)
        c = a.json()
        if c["message"]["body"]["translations_list"] and letra:
            tr = letra
            for i in c["message"]["body"]["translations_list"]:
                escape = re.escape(i["translation"]["snippet"])
                tr = re.sub(f"^{escape}$", i["translation"]["description"], tr, flags=re.M)
        elif c["message"]["body"]["translations_list"]:
            tr = True
        else:
            tr = None

        return tr

    async def auto(self, q=None, lang="pt", limit=5, id=None):
        print("auto", q, lang, limit, id)
        if q:
            a = await self.search(q, limit)
            res = (
                a["message"]["body"]["macro_result_list"]["track_list"]
                if limit != 1
                else [a["message"]["body"]["macro_result_list"]["best_match"]]
            )
        else:
            res = [id]
        ret = []
        for i in res:
            if not id:
                id = i["track"]["track_id"] if "track" in i else i["id"]
            b = await self.lyrics(id)
            letra = b["message"]["body"]["macro_calls"]["track.lyrics.get"]["message"]["body"][
                "lyrics"
            ]["lyrics_body"]
            c = await self.translation(id, lang, letra)
            b["translate"] = c
            ret.append(b)
        return ret

    def parse(self, q):
        autor = q["message"]["body"]["macro_calls"]["matcher.track.get"]["message"]["body"][
            "track"
        ]["artist_name"]
        musica = q["message"]["body"]["macro_calls"]["matcher.track.get"]["message"]["body"][
            "track"
        ]["track_name"]
        letra = q["message"]["body"]["macro_calls"]["track.lyrics.get"]["message"]["body"][
            "lyrics"
        ]["lyrics_body"]
        link = q["message"]["body"]["macro_calls"]["track.lyrics.get"]["message"]["body"][
            "lyrics"
        ]["backlink_url"].split("?")[0]
        traducao = q.get("translate", None)
        id = q["message"]["body"]["macro_calls"]["matcher.track.get"]["message"]["body"]["track"][
            "track_id"
        ]
        return {
            "autor": autor,
            "musica": musica,
            "letra": letra,
            "link": link,
            "traducao": traducao,
            "id": id,
        }


class Letras:
    def __init__(self):
        self.http = httpx.AsyncClient(http2=True)

    async def letra(self, query, **kwargs):
        link = query["link"].replace("www.letras", "m.letras")
        r = await self.http.get(link, params=dict(**kwargs))
        tr = None
        soup = BeautifulSoup(r.text, "html.parser")
        for br in soup.find_all("br"):
            br.replace_with("\n")
        a = soup.find("div", "lyric-cnt g-1")
        # Songs with translation
        if a is None:
            a = soup.find("div", "lyric-tra_l")
            tr = soup.find("div", "lyric-tra_r")
        b = "\n\n".join(i.get_text() for i in a.find_all("p"))
        query.update({"letra": b})
        if tr is not None:
            b = "\n\n".join(i.get_text() for i in a.find_all("p"))
            query.update({"traducao": b})
        else:
            query.update({"traducao": None})
        return query

    async def search(self, query):
        r = await self.http.get(
            "https://studiosolsolr-a.akamaihd.net/letras/app2/", params={"q": query}
        )
        a = r.json()
        x = []
        for n, i in enumerate(a["highlighting"]):
            if "mus" in i:
                g = a["response"]["docs"][n]
                g.update({"link": f"https://www.letras.mus.br/{g['dns']}/{g['url']}"})
                x.append(g)
        return x

    async def auto(self, query, limit=4):
        result = []
        for n, i in enumerate(await self.search(query)):
            a = await self.letra(i)
            result.append(a)
            if n == limit:
                break
        return result

    def parse(self, q):
        autor = q["art"]
        musica = q["txt"]
        letra = q["letra"]
        link = q["link"]
        traducao = q["traducao"]
        id = q["id"]
        return {
            "autor": autor,
            "musica": musica,
            "letra": letra,
            "link": link,
            "traducao": traducao,
            "id": id,
        }
