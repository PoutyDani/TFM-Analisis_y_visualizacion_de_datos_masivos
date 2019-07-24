import unittest

import pandas as pd
import os

from movie_titles_extractor import MovieTitlesExtractor

class TestMovieTitlesExtractor(unittest.TestCase):

  def setUp(self):
    extractor = MovieTitlesExtractor()
    extractor.generate_csv()
    self.titles = extractor.read_csv()

  def tearDown(self):
    if os.path.exists('./files/movie_titles.csv'):
      os.remove('./files/movie_titles.csv')

    if os.path.exists('./files'):
      os.rmdir('./files')

  def test_generate_csv(self):
    self.assertTrue(os.path.exists('./files/movie_titles.csv'))

  def test_read_csv(self):
    self.assertIsInstance(self.titles, pd.DataFrame)

  def test_csv_structure(self):
    self.assertIsInstance(self.titles, pd.DataFrame)

    self.assertIn('Movie', self.titles.head())
    self.assertIn('Year', self.titles.head())

    self.assertFalse(self.titles.empty)

  def test_csv_content(self):
    self.assertEqual(len(self.titles.index), 115)

    movie = self.titles[self.titles['Movie'] == 'UN MONSTRUO VIENE A VERME']
    self.assertFalse(movie.empty)
    self.assertEqual(movie.Year.iloc[0], '2016')

if __name__ == '__main__':
  unittest.main()
