"""Script to scrap the codeforces problemset."""
from .fill_problem_table import make_problem_table

from ..framework.transaction_utils import fill_initial_team
from ..framework.schema import session_scope

from scrapy.crawler import CrawlerProcess
from ..codeforces_scraper.codeforces_scraper.spiders.problemset_spider import CodeforcesProblemSpider

process = CrawlerProcess()
process.crawl(CodeforcesProblemSpider, arg1=val1, arg2=val2)
process.start()

def main():

    with session_scope() as session:
        make_problem_table(session)

        print("DONE!")
