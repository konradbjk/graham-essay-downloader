# Graham Essays Collection

This is the new maintained version under `konradbjk/graham-essay-downloader`.
It is based on the original `ofou/graham-essays` project and keeps the same spirit,
while modernizing the tooling and CLI.

![https://startupquote.com/post/3890222281](https://64.media.tumblr.com/tumblr_li4p22jETB1qz6pqio1_500.png)

> "If you are not embarrassed by the first version of your product, you've launched too late".

---

**Check out the [releases page] for the latest build, updated daily.**

Download the _complete collection_ of +200 essays from [Paul Graham] website and export them in [EPUB], and Markdown for easy [AFK] reading. It turned out to be a whooping +500k words. I used the RSS originally made by [Aaron Swartz] [shared] by PG himself, `feedparser`, `html2text`, `htmldate` and `Unidecode` libraries for data cleaning and acquisition. 

## Dependencies for MacOS

On macOS you need [brew] in order to install the external tools used by the CLI, e.g.:

```bash
brew install uv pandoc calibre
```

## Usage

Install Python dependencies with `uv`:

```bash
uv venv .venv
uv sync
```

Run the CLI:

```bash
uv run graham-essays fetch
uv run graham-essays merge
uv run graham-essays epub
uv run graham-essays pdf
uv run graham-essays wordcount
```

Or run everything at once:

```bash
uv run graham-essays all
```

See all commands:

```bash
uv run graham-essays --help
```

### Metadata Exports

Each markdown file includes YAML frontmatter with `title`, `description`, `date`, and `author`.
The `fetch` command also writes `essays.csv` with columns:

- Article no.
- Title
- Description
- Date
- Author
- URL
- Filename

You can disable the CSV or choose a different path:

```bash
uv run graham-essays fetch --no-csv
uv run graham-essays fetch --csv-path data/essays.csv
```

### External Tools

These commands rely on external tools:

- `pandoc` (for `merge` and `epub`)
- `calibre` (for `pdf`, which uses `ebook-convert`)

### Current Essays

Here's a [list] of the current essays included, and an [EPUB].

---

_If you have any ideas, suggestions, curses or feedback in order to improve the code, please don't hesitate in opening an issue or PR. They'll be very welcomed!_

[afk]: https://www.grammarly.com/blog/afk-meaning/
[paul graham]: http://www.paulgraham.com/articles.html
[aaron swartz]: https://en.wikipedia.org/wiki/Aaron_Swartz
[brew]: https://docs.brew.sh/Installation
[pandoc]: https://pandoc.org/installing.html
[calibre]: https://calibre-ebook.com/
[EPUB]: https://github.com/ofou/graham-essays/releases/download/latest/graham.epub
[releases page]: https://github.com/ofou/graham-essays/releases
[shared]: http://www.paulgraham.com/rss.html
[list]: https://github.com/ofou/graham-essays/releases/download/latest/essays.csv
