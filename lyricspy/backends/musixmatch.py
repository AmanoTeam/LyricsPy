from __future__ import annotations

import random
import re

import httpx

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.37"
}


class Musixmatch:
    def __init__(self, usertoken: str | list):
        self.token = usertoken
        self.http = httpx.AsyncClient(http2=True)

    async def search(self, query: str, limit: int):
        utoken = random.choice(self.token) if isinstance(self.token, list) else self.token

        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/macro.search",
            params={
                "app_id": "android-player-v1.0",
                "usertoken": utoken,
                "q": query,
                "page": 0,
                "page_size": limit + 1,
                "format": "json",
            },
            headers=headers,
        )
        return a.json()

    async def lyrics(self, id):
        utoken = random.choice(self.token) if isinstance(self.token, list) else self.token

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

    async def spotify_lyrics(self, artist: str, track: str):
        utoken = random.choice(self.token) if isinstance(self.token, list) else self.token
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
        utoken = random.choice(self.token) if isinstance(self.token, list) else self.token
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
                tr = re.sub(f"^{escape}$", i["translation"]["description"], tr, flags=re.MULTILINE)
        elif c["message"]["body"]["translations_list"]:
            tr = True
        else:
            tr = None

        return tr

    async def auto(self, query=None, lang="pt", limit=5, id=None):
        print("auto", query, lang, limit, id)
        if query:
            a = await self.search(query, limit)
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

    @staticmethod
    def parse(query):
        macro_calls = query["message"]["body"]["macro_calls"]
        track_data = macro_calls["matcher.track.get"]["message"]["body"]["track"]
        lyrics_data = macro_calls["track.lyrics.get"]["message"]["body"]["lyrics"]

        return {
            "autor": track_data["artist_name"],
            "musica": track_data["track_name"],
            "letra": lyrics_data["lyrics_body"],
            "link": lyrics_data["backlink_url"].split("?")[0],
            "traducao": query.get("translate", None),
            "id": track_data["track_id"],
        }
