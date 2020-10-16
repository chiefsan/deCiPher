"""Script to scrap the codeforces problemset."""
from .fill_problem_table import make_problem_table

from ..framework.schema import session_scope

from scrapy.crawler import CrawlerProcess

import os
import sys
import importlib

from ..codeforces_scraper.codeforces_scraper.spiders.problemset_spider import CodeforcesProblemSpider

def main():
    # process = CrawlerProcess()
    # process.crawl(CodeforcesProblemSpider)
    # process.start()

    scraper_dirname = os.path.join(
            os.path.dirname(importlib.util.find_spec('decipher').origin),
            "codeforces_scraper",
        )
    os.chdir(scraper_dirname)
    print(os.getcwd())
    if not os.path.exists('../data'):
        os.makedirs('../data')
    os.system("scrapy crawl problemset_spider -o ../data/problemset.json")

    print("DONE!")
