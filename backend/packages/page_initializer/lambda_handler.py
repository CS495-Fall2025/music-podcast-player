import os
from pathlib import Path


def handler(event, context):
    if event.get("RequestType") == "Delete":
        return

    data_dir = Path(__file__).parent
    os.environ["INIT_DATA_DIR"] = str(data_dir.absolute())

    import rss_music_page_initializer

    rss_music_page_initializer.run()
