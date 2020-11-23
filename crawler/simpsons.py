import os
import re
import shutil
from datetime import datetime
from glob import glob

import requests
from bs4 import BeautifulSoup

from models.episodes import Episode, Episodes
from crawler.utils.season_utils import Season


class Simpsons:
    def __init__(self, season: int, destination: str):
        self.season = season
        self.destination_folder = f"{os.getenv('BASE_DESTINATION')}{os.path.sep}{destination}"
        self.response = Episodes()
        self.session = requests.Session()

        if not os.path.exists(self.destination_folder):
            os.mkdir(self.destination_folder)

    def run(self):
        try:
            self._crawl()
        except Exception as e:
            raise e

        return self.response

    def _crawl(self):
        resp = self.session.get("https://animezeira.site/os-simpsons/")
        if self.season <= 15:
            episodes = Season.episodes_wikipedia(
                "https://pt.wikipedia.org/wiki/Lista_de_episódios_de_Os_Simpsons_(temporadas_1–15)", self.season)
        else:
            episodes = Season.episodes_wikipedia(
                "https://pt.wikipedia.org/wiki/Lista_de_episódios_de_Os_Simpsons_(temporadas_16_–_presente)", self.season, 15)
        # getting all episodes
        bs = BeautifulSoup(resp.text, "lxml")
        episodes_list = [li.a for li in bs.find("ul", {"class": "episodios"}).find_all("li")
                         if Season.episode_exist(li.a.span.text, episodes)]
        total_size = 0
        l = re.compile(r"^Os Simpsons - Epis[oó]dio\s*(\d*).*", re.I | re.M)
        for ep in episodes_list:
            number_ep = l.match(ep["title"]).group(1)
            if (episode := self._get_episode(ep["href"], int(number_ep))) is not None:
                total_size += episode.size
                self.response.episodes.append(episode)
        self.response.total_size = total_size

    def _get_episode(self, link: str, number: int) -> Episode:
        season = str(self.season).zfill(2)
        number = str(number).zfill(2)
        print("getting", number)

        resp = self.session.get(link)
        bs = BeautifulSoup(resp.text, "lxml")
        video = bs.find("div", {"id": "video-3"}).video
        source = re.match(r".*(https://.+)\s*$", video.source['src']).group(1)
        resp = self.session.get(source, stream=True)

        if resp.status_code == 200:
            path = f"{self.destination_folder}{os.path.sep}{self.season}"
            if glob(f"{path}{os.path.sep}*e{number}.mp4"):
                print(f"Episode {number} already exists")
                return None
            save_path = f"{path}{os.path.sep}s{season}e{number}.mp4"
            if not os.path.exists(path):
                os.mkdir(path)
            initial = datetime.now()
            with open(save_path, "wb") as fh:
                shutil.copyfileobj(resp.raw, fh)
            final = datetime.now()
            time = str(final - initial)
            print(f"Episode {number} downloaded in {time}")
            return Episode(
                name=f"s{season}e{number}.mp4",
                path=path,
                size=resp.headers.get('content-length', 0),
                download_time=time
            )


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    crawler = Simpsons(1, "Os Simpsons")
    crawler.run()
