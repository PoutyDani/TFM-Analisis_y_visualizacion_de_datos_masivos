import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from unidecode import unidecode
from mongo_db_controller import MongoDBController

class SubtitleWebScraper:
  __TEMP_FILE_DIR = f'{os.getcwd()}\\files\\temp'
  __CHROME_EXTENSION_PATH = fr'{os.getcwd()}\\drivers\\openSubtitles_1.0.14_0.crx'
  __DRIVER_PATH = './drivers/chromedriver.exe'
  __DRIVER_DELAY = 3 # seconds
  __REQUESTS_WITH_DELAY = 2
  __URL = {
    'search': 'https://www.opensubtitles.org/en/search2/sublanguageid-spa/',
    'country': 'moviecountry-spain/',
    'year': 'movieyearsign-1/movieyear-',
    'name': '/moviename-'
  }
  __XPATH = {
    'download': '//table[@id="search_results"]/tbody//tr/td[2]/a[@title="Spanish"]/parent::td/parent::tr/td[5]/a',
    'imdb': '//table[@id="search_results"]/tbody//tr/td[2]/a[@title="Spanish"]/parent::td/parent::tr/td[8]/a',
    'alone_download': '//a[@download="download"]',
    'alone_imdb': '//a[starts-with(@title, "About movie")]'
  }

  def __init__(self):
    self.__generate_options()
    self.__generate_driver()
    self.mongodb = MongoDBController()

  # Public methods

  def run(self, movies):
    self.__encode_movie_titles(movies)

    for counter in range(len(movies)):
      try:
        try:

          # Normal search
          try:
            self.driver.get(self.__generate_url(movies.loc[counter, :]))

            self.__download_subtitles(self.__XPATH['download'], counter)
            imdb_link = self.__extract_imdb_link(self.__XPATH['imdb'])

          except NoSuchElementException:
            self.__download_subtitles(self.__XPATH['alone_download'])
            imdb_link = self.__extract_imdb_link(self.__XPATH['alone_imdb'])

        except NoSuchElementException:

          # Search with country
          try:
            self.driver.get(self.__generate_url(movies.loc[counter, :], with_country = True))

            self.__download_subtitles(self.__XPATH['download'])
            imdb_link = self.__extract_imdb_link(self.__XPATH['imdb'])

          except NoSuchElementException:
            self.__download_subtitles(self.__XPATH['alone_download'])
            imdb_link = self.__extract_imdb_link(self.__XPATH['alone_imdb'])

        self.mongodb.save(imdb_link)

      except NoSuchElementException:
        print(f'Movie not found: {movies["Movie"][counter]}')

    time.sleep(self.__DRIVER_DELAY)
    self.driver.quit()

  # Private methods

  def __generate_options(self):
    self.chrome_options = Options()
    self.chrome_options.add_experimental_option('prefs', { 'download.default_directory': self.__TEMP_FILE_DIR })
    self.chrome_options.add_extension(self.__CHROME_EXTENSION_PATH)

  def __generate_driver(self):
    self.driver = webdriver.Chrome(executable_path = self.__DRIVER_PATH, options = self.chrome_options)
    self.driver.implicitly_wait(self.__DRIVER_DELAY)

  def __encode_movie_titles(self, movies):
    movies['Movie'] = movies['Movie'].str.replace(' ', '+').apply(unidecode)

  def __generate_url(self, movie, with_country = False):
    return f'{self.__URL["search"]}{self.__URL["country"] if with_country else ""}{self.__URL["year"]}{movie["Year"]}{self.__URL["name"]}{movie["Movie"]}'

  def __download_subtitles(self, xpath, counter = __REQUESTS_WITH_DELAY):
    button = self.driver.find_element_by_xpath(xpath)
    if counter < self.__REQUESTS_WITH_DELAY:
      time.sleep(self.__DRIVER_DELAY)
    button.click()

  def __extract_imdb_link(self, xpath):
    return self.driver.find_element_by_xpath(xpath).get_attribute('href')
