import os
from pathlib import Path



def main() -> None:
    data_dir = Path(__file__).parent
    os.environ["INIT_DATA_DIR"] = str(data_dir.absolute())

    import rss_music_page_initializer
    rss_music_page_initializer.run()


if __name__ == "__main__":
    main()
