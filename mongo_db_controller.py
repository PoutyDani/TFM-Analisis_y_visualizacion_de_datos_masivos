import os
import zipfile
import pysrt
import pymongo
import re
from requests import get
from lxml import html

class MongoDBController:
  __MONGO_DB_HOST = 'mongodb://localhost:27017/'
  __DB_NAME = 'mydatabase'
  __COLLECTION_NAME = 'movies'
  __TEMP_FILE_DIR = f'{os.getcwd()}\\files\\temp'
  __XPATH = {
    'title': '//*[@id="main"]/section/div/div[1]/div[1]/h3/a/text()',
    'year': '//*[@id="titleYear"]/a/text()',
    'genre': '//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/div/a[position()<last()]/text()',
    'votes_by_score': ['//table[@cellpadding="0"]/tr[' ,']/td[3]/div/div/text()'],
    'votes_by_demographic': {
      'base': ['//*[@id="main"]/section/div/table[2]/tr[', ']/td['],
      'mean': ']/div[1]/text()',
      'amount': ']/div[2]/a/text()'
    }
  }
  __RATINGS_PATH = 'ratings?ref_=tturv_ql_4'
  __AGES = ['All ages', '<18', '18-29', '30-44', '45+']

  def __init__(self):
    self.collection = pymongo.MongoClient(self.__MONGO_DB_HOST)[self.__DB_NAME][self.__COLLECTION_NAME]

  # Public methods

  def save(self, href):
    html = self.__extract_html_content(href)

    movie = {
      'title': html['ratings'].xpath(self.__XPATH['title'])[0],
      'year': html['movie'].xpath(self.__XPATH['year'])[0],
      'genre': html['movie'].xpath(self.__XPATH['genre']),
      'ratings': {
        'votes by score': self.__extract_votes_by_score(html),
        'votes by demographic': self.__extract_votes_by_demographic(html)
      },
      'subtitles': self.__extract_subtitles()
    }

    self.collection.insert_one(movie)

    self.__clean_directory()

  # Private methods

  def __extract_html_content(self, href):
    return {
      'movie': html.fromstring(get(href).content),
      'ratings': html.fromstring(get(f'{href}{self.__RATINGS_PATH}').content)
    }

  def __extract_votes_by_score(self, html):
    votes = {}
    for i, j in zip(range(1, 11), range(11, 1, -1)):
      votes.update({ str(i): html['ratings'].xpath(f'{self.__XPATH["votes_by_score"][0]}{str(j)}{self.__XPATH["votes_by_score"][1]}')[0] })

    return votes

  def __extract_votes_by_demographic(self, html):
    votes = { 'All': {}, 'Males': {}, 'Females': {} }
    for gender in votes:
      for age in self.__AGES:
        base_path = f'{self.__XPATH["votes_by_demographic"]["base"][0]}{str(list(votes).index(gender) + 2)}{self.__XPATH["votes_by_demographic"]["base"][1]}{str(self.__AGES.index(age) + 2)}'
        mean = html['ratings'].xpath(f'{base_path}{self.__XPATH["votes_by_demographic"]["mean"]}')[0]
        if mean != '-':
          amount = html['ratings'].xpath(f'{base_path}{self.__XPATH["votes_by_demographic"]["amount"]}')[0].strip()
        else:
          mean = '0'
          amount = '0'
        votes[gender].update({ age: { 'mean': mean, 'amount': amount } })

    return votes

  def __extract_subtitles(self):
    for f_name in os.listdir(self.__TEMP_FILE_DIR):
      zip_ref = zipfile.ZipFile(f'{self.__TEMP_FILE_DIR}\\{f_name}', 'r')
    zip_ref.extractall(self.__TEMP_FILE_DIR)
    zip_ref.close()

    for srt_file in os.listdir(self.__TEMP_FILE_DIR):
      if (not srt_file.endswith('.nfo')) and (not srt_file.endswith('.zip')):
        try:
          subs = pysrt.open(f'{self.__TEMP_FILE_DIR}\\{srt_file}')
        except:
          subs = pysrt.open(f'{self.__TEMP_FILE_DIR}\\{srt_file}', encoding = 'ISO-8859-1')

    return list(map(lambda x: re.sub(r'\<[^>]*\>', '', x), subs.text.split('\n')))

  def __clean_directory(self):
    for file in os.listdir(self.__TEMP_FILE_DIR):
      os.remove(f'{self.__TEMP_FILE_DIR}\\{file}')
