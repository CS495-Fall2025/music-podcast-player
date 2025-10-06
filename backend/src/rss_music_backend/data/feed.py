class Feed:
    def __init__(self, url: str, art_url: str, title: str, artist: str, locked: bool):
        self.url = url
        self.art_url = url
        self.title = title
        self.artist = artist
        self.locked = locked
