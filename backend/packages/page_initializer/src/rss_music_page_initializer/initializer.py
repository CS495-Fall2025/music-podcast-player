import json
import os
from pathlib import Path

from rss_music_editable_pages import page_content

PAGE_DIRECTORY = Path(os.environ["INIT_DATA_DIR"]) / "pages"
VERSION_FILE = Path(os.environ["INIT_DATA_DIR"]) / "page_versions.json"


def _get_page_names() -> list[str]:
    names = []
    for path in PAGE_DIRECTORY.iterdir():
        if path.suffix == ".html":
            names.append(path.stem)

    return names


def _get_page_stored_versions(pages: list[str]) -> dict[str, int]:
    result = {}
    for page in pages:
        result[page] = page_content.get_page_version(page)

    return result


def _get_new_page_versions(pages: list[str]) -> dict[str, int]:
    with open(VERSION_FILE, "r") as file:
        version_data = json.load(file)

    result = {}
    for page in pages:
        result[page] = version_data[page]

    return result


def _get_outdated_pages(
    stored_versions: dict[str, int], new_versions: dict[str, int]
) -> list[str]:
    result = []
    for page in new_versions:
        stored_version = stored_versions[page]
        new_version = new_versions[page]

        if new_version > stored_version:
            result.append(page)

    return result


def _replace_outdated_pages(
    outdated_pages: list[str], new_versions: dict[str, int]
) -> None:
    for page in outdated_pages:
        page_path = PAGE_DIRECTORY / f"{page}.html"
        with open(page_path, "r") as file:
            content = file.read()

        page_content.put_page_content(page, content, new_versions[page])


def run() -> None:
    pages = _get_page_names()

    print(f"Discovered {len(pages)} pages.")

    stored_versions = _get_page_stored_versions(pages)
    new_versions = _get_new_page_versions(pages)
    outdated_pages = _get_outdated_pages(stored_versions, new_versions)

    print(f"Replacing {len(outdated_pages)} outdated pages:")
    print(outdated_pages)

    _replace_outdated_pages(outdated_pages, new_versions)
