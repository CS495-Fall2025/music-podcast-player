from dataclasses import dataclass, field

@dataclass
class Rss:
    url: str
    title: str
    description: str
    artist: str
    link: str
    image_url: str
    language: str
    pub_date: str
    last_build_date: str
    items: list[dict] = field(default_factory=list)

