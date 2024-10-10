import random
import re
from typing import Union
from uuid import uuid4

import httpx
from bs4 import BeautifulSoup

headers = {
    "Connection": "Keep-Alive",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.37",
}


class Musixmatch:
    """
    A class for interacting with the Musixmatch API.

    Provides methods for generating tokens, searching for songs, retrieving lyrics,
    and translating lyrics.

    Attributes:
        token (str|list): The API token(s) for authenticating requests to Musixmatch.
    """

    def __init__(self, usertoken: Union[str, list] = None):
        self.token = usertoken
        self.http = httpx.AsyncClient(http2=True, follow_redirects=True)

    async def gen_token(self) -> str:
        """
        enerate a token for authenticating requests to Musixmatch.

        Returns:
            str: The generated API token.
        """
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/token.get",
            params=dict(app_id="community-app-v1.0", guid=str(uuid4()), format="json"),
            headers=headers,
        )
        return a.json()["message"]["body"]["user_token"]

    async def search(self, q, limit) -> dict:
        """
        Search for songs on Musixmatch.

        Args:
            q (str): The search query.
            limit (int): The maximum number of results to return.

        Returns:
            dict: The search results.
        """
        if not self.token:
            utoken = await self.gen_token()
        else:
            utoken = (
                random.choice(self.token) if type(self.token) is list else self.token
            )
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/macro.search",
            params=dict(
                app_id="android-player-v1.0",
                usertoken=utoken,
                q=q,
                page=0,
                page_size=limit + 1,
                format="json",
            ),
            headers=headers,
        )
        return a.json()

    async def lyrics(self, id) -> dict:
        """
        Retrieve the lyrics for a song on Musixmatch.

        Args:
            id (str): The ID of the song.

        Returns:
            dict: The lyrics for the song.
        """
        if not self.token:
            utoken = await self.gen_token()
        else:
            utoken = (
                random.choice(self.token) if type(self.token) is list else self.token
            )
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/macro.subtitles.get",
            params=dict(
                app_id="android-player-v1.0",
                usertoken=utoken,
                track_id=id,
                format="json",
            ),
            headers=headers,
            follow_redirects=True,
        )

        return a.json()

    async def spotify_lyrics(self, artist, track) -> dict:
        """
        Retrieve the lyrics for a song on Musixmatch using Spotify data.

        Args:
            artist (str): The name of the artist.
            track (str): The name of the track.

        Returns:
            dict: The lyrics for the song.
        """
        if not self.token:
            utoken = await self.gen_token()
        else:
            utoken = (
                random.choice(self.token) if type(self.token) is list else self.token
            )
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/macro.subtitles.get",
            params=dict(
                app_id="android-player-v1.0",
                usertoken=utoken,
                q_artist=artist,
                q_track=track,
                format="json",
            ),
            headers=headers,
            follow_redirects=True,
        )

        return a.json()

    async def translation(self, id, lang, letra=None) -> Union[str, None]:
        """
        Translate the lyrics for a song on Musixmatch.

        Args:
            id (str): The ID of the song.
            lang (str): The language to translate the lyrics to.
            letra (str): The lyrics to translate.

        Returns:
            str|None: The translated lyrics.
        """
        if not self.token:
            utoken = await self.gen_token()
        else:
            utoken = (
                random.choice(self.token) if type(self.token) is list else self.token
            )
        a = await self.http.get(
            "https://apic.musixmatch.com/ws/1.1/crowd.track.translations.get",
            params=dict(
                app_id="android-player-v1.0",
                usertoken=utoken,
                selected_language=lang,
                track_id=id,
                part="user",
                format="json",
            ),
            headers=headers,
        )
        c = a.json()
        if c["message"]["body"]["translations_list"] and letra:
            tr = letra
            for i in c["message"]["body"]["translations_list"]:
                escape = re.escape(i["translation"]["snippet"])
                tr = re.sub(
                    f"^{escape}$", i["translation"]["description"], tr, flags=re.M
                )
        elif c["message"]["body"]["translations_list"]:
            tr = True
        else:
            tr = None

        return tr

    async def auto(self, q=None, lang="pt", limit=5, id=None) -> list:
        """
        Retrieve the lyrics for a song on Musixmatch.

        Args:
            q (str): The search query.
            lang (str): The language to translate the lyrics to.
            limit (int): The maximum number of results to return.
            id (str): The ID of the song.

        Returns:
            list: The lyrics for the song.
        """
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
            letra = b["message"]["body"]["macro_calls"]["track.lyrics.get"]["message"][
                "body"
            ]["lyrics"]["lyrics_body"]
            c = await self.translation(id, lang, letra)
            b["translate"] = c
            ret.append(b)
        return ret

    def parce(self, q):
        autor = q["message"]["body"]["macro_calls"]["matcher.track.get"]["message"][
            "body"
        ]["track"]["artist_name"]
        musica = q["message"]["body"]["macro_calls"]["matcher.track.get"]["message"][
            "body"
        ]["track"]["track_name"]
        letra = q["message"]["body"]["macro_calls"]["track.lyrics.get"]["message"][
            "body"
        ]["lyrics"]["lyrics_body"]
        link = q["message"]["body"]["macro_calls"]["track.lyrics.get"]["message"][
            "body"
        ]["lyrics"]["backlink_url"].split("?")[0]
        traducao = q["translate"] if "translate" in q else None
        id = q["message"]["body"]["macro_calls"]["matcher.track.get"]["message"][
            "body"
        ]["track"]["track_id"]
        ret = {
            "autor": autor,
            "musica": musica,
            "letra": letra,
            "link": link,
            "traducao": traducao,
            "id": id,
        }
        return ret


