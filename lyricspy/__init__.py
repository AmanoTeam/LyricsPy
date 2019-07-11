import requests
from bs4 import BeautifulSoup
import json
import duckpy
import re

ddg = duckpy.Client()
   
def letra(query):
    r = requests.get(query)
    soup = BeautifulSoup(r.text, "html.parser")
    infos = json.loads(soup.find_all('script', type="application/ld+json")[1].text)
    letra = soup.find('div', class_='cnt-letra p402_premium')
    letra = re.sub(r' ?<(/)?div.*?> ?', '', str(letra))
    ret = {
            "musica":infos['name'],
            "autor":infos['byArtist']['name'],
            "link":infos['url'],
            "thumb":infos['image'],
            "descricao":infos['description'],
            "letra":letra
            }
    if soup.find('a', class_='lm_lang lm_lang_pt'):
        r = requests.get(query+'/traducao.html')
        soup = BeautifulSoup(r.text, "html.parser")
        traducao = soup.find('div', class_='cnt-trad_r')
        traducao = re.sub(r' ?<(/)?div.*?> ?|<(/)?span>| ?<h3>.*?</h3> ?', '', str(traducao))
        ret["traducao"] = traducao
    return ret

def auto(query, limit=4):
    result = []
    n = 0
    for i in ddg.search('site:letras.mus.br ' + query):
        if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', i['url']) and not '/traducao.html' in i['url']:
            try:
                a = letra(i['url'])
                result.append(a)
                n += 1
            except:
                pass
        if n == limit:
            break
    return result