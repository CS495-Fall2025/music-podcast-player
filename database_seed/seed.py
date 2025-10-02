from argparse import ArgumentParser, Namespace
import hashlib
import os
from pathlib import Path
import requests
import sys
import tarfile
from tempfile import NamedTemporaryFile
import time

import dotenv

USER_AGENT = "RSSMusicPlayerDBSeederUtility/1.0"

PODCAST_INDEX_DB_PATH = Path(__file__).parent / "podcastindex_feeds.db"
PODCAST_INDEX_DB_URL = "https://public.podcastindex.org/podcastindex_feeds.db.tgz"

REQUIRED_ENV_VARS = {
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "PODCAST_INDEX_KEY",
    "PODCAST_INDEX_SECRET"
}


def main() -> None:
    args = parse_arguments()

    if args.download or not is_index_db_present():
        download_index_db()
    else:
        print("Podcast Index database is already present, continuing.")
    
    dotenv.load_dotenv()

    check_env()


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

    headers = {"User-Agent": USER_AGENT} 
    with requests.get(PODCAST_INDEX_DB_URL, stream=True, headers=headers) as response:
        response.raise_for_status()
        with NamedTemporaryFile("wb") as file:
            mb_downloaded = 0
            for chunk in response.iter_content(chunk_size=1024**2):
                file.write(chunk)
                mb_downloaded += 1

                if mb_downloaded % 50 == 0:
                    print(f"Progress: {mb_downloaded} MiB")

            print("Download successful, starting extraction.")
            archieve = tarfile.open(file.name)
            archieve.extractall(path=PODCAST_INDEX_DB_PATH.parent, filter="data")
            print("Successfully extracted.")


def check_env() -> None:
    if not REQUIRED_ENV_VARS.issubset(set(os.environ.keys())):
        print("Environment is missing required variables, make sure .env is present")
        sys.exit(1)


def make_podcast_index_auth_headers() -> dict[str, str]:
    seconds = str(int(time.time()))
    key = os.getenv("PODCAST_INDEX_KEY")
    secret = os.getenv("PODCAST_INDEX_SECRET")
    hash = hashlib.sha1(f"{key}{secret}{seconds}".encode("utf-8")).hexdigest()

    return {
        "User-Agent": USER_AGENT,
        "X-Auth-Key": key,
        "X-Auth-Date": seconds,
        "Authorization": hash,
    }


if __name__ == "__main__":
    main()