class Letras:
    """
    A class for interacting with the Letras API.

    Provides methods for searching songs and retrieving lyrics from Letras.
    """

    def __init__(self):
        self.http = httpx.AsyncClient(http2=True)

    async def letra(self, query, **kwargs) -> dict:
        """
        Retrieve the lyrics for a song on Letras.

        Args:
            query (dict): The search query.
            kwargs: Additional keyword arguments.

        Returns:
            dict: The lyrics for the song.
        """
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

    async def search(self, query) -> dict:
        """
        Search for songs on Letras.

        Args:
            query (str): The search query.

        Returns:
            dict: The search results.
        """
        r = await self.http.get(
            "https://studiosolsolr-a.akamaihd.net/letras/app2/", params=dict(q=query)
        )
        a = r.json()
        x = []
        n = 0
        for i in a["highlighting"]:
            if "mus" in i:
                g = a["response"]["docs"][n]
                g.update({"link": f"https://www.letras.mus.br/{g['dns']}/{g['url']}"})
                x.append(g)
            n += 1
        return x

    async def auto(self, query, limit=4) -> list:
        """
        Retrieve the lyrics for a song on Letras.

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return.

        Returns:
            list: The lyrics for the song.
        """
        result = []
        n = 0
        for i in await self.search(query):
            a = await self.letra(i)
            result.append(a)
            n += 1
            if n == limit:
                break
        return result

    def parce(self, q) -> dict:
        """
        Parse the search results from Letras.

        Args:
            q (dict): The search results.

        Returns:
            dict: The parsed search results.
        """
        autor = q["art"]
        musica = q["txt"]
        letra = q["letra"]
        link = q["link"]
        traducao = q["traducao"]
        id = q["id"]
        ret = {
            "autor": autor,
            "musica": musica,
            "letra": letra,
            "link": link,
            "traducao": traducao,
            "id": id,
        }
        return ret


class Genius:
    """
    Class for interacting with the Genius API.

    Provides methods for searching songs and retrieving lyrics from Genius.

    Attributes:
        token (str): The API token for authenticating requests to Genius.
    """

    def __init__(self, token=None):
        self.token = (
            token
            if token
            else "ZTejoT_ojOEasIkT9WrMBhBQOz6eYKK5QULCMECmOhvwqjRZ6WbpamFe3geHnvp3"
        )
        self.http = httpx.AsyncClient(http2=True)

    async def lyrics(self, id) -> dict:
        """
        Retrieve the lyrics for a song on Genius.

        Args:
            id (str): The ID of the song.

        Returns:
            dict: The lyrics for the song.
        """
        async with httpx.AsyncClient(http2=True, timeout=50) as client:
            response = await client.get(
                f"https://api.genius.com/songs/{id}",
                params={"text_format": "plain"},
                headers={"Authorization": f"Bearer {self.token}"},
            )

        return response.json()

    async def spotify_lyrics(self, artist, track) -> dict:
        """
        Retrieve the lyrics for a song on Genius using Spotify data.

        Args:
            artist (str): The name of the artist.
            track (str): The name of the track.

        Returns:
            dict: The lyrics for the song.
        """
        res = await self.search(f"{artist} {track}")

        if not res:
            return None

        return res[0]["result"]["id"]

        return None

    async def search(self, query) -> dict:
        """
        Search for songs on Genius.

        Args:
            query (str): The search query.

        Returns:
            dict: The search results.
        """
        async with httpx.AsyncClient(http2=True, follow_redirects=True) as client:
            response = await client.get(
                "https://api.genius.com/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {self.token}"},
            )

        return response.json()["response"]["hits"]

    async def auto(self, query, limit=4) -> list:
        """
        Retrieve the lyrics for a song on Genius.

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return.

        Returns:
            list: The lyrics for the song.
        """
        result = []
        hits = await self.search(query)
        for i in hits:
            lyrics = await self.lyrics(i["result"]["id"])
            result.append(lyrics)
            if len(result) == limit:
                break
        return result

    def parse(self, q) -> dict:
        """
        Parse the search results from Genius.

        Args:
            q (dict): The search results.

        Returns:
            dict: The parsed search results.
        """
        autor = q["response"]["song"]["primary_artist"]["name"]
        musica = q["response"]["song"]["title"]
        letra = q["response"]["song"]["lyrics"]["plain"]
        link = q["response"]["song"]["url"]
        traducao = None
        id = q["response"]["song"]["id"]
        ret = {
            "autor": autor,
            "musica": musica,
            "letra": letra,
            "link": link,
            "traducao": traducao,
            "id": id,
        }
        return ret
