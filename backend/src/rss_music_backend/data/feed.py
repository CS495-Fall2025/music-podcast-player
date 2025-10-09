from dataclasses import dataclass


@dataclass
class Feed:
    url: str
    art_url: str
    title: str
    artist: str
