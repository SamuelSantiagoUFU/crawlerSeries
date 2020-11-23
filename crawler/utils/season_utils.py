import requests
from bs4 import BeautifulSoup

class Season:

    @staticmethod
    def episodes_wikipedia(link: str, season: int, offset: int = 0) -> dict:
        session = requests.Session()
        resp = session.get(link)
        bs = BeautifulSoup(resp.text, "lxml")

        position = season - 1 - offset
        table = bs.find_all("table", {"class": "wikitable plainrowheaders wikiepisodetable"})
        trs = table[position].tbody.find_all("tr")
        first_episode, last_episode = trs[1].th.text.strip(), trs[-1].th.text.strip()
        return {"first": int(first_episode), "last": int(last_episode)}

    @staticmethod
    def episode_exist(ep: str, episodes: dict) -> bool:
        try:
            return episodes['first'] <= int(ep) <= episodes['last']
        except ValueError as e:
            print(e)
            return False