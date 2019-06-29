from movie_titles_extractor import MovieTitlesExtractor
from subtitle_web_scraper import SubtitleWebScraper

titles_extractor = MovieTitlesExtractor()
titles_extractor.generate_csv()

SubtitleWebScraper().run(titles_extractor.read_csv())
