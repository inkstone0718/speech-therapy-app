from icrawler.builtin import BingImageCrawler
import os

bing_crawler = BingImageCrawler(storage={'root_dir': 'test_bing'})
bing_crawler.crawl(keyword='蘋果 實物', max_num=1)
