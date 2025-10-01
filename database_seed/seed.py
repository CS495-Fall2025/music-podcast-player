from argparse import ArgumentParser, Namespace
from pathlib import Path
import tarfile
from tempfile import NamedTemporaryFile
from urllib import request


PODCAST_INDEX_DB_PATH = Path(__file__).parent / "podcastindex_feeds.db"
PODCAST_INDEX_DB_URL = "https://public.podcastindex.org/podcastindex_feeds.db.tgz"


def main() -> None:
    args = parse_arguments()

    if args.download or not is_index_db_present():
        download_index_db()
    else:
        print("Podcast Index database is already present, continuing.")


def parse_arguments() -> Namespace:
    parser = ArgumentParser(
        prog="RSS Music Player Seed Utility",
        description=(
                "Seeds the development Postgres database for the RSS Music Player "
                "webapp."
        )
    )

    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help=(
            "Redownloads the PodcastIndex database"
        )
    )

    return parser.parse_args()


def is_index_db_present() -> bool:
    return PODCAST_INDEX_DB_PATH.is_file()


def download_index_db() -> None:
    print("Initiating download of Podcast Index database, this may take a few minutes.")
    with NamedTemporaryFile(delete_on_close=False) as file:
        file.close()

        request.urlretrieve(PODCAST_INDEX_DB_URL, file.name)
        print("Download successful, starting extraction.")
        archieve = tarfile.open(file.name)
        archieve.extractall(path=PODCAST_INDEX_DB_PATH.parent, filter="data")
        print("Successfully extracted.")


if __name__ == "__main__":
    main()
