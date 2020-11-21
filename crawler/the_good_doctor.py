import os
import re
import shutil
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from glob import glob
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.webdriver import WebDriver

from crawler.utils.selenium_utils import wait_frame_switch
from models.episodes import Episode, Episodes


class TheGoodDoctor:
    def __init__(self, season: int, destination: str):
        self.season = season
        self.destination_folder = f"{os.getenv('BASE_DESTINATION')}{os.path.sep}{destination}"
        self.response = Episodes()

    @contextmanager
    def _get_driver(self, headless=False, implicity_wait=15) -> WebDriver:
        path = f"{self.destination_folder}{os.path.sep}{self.season}"
        os.makedirs(path, exist_ok=True)  # criando pasta file_dir

        driver = None
        display = None
        try:
            profile = FirefoxProfile()
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.dir", path)
            profile.set_preference("browser.download.useDownloadDir", True)
            profile.set_preference("browser.download.viewableInternally.enabledTypes", "")
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                                   "video/*")
            profile.set_preference("browser.helperApps.alwaysAsk.force", False)
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("browser.download.manager.useWindow", False)
            profile.set_preference("browser.download.manager.focusWhenStarting", False)
            profile.set_preference("browser.download.manager.showAlertOnComplete", False)
            # profile.set_preference("browser.download.manager.closeWhenDone", True)

            options = FirefoxOptions()
            options.headless = headless
            options.profile = profile

            driver = webdriver.Firefox(options=options)

            driver.implicitly_wait(implicity_wait)
            driver.set_window_size(1200, 800)

            yield driver
        except Exception as e:
            raise e
        finally:
            if driver is not None:
                driver.quit()
            if display is not None:
                display.stop()

    def run(self):
        try:
            self._crawl()
        except Exception as e:
            raise e

        return self.response

    def _get_episodes(self) -> list:
        url = "https://filmplay.biz/series/the-good-doctor/"
        resp = requests.get(url)
        bs = BeautifulSoup(resp.text, "lxml")
        season = bs.find("div", {"id": "seasons"})
        season = season.find_all("div", {"class": "se-c"})[self.season-1]
        episodes = season.find("ul", {"class": "episodios"})
        episodes = [li.a['href'] for li in episodes.find_all("li")]
        return episodes

    def _crawl(self):
        with self._get_driver(headless=False) as driver:
            time.sleep(0.5)
            episodes = self._get_episodes()
            for ep in episodes:
                try:
                    driver.get(ep)
                    # entrando no primeiro iframe

                    time.sleep(2)
                    # escolhendo player
                    wait_frame_switch(driver, By.XPATH, '//*[@id="dooplay_player_response"]/div/iframe')
                    wait_frame_switch(driver, By.XPATH, '/html/body/div/iframe')
                    time.sleep(2)
                    Wait(driver, 30).until(
                        EC.visibility_of_element_located((By.XPATH, '//*[@id="player"]/div[5]/div[1]/ul/li[2]'))
                    )
                    player = driver.find_element_by_xpath('//*[@id="player"]/div[5]/div[1]/ul/li[2]')
                    player.click()
                    driver.find_element_by_xpath('//*[@id="player"]/div[4]/div[2]').click()

                    wait_frame_switch(driver, By.XPATH, '//*[@id="SvplayerID"]/iframe')
                    wait_frame_switch(driver, By.XPATH, '//*[@id="iframe"]/center/iframe')
                    # clicando no play
                    print("procurando")

                    Wait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/*[name()="svg"]/*[name()="path" and @fill="currentColor"]'))
                    )
                    print("achou")
                    return
                    #driver.find_element_by_xpath('/html/body/div[2]/div/*[name()="svg"]/*[name()="path" and @fill="currentColor"]').click()
                    # voltando
                    print("Voltando")
                    driver.switch_to.default_content()
                    print("Voltou")
                    wait_frame_switch(driver, By.XPATH, '//*[@id="dooplay_player_response"]/div/iframe')
                    print("Frame 1")
                    wait_frame_switch(driver, By.XPATH, '/html/body/div/iframe')
                    print("Frame 2")
                    wait_frame_switch(driver, By.XPATH, '//*[@id="SvplayerID"]/iframe')
                    print("Frame 3")
                    wait_frame_switch(driver, By.XPATH, '//*[@id="iframe"]/center/iframe')
                    print("Frame 4")
                    # pegando src do video
                    Wait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="vstr"]/div[2]/div[3]/video'))
                    )
                    print("tunta")
                    link_video = driver.find_element_by_xpath('//*[@id="player"]/div[4]/div[2]').get_attribute("src")
                    driver.save_screenshot("screen.png")
                    print(link_video)
                except Exception as e:
                    raise e
                return


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    crawler = TheGoodDoctor(1, "The Good Doctor")
    crawler.run()
