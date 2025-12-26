#!/usr/bin/env python3
"""
HarmonyScan Downloader
A beautiful CLI manga downloader for harmony-scan.fr

Usage:
    python main.py              - Run the interactive CLI
    python main.py download URL - Quick download from URL
    python main.py --help       - Show help
"""

import asyncio
import sys
import typer
from typing import Optional
from pathlib import Path

from rich.console import Console

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.app import HarmonyScanApp, run_app
from src.cli.display import print_banner, print_info, print_error, print_success, console, COLORS, create_download_progress
from src.scraper.manga import MangaScraper
from src.downloader.manager import DownloadManager
from src.converters.pdf import convert_to_pdf
from src.converters.cbz import convert_to_cbz
from config import config


app = typer.Typer(
    name="harmonyscan",
    help="🎨 Beautiful manga downloader for harmony-scan.fr",
    add_completion=False,
    rich_markup_mode="rich"
)


@app.command("interactive", help="Run the interactive CLI interface")
def interactive():
    """Run the interactive menu-driven interface."""
    run_app()


@app.command("download", help="Download a manga directly by URL")
def download(
    url: str = typer.Argument(..., help="Manga page URL from harmony-scan.fr"),
    chapters: str = typer.Option("all", "-c", "--chapters", help="Chapters to download: 'all', single number, or range (e.g., '1-10')"),
    format: str = typer.Option("images", "-f", "--format", help="Output format: images, pdf, cbz"),
    keep_images: bool = typer.Option(True, "-k", "--keep-images", help="Keep images after conversion"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output directory")
):
    """Download manga chapters directly from command line."""
    # Run the async download
    asyncio.run(_download_async(url, chapters, format, keep_images, output))


async def _download_async(url: str, chapters: str, format: str, keep_images: bool, output: Optional[Path]):
    """Async download function."""
    print_banner()
    
    if not url.startswith("https://harmony-scan.fr/manga/"):
        print_error("Invalid URL. Must be a harmony-scan.fr manga page.")
        raise typer.Exit(1)
    
    # Parse chapters
    try:
        if chapters.lower() == "all":
            chapter_start, chapter_end = None, None
        elif "-" in chapters:
            parts = chapters.split("-")
            chapter_start, chapter_end = int(parts[0]), int(parts[1])
        else:
            chapter_start = chapter_end = int(chapters)
    except ValueError:
        print_error("Invalid chapter format. Use 'all', single number, or range (e.g., '1-10')")
        raise typer.Exit(1)
    
    # Initialize scraper
    print_info("Initializing browser...")
    scraper = MangaScraper(max_concurrent=config.max_concurrent_chapters)
    
    try:
        await scraper.start()
        print_success("Browser ready!")
        
        # Fetch manga info
        with console.status(f"[{COLORS['primary']}]Fetching manga info...[/]", spinner="dots"):
            manga = await scraper.get_manga_info(url)
        
        if not manga or not manga.chapters:
            print_error("Failed to get manga information or no chapters found")
            raise typer.Exit(1)
        
        print_success(f"Found: {manga.title} ({len(manga.chapters)} chapters)")
        
        # Select chapters
        if chapter_start is None:
            selected = manga.chapters
        else:
            selected = [
                ch for i, ch in enumerate(manga.chapters, 1)
                if chapter_start <= i <= chapter_end
            ]
        
        if not selected:
            print_error("No chapters match the selection")
            raise typer.Exit(1)
        
        print_info(f"Downloading {len(selected)} chapter(s)...")
        
        # Setup download manager
        download_dir = output if output else config.get_download_path()
        manager = DownloadManager(
            scraper=scraper,
            download_dir=download_dir,
            max_concurrent_chapters=config.max_concurrent_chapters,
            max_concurrent_images=config.max_concurrent_images
        )
        
        # Download with progress
        results = []
        task_ids = {}
        progress = create_download_progress()
        
        with progress:
            for chapter in selected:
                task_id = progress.add_task(
                    f"[{COLORS['primary']}]{chapter.title}[/]",
                    total=100,
                    status="Queued..."
                )
                task_ids[chapter.number] = task_id
            
            def on_complete(chapter, result):
                task_id = task_ids.get(chapter.number)
                if task_id:
                    if result.success:
                        status = f"✓ {result.images_downloaded}/{result.total_images}"
                    else:
                        status = f"✗ Failed"
                    progress.update(task_id, completed=100, status=status)
            
            results = await manager.download_chapters_async(
                chapters=selected,
                manga_title=manga.title,
                on_chapter_complete=on_complete
            )
        
        results.sort(key=lambda r: r.chapter.number)
        
        # Convert if needed
        if format != "images":
            print_info(f"Converting to {format.upper()}...")
            for result in results:
                if result.success:
                    if format == "pdf":
                        convert_to_pdf(result.output_path, delete_images=not keep_images)
                    elif format == "cbz":
                        convert_to_cbz(result.output_path, delete_images=not keep_images)
        
        # Summary
        success_count = sum(1 for r in results if r.success)
        print_success(f"Downloaded {success_count}/{len(results)} chapters successfully!")
        
    finally:
        await scraper.stop()


@app.command("config", help="Show or modify configuration")
def show_config(
    show: bool = typer.Option(True, "--show/--no-show", help="Show current config"),
    reset: bool = typer.Option(False, "--reset", help="Reset to defaults")
):
    """Show or reset configuration."""
    if reset:
        from config import Config, CONFIG_FILE
        new_config = Config()
        new_config.save()
        print_success("Configuration reset to defaults!")
    
    if show:
        from src.cli.display import print_settings
        print_settings(config)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    HarmonyScan Downloader - Beautiful manga downloader for harmony-scan.fr
    
    Run without arguments to start the interactive interface.
    """
    if ctx.invoked_subcommand is None:
        run_app()


if __name__ == "__main__":
    app()
