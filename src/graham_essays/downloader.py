from __future__ import annotations

import csv
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin

import html2text
import regex as re
import requests
from bs4 import BeautifulSoup
from dateparser import parse as parse_date
from htmldate import find_date


@dataclass(frozen=True)
class EssaySource:
    base_url: str = "https://paulgraham.com/"
    articles_url: str = "articles.html"


def _parse_main_page(source: EssaySource) -> list[dict[str, str]]:
    if not source.base_url.endswith("/"):
        raise ValueError(f"Base URL must end with a slash: {source.base_url}")

    response = requests.get(source.base_url + source.articles_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    td_cells = soup.select("table > tr > td > table > tr > td")
    chapter_links: list[dict[str, str]] = []

    for td in td_cells:
        img = td.find("img")
        if img and int(img.get("width", 0)) <= 15 and int(img.get("height", 0)) <= 15:
            a_tag = td.find("font").find("a") if td.find("font") else None
            if a_tag:
                chapter_links.append(
                    {"link": urljoin(source.base_url, a_tag["href"]), "title": a_tag.text}
                )

    return chapter_links


def _convert_to_pandoc_footnotes(text: bytes | str) -> bytes:
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    notes_section_pattern = r"\*\*Notes?\*\*.*?(?=\n\s*\*\*|\Z)"
    notes_match = re.search(notes_section_pattern, text, re.DOTALL | re.IGNORECASE)

    if not notes_match:
        return text.encode("utf-8")

    notes_content = notes_match.group(0)
    footnote_pattern = r"\[(\d+)\]\s*(.*?)(?=\s*\[\d+\]|\s*$)"
    footnotes = re.findall(footnote_pattern, notes_content, re.DOTALL)

    if not footnotes:
        return text.encode("utf-8")

    footnote_definitions: dict[str, str] = {}
    for note_num, note_content in footnotes:
        note_content = re.sub(r"\s+", " ", note_content.strip()).strip()
        if note_content:
            footnote_definitions[note_num] = note_content

    text = re.sub(notes_section_pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    for note_num in footnote_definitions.keys():
        text = re.sub(rf"\[{note_num}\]", f"[^{note_num}]", text)

    if footnote_definitions:
        footnote_defs = []
        for note_num in sorted(footnote_definitions.keys(), key=int):
            footnote_defs.append(f"[^{note_num}]: {footnote_definitions[note_num]}")
        text += "\n\n" + "\n\n".join(footnote_defs)

    return text.encode("utf-8")


def _yaml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _extract_description(parsed_text: str) -> str:
    for line in (line.strip() for line in parsed_text.splitlines()):
        if not line:
            continue
        if len(line) < 20:
            continue
        return line
    return ""


def fetch_essays(
    output_dir: Path,
    csv_path: Path | None,
    delay_seconds: float = 0.05,
    source: EssaySource | None = None,
    log: Callable[[str], None] | None = None,
) -> int:
    """Fetch essays into output_dir. Returns number of essays downloaded."""
    logger = log or (lambda message: print(message))
    source = source or EssaySource()

    output_dir.mkdir(parents=True, exist_ok=True)
    if csv_path is not None and csv_path.exists():
        csv_path.unlink()

    toc = list(reversed(_parse_main_page(source)))
    logger(f"Found {len(toc)} essays.")

    if csv_path is not None:
        with csv_path.open("a+", newline="\n") as csv_file:
            fieldnames = [
                "Article no.",
                "Title",
                "Description",
                "Date",
                "Author",
                "URL",
                "Filename",
            ]
            csvwriter = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csvwriter.writeheader()

    html_parser = html2text.HTML2Text()
    html_parser.ignore_images = True
    html_parser.ignore_tables = True
    html_parser.escape_all = True
    html_parser.reference_links = True
    html_parser.mark_code = True

    success_count = 0
    for index, entry in enumerate(toc, start=1):
        url = entry["link"]
        if "http://www.paulgraham.com/https://" in url:
            url = url.replace("http://www.paulgraham.com/https://", "https://")
        title = entry["title"]

        try:
            try:
                with urllib.request.urlopen(url, timeout=30) as website:
                    content = website.read().decode("utf-8")
            except UnicodeDecodeError:
                with urllib.request.urlopen(url, timeout=30) as website:
                    content = website.read().decode("latin-1")

            parsed = html_parser.handle(content)
            normalized_title = re.sub(r"[\W\s]+", "", "_".join(title.split(" ")).lower())

            pg_date_match = re.search(
                r"<font[^>]*>((?:January|February|March|April|May|June|July|August|"
                r"September|October|November|December)\s+\d{4})",
                content,
                re.IGNORECASE,
            )
            if pg_date_match:
                parsed_date = parse_date(pg_date_match.group(1))
                date_value = (
                    parsed_date.strftime("%Y-%m-%d") if parsed_date else find_date(content)
                )
            else:
                date_value = find_date(content)

            output_path = output_dir / f"{str(index).zfill(3)}_{normalized_title}.md"
            description = _extract_description(parsed)
            with output_path.open("wb+") as file:
                frontmatter = "\n".join(
                    [
                        "---",
                        f'title: "{_yaml_escape(title)}"',
                        f'description: "{_yaml_escape(description)}"',
                        f'date: "{date_value}"',
                        'author: "Paul Graham"',
                        "---",
                        "",
                    ]
                )
                file.write(frontmatter.encode())
                file.write(f"# {str(index).zfill(3)} {title}\n\n".encode())
                parsed = parsed.replace("[](index.html)  \n  \n", "")

                parsed_lines = [
                    (
                        paragraph.replace("\n", " ")
                        if re.match(
                            r"^[\p{Z}\s]*(?:[^\p{Z}\s][\p{Z}\s]*){5,100}$",
                            paragraph,
                        )
                        else "\n" + paragraph + "\n"
                    )
                    for paragraph in parsed.split("\n")
                ]

                encoded = " ".join(parsed_lines).encode()
                processed_content = _convert_to_pandoc_footnotes(encoded)
                file.write(processed_content)

            if csv_path is not None:
                with csv_path.open("a+", newline="\n") as csv_file:
                    csvwriter = csv.writer(
                        csv_file, quoting=csv.QUOTE_MINIMAL, delimiter=",", quotechar='"'
                    )
                    csvwriter.writerow(
                        [
                            str(index).zfill(3),
                            title,
                            description,
                            date_value,
                            "Paul Graham",
                            url,
                            output_path.name,
                        ]
                    )

            logger(f"✅ {str(index).zfill(3)} {title}")
            success_count += 1
        except Exception as exc:
            logger(f"❌ {str(index).zfill(3)} {title}, ({exc})")
        time.sleep(delay_seconds)

    return success_count
