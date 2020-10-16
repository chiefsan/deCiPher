# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CodeforcesProblemItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    p_id = scrapy.Field()
    p_index = scrapy.Field()
    p_title = scrapy.Field()
    p_time_limit = scrapy.Field()
    p_memory_limit = scrapy.Field()
    p_input_file = scrapy.Field()
    p_output_file = scrapy.Field()
    p_statement = scrapy.Field()
    p_input_specification = scrapy.Field()
    p_output_specification = scrapy.Field()
    p_sample_tests = scrapy.Field()
    p_note = scrapy.Field()

class CodeforcesSolutionItem(scrapy.Item):
    s_pid = scrapy.Field()
    s_index = scrapy.Field()
    s_source = scrapy.Field()
    s_sid = scrapy.Field()
    s_lang = scrapy.Field()
