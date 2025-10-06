from abc import ABC, abstractmethod

from requests import Response

from rss_music_backend.data import Feed


class SearchFeedsParser(ABC):
    @classmethod
    @abstractmethod
    def parse_search_feeds(cls, response: Response) -> list[Feed]:
        pass
