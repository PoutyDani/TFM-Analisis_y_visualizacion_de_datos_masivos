import pandas as pd
import os
from requests import get
from bs4 import BeautifulSoup

class MovieTitlesExtractor:
  __URL = 'https://www.taquillaespana.es/estadisticas/peliculas-espanolas-mas-taquilleras-de-todos-los-tiempos/'
  __DIR = './files'
  __FILENAME = 'movie_titles.csv'
  __COLUMNS = ['Movie', 'Year']

  # Public methods

  def generate_csv(self):
    self.__html_content()
    self.__extract_data()
    self.__create_data_frame()
    self.__write_csv()

  def read_csv(self):
    return pd.read_csv(f'{self.__DIR}/{self.__FILENAME}', header = 0, dtype = str)

  # Private methods

  def __html_content(self):
    self.html = BeautifulSoup(get(self.__URL).content, 'html.parser')

  def __extract_data(self):
    data = {
      'movies': self.html.findAll('td', { 'class': 'column-2' }),
      'years': self.html.findAll('td', { 'class': 'column-3' })
    }
    self.data = list(map(list, zip(data['movies'], data['years'])))

  def __create_data_frame(self):
    self.movies = pd.DataFrame(columns = self.__COLUMNS)
    for record in self.data:
      self.movies = self.movies.append(
        { self.__COLUMNS[0]: record[0].text, self.__COLUMNS[1]: record[1].text },
        ignore_index = True
      )

  def __write_csv(self):
    if not os.path.exists(self.__DIR):
      os.makedirs(self.__DIR)

    self.movies.to_csv(f'{self.__DIR}/{self.__FILENAME}', index = False)
