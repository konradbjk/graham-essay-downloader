from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import typer

from graham_essays.downloader import EssaySource, fetch_essays


app = typer.Typer(
    add_completion=False,
    help="Download and export the Paul Graham essays collection.",
)


def _resolve_root(root: Path | None) -> Path:
    return root.resolve() if root else Path.cwd()


def _require_tool(name: str) -> str:
    tool_path = shutil.which(name)
    if not tool_path:
        typer.secho(
            f"Missing required tool: {name}. Install it and ensure it's on PATH.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    return tool_path


@app.command()
def clean(
    root: Path | None = typer.Option(
        None,
        "--root",
        help="Project root where outputs are stored.",
    )
) -> None:
    """Remove generated files."""
    base = _resolve_root(root)
    paths = [
        base / "essays",
        base / "graham.epub",
        base / "graham.pdf",
        base / "graham.md",
        base / "essays.csv",
    ]
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    typer.echo("Cleaned generated files.")


@app.command()
def fetch(
    root: Path | None = typer.Option(None, "--root", help="Project root."),
    delay: float = typer.Option(0.05, "--delay", help="Delay between requests."),
    csv: bool = typer.Option(True, "--csv/--no-csv", help="Write essays.csv metadata."),
    csv_path: Path | None = typer.Option(
        None, "--csv-path", help="Optional path for the CSV export."
    ),
) -> None:
    """Download the essays as markdown files."""
    base = _resolve_root(root)
    output_dir = base / "essays"
    resolved_csv = csv_path or (base / "essays.csv")
    fetch_essays(
        output_dir=output_dir,
        csv_path=resolved_csv if csv else None,
        delay_seconds=delay,
    )


@app.command()
def merge(
    root: Path | None = typer.Option(None, "--root", help="Project root."),
) -> None:
    """Merge all essays into a single markdown file using pandoc."""
    base = _resolve_root(root)
    essays_dir = base / "essays"
    if not essays_dir.exists():
        typer.secho("Essays directory not found. Run fetch first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    _require_tool("pandoc")
    output_path = base / "graham.md"
    subprocess.run(
        ["pandoc", *map(str, sorted(essays_dir.glob("*.md"))), "-o", str(output_path)],
        check=True,
    )
    typer.echo(f"Wrote {output_path.name}.")


@app.command()
def epub(
    root: Path | None = typer.Option(None, "--root", help="Project root."),
) -> None:
    """Create an EPUB using pandoc."""
    base = _resolve_root(root)
    essays_dir = base / "essays"
    if not essays_dir.exists():
        typer.secho("Essays directory not found. Run fetch first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    _require_tool("pandoc")
    output_path = base / "graham.epub"
    metadata_path = base / "metadata.yaml"
    cover_path = base / "cover.png"
    subprocess.run(
        [
            "pandoc",
            *map(str, sorted(essays_dir.glob("*.md"))),
            "-o",
            str(output_path),
            "-t",
            "epub3",
            "-f",
            "markdown",
            "--metadata-file",
            str(metadata_path),
            "--toc",
            "--toc-depth=1",
            "--epub-cover-image",
            str(cover_path),
        ],
        check=True,
    )
    typer.echo(f"Wrote {output_path.name}.")


@app.command()
def pdf(
    root: Path | None = typer.Option(None, "--root", help="Project root."),
) -> None:
    """Create a PDF via calibre's ebook-convert."""
    base = _resolve_root(root)
    epub_path = base / "graham.epub"
    if not epub_path.exists():
        typer.secho("EPUB not found. Run epub first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    _require_tool("ebook-convert")
    output_path = base / "graham.pdf"
    subprocess.run(
        ["ebook-convert", str(epub_path), str(output_path)],
        check=True,
    )
    typer.echo(f"Wrote {output_path.name}.")


@app.command()
def wordcount(
    root: Path | None = typer.Option(None, "--root", help="Project root."),
) -> None:
    """Count total words and articles."""
    base = _resolve_root(root)
    essays_dir = base / "essays"
    if not essays_dir.exists():
        typer.secho("Essays directory not found. Run fetch first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    word_total = 0
    files = sorted(essays_dir.glob("*.md"))
    for path in files:
        word_total += len(path.read_text(encoding="utf-8", errors="ignore").split())

    typer.echo(f"Total words: {word_total}")
    typer.echo(f"Total articles: {len(files)}")


@app.command()
def all(
    root: Path | None = typer.Option(None, "--root", help="Project root."),
    delay: float = typer.Option(0.05, "--delay", help="Delay between requests."),
    csv: bool = typer.Option(True, "--csv/--no-csv", help="Write essays.csv metadata."),
    csv_path: Path | None = typer.Option(
        None, "--csv-path", help="Optional path for the CSV export."
    ),
) -> None:
    """Run clean, fetch, merge, epub, and wordcount."""
    base = _resolve_root(root)
    clean(base)
    fetch(base, delay=delay, csv=csv, csv_path=csv_path)
    merge(base)
    epub(base)
    wordcount(base)


def _main() -> None:
    app()


if __name__ == "__main__":
    _main()
