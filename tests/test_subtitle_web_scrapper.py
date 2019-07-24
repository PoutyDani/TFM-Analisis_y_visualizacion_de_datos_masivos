import unittest

import pandas as pd
import pymongo
import os

from subtitle_web_scraper import SubtitleWebScraper

class TestSubtitleWebScraper(unittest.TestCase):

  def setUp(self):
    self.scraper = SubtitleWebScraper()
    self.title = pd.DataFrame(columns = ['Movie', 'Year'])
    self.collection = pymongo.MongoClient('mongodb://localhost:27017/')['mydatabase']['movies']

  def tearDown(self):
    self.collection.delete_many({})

    os.rmdir('./files/temp')
    os.rmdir('./files')

  def test_run(self):
    self.__execute({ 'Movie': '8 APELLIDOS VASCOS', 'Year': '2014' })

    self.assertEqual('Ocho apellidos vascos', self.record['title'])
    self.assertEqual('2014', self.record['year'])
    self.assertIn('Comedy', self.record['genre'])
    self.assertIn('Viva el vino, la manzanilla', self.record['subtitles'])

  def test_movie_alone(self):
    self.__execute({ 'Movie': 'SUPERLÓPEZ', 'Year': '2018' })

    self.assertEqual('Superlópez', self.record['title'])
    self.assertEqual('2018', self.record['year'])
    self.assertIn('Comedy', self.record['genre'])
    self.assertIn('¡Es mi hijo!', self.record['subtitles'])

  def test_movie_search_with_country(self):
    self.__execute({ 'Movie': 'AGORA', 'Year': '2009' })

    self.assertEqual('Ágora', self.record['title'])
    self.assertEqual('2009', self.record['year'])
    self.assertIn('Drama', self.record['genre'])
    self.assertIn('Eres libre.', self.record['subtitles'])


  def __execute(self, data):
    self.title = self.title.append(data, ignore_index = True)
    self.scraper.run(self.title)
    self.record = self.collection.find_one()

if __name__ == '__main__':
  unittest.main()
