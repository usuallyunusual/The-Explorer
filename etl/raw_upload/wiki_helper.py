import bz2
import glob
import logging
import xml.etree.ElementTree as et
from datetime import datetime

from etl.counters import Counters


class WikiHelper:
    __PAGE_TAG = "<page>"
    __CLOSE_PAGE_TAG = "</page>"
    __ARTICLE_LIST = list()
    __NO_NAMESPACE_COUNTER = "Pages with no namespace element"
    __NAMESPACE_NOT_MAIN_COUNTER = "Pages with namespace not in main"
    __PAGES_WITH_NO_TEXT = "Pages with no text"
    __PAGES_WITH_NO_TITLE = "Pages with no title"
    __TOTAL_FILES_PROCESSED = "Total files processed"
    __TOTAL_ARTICLES_PROCESSED = "Total number of articles processed"
    __TOTAL_VALID_ARTICLES_PROCESSED = "Total number of valid articles processed"

    def __init__(self, source, destination, io_helper, chunk_size):
        self.source = source[:-1] if source[-1] == "/" else source
        self.timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.destination = destination[:-1] if destination[-1] == "/" else destination
        self.timestamp_destination = f"{self.destination}/{self.timestamp}"
        self.io_helper = io_helper
        self.chunk_size = chunk_size
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def is_page_start_tag(self, line):
        if line.find(WikiHelper.__PAGE_TAG) > -1:
            return True
        return False

    def is_page_close_tag(self, line):
        if line.find(WikiHelper.__CLOSE_PAGE_TAG) > -1:
            return True
        return False

    def get_article_from_xml(self, xml_string):
        root = et.fromstring(xml_string)
        namespace = root.find("./ns")
        if namespace is None:
            self.LOGGER.debug("No namespace")
            Counters.increment(self.__NO_NAMESPACE_COUNTER)
            return
        # All mainspace wiki articles are namespace 0
        if namespace.text != "0":
            self.LOGGER.debug("Page not in mainspace.")
            Counters.increment(self.__NAMESPACE_NOT_MAIN_COUNTER)
            return
        text = root.find("./revision/text")
        if text is None:
            self.LOGGER.debug("No text")
            Counters.increment(self.__PAGES_WITH_NO_TEXT)
            return
        title = root.find(".title")
        if title is None:
            self.LOGGER.debug("No title")
            Counters.increment(self.__PAGES_WITH_NO_TITLE)
            return
        return {
            "text": text.text,
            "title": title.text
        }

    def extract_to_destination(self):
        zip_raw_files = glob.glob(self.source + "*.bz2")
        self.LOGGER.info(f"Processing {len(zip_raw_files)} zip files at source {self.source}")
        for raw_file in zip_raw_files:
            self.LOGGER.info(f"Processing file: {raw_file}")
            self.extract(raw_file)
            Counters.increment(self.__TOTAL_FILES_PROCESSED)
        self.io_helper.cleanup_serializer()

    def extract(self, raw_file):
        zip_file = bz2.open(raw_file, 'rb')
        is_article = False
        article = ""
        for idx, line in enumerate(zip_file):
            line = line.decode()
            if self.is_page_start_tag(line):
                is_article = True
            if self.is_page_close_tag(line):
                is_article = False
                article += line
                Counters.increment(self.__TOTAL_ARTICLES_PROCESSED)
                article = self.get_article_from_xml(article)
                if article:
                    Counters.increment(self.__TOTAL_VALID_ARTICLES_PROCESSED)
                    self.__ARTICLE_LIST.append(article)
                article = ""
            if is_article:
                article += line
            if len(self.__ARTICLE_LIST) != 0 and len(self.__ARTICLE_LIST) % self.chunk_size == 0:
                self.__write_using_io()
        self.__write_using_io()
        zip_file.close()
        return True

    def __write_using_io(self):
        self.LOGGER.info(f"Writing {len(self.__ARTICLE_LIST)} records to output")
        self.io_helper.write(self.__ARTICLE_LIST, self.timestamp_destination)
        self.__ARTICLE_LIST = list()
