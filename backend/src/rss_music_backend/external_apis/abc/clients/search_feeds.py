from abc import ABC, abstractmethod

from requests import PreparedRequest


class SearchFeedsClient(ABC):
    @classmethod
    @abstractmethod
    def request_search_feeds(cls, query: str) -> PreparedRequest:
        pass
