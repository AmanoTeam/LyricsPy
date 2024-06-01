import httpx
from bs4 import BeautifulSoup


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

    def parse(self, query):
        autor = query["art"]
        musica = query["txt"]
        letra = query["letra"]
        link = query["link"]
        traducao = query["traducao"]
        id = query["id"]
        return {
            "autor": autor,
            "musica": musica,
            "letra": letra,
            "link": link,
            "traducao": traducao,
            "id": id,
        }
