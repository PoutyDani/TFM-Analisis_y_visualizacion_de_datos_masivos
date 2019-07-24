import unittest

import pymongo
import os
import zipfile

from mongo_db_controller import MongoDBController

class TestMongoDBController(unittest.TestCase):

  def setUp(self):
    self.controller = MongoDBController()
    self.collection = pymongo.MongoClient('mongodb://localhost:27017/')['mydatabase']['movies']

    file = open('./subtitles.srt', 'w+')
    file.writelines(
      [
        '1\n',
        '00:00:01,600 --> 00:00:4,200\n',
        'This is a subtitle in english'
      ]
    )
    file.close()

    os.makedirs('./files/temp')
    file = zipfile.ZipFile('./files/temp/subtitles.zip', 'w')
    file.write('./subtitles.srt')
    file.close()

    os.remove('./subtitles.srt')

    self.controller.save('https://www.imdb.com/title/tt4154796/')

    self.record = self.collection.find_one()

  def tearDown(self):
    self.collection.delete_many({})

    os.rmdir('./files/temp')
    os.rmdir('./files')

  def test_save_record(self):
    self.assertIsNotNone(self.record)

  def test_db_content(self):
    self.assertEqual('Vengadores: Endgame', self.record['title'])
    self.assertEqual('2019', self.record['year'])
    self.assertIn('Action', self.record['genre'])
    self.assertIn('ratings', self.record)
    self.assertIn('votes by score', self.record['ratings'])
    self.assertIn('votes by demographic', self.record['ratings'])
    self.assertIn('This is a subtitle in english', self.record['subtitles'])

if __name__ == '__main__':
  unittest.main()
