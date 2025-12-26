"""
HarmonyScan Downloader - Display Components
Beautiful console UI using Rich library
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.style import Style
from rich.align import Align
from rich import box
from typing import List, Optional

from ..scraper.manga import MangaInfo, Chapter


console = Console()


# Color scheme
COLORS = {
    "primary": "#FF6B9D",      # Pink
    "secondary": "#C084FC",    # Purple
    "accent": "#22D3EE",       # Cyan
    "success": "#4ADE80",      # Green
    "warning": "#FBBF24",      # Yellow
    "error": "#F87171",        # Red
    "muted": "#94A3B8",        # Gray
}


def print_banner():
    """Display the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ ██████╗ ███╗   ██╗██╗   ██╗ ║
║   ██║  ██║██╔══██╗██╔══██╗████╗ ████║██╔═══██╗████╗  ██║╚██╗ ██╔╝ ║
║   ███████║███████║██████╔╝██╔████╔██║██║   ██║██╔██╗ ██║ ╚████╔╝  ║
║   ██╔══██║██╔══██║██╔══██╗██║╚██╔╝██║██║   ██║██║╚██╗██║  ╚██╔╝   ║
║   ██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║   ██║    ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    ║
║                      SCAN DOWNLOADER                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    
    gradient_banner = Text(banner)
    gradient_banner.stylize(f"bold {COLORS['primary']}")
    
    console.print(gradient_banner)
    console.print(
        Align.center(
            Text("⚡ Fast & Beautiful Manga Downloader for harmony-scan.fr ⚡", 
                 style=f"italic {COLORS['muted']}")
        )
    )
    console.print()


def print_manga_info(manga: MangaInfo):
    """Display manga information in a beautiful panel."""
    # Create info table
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column("Label", style=f"bold {COLORS['accent']}")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("📖 Title", manga.title)
    
    if manga.rating:
        stars = "★" * int(manga.rating) + "☆" * (5 - int(manga.rating))
        rating_text = f"{stars} {manga.rating}/5"
        if manga.rating_count:
            rating_text += f" ({manga.rating_count} votes)"
        info_table.add_row("⭐ Rating", rating_text)
    
    if manga.authors:
        info_table.add_row("✍️  Author(s)", ", ".join(manga.authors))
    
    if manga.artists:
        info_table.add_row("🎨 Artist(s)", ", ".join(manga.artists))
    
    if manga.genres:
        genres_text = " • ".join(manga.genres)
        info_table.add_row("🏷️  Genres", genres_text)
    
    if manga.status:
        status_color = COLORS['success'] if 'Terminé' in manga.status else COLORS['warning']
        info_table.add_row("📊 Status", Text(manga.status, style=status_color))
    
    if manga.manga_type:
        info_table.add_row("📚 Type", manga.manga_type)
    
    if manga.release_year:
        info_table.add_row("📅 Release", manga.release_year)
    
    info_table.add_row("📑 Chapters", str(len(manga.chapters)))
    
    panel = Panel(
        info_table,
        title=f"[bold {COLORS['primary']}]Manga Information[/]",
        border_style=COLORS['secondary'],
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(panel)


def print_chapter_list(chapters: List[Chapter], show_limit: int = 10):
    """Display chapter list in a table."""
    table = Table(
        title=f"[bold {COLORS['primary']}]Available Chapters ({len(chapters)} total)[/]",
        box=box.ROUNDED,
        border_style=COLORS['muted'],
        header_style=f"bold {COLORS['accent']}"
    )
    
    table.add_column("#", justify="right", width=6)
    table.add_column("Chapter", style="white")
    table.add_column("Views", justify="right", style=COLORS['muted'])
    
    # Show first few and last few if too many
    if len(chapters) <= show_limit:
        display_chapters = [(i, ch) for i, ch in enumerate(chapters, 1)]
    else:
        half = show_limit // 2
        display_chapters = [(i, ch) for i, ch in enumerate(chapters[:half], 1)]
        display_chapters.append((None, None))  # Ellipsis marker
        display_chapters.extend([(i, ch) for i, ch in enumerate(chapters[-half:], len(chapters) - half + 1)])
    
    for idx, chapter in display_chapters:
        if chapter is None:
            table.add_row("...", f"... {len(chapters) - show_limit} more chapters ...", "...")
        else:
            views = f"{chapter.views:,}" if chapter.views else "-"
            table.add_row(str(idx), chapter.title, views)
    
    console.print(table)


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold {COLORS['success']}]✓[/] {message}")


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold {COLORS['error']}]✗[/] {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold {COLORS['warning']}]⚠[/] {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[bold {COLORS['accent']}]ℹ[/] {message}")


def create_download_progress() -> Progress:
    """Create a progress bar for downloads."""
    return Progress(
        SpinnerColumn(style=COLORS['primary']),
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=40, style=COLORS['muted'], complete_style=COLORS['primary']),
        TaskProgressColumn(),
        TextColumn("[{task.fields[status]}]", style=COLORS['muted']),
        console=console,
        expand=False
    )


def print_settings(config):
    """Display current settings."""
    table = Table(
        title=f"[bold {COLORS['primary']}]Current Settings[/]",
        box=box.ROUNDED,
        border_style=COLORS['muted']
    )
    
    table.add_column("Setting", style=f"bold {COLORS['accent']}")
    table.add_column("Value", style="white")
    
    table.add_row("Download Directory", config.download_dir)
    table.add_row("Output Format", config.output_format.upper())
    table.add_row("Keep Images", "Yes" if config.keep_images else "No")
    table.add_row("Max Concurrent Chapters", str(config.max_concurrent_chapters))
    table.add_row("Max Concurrent Images", str(config.max_concurrent_images))
    
    console.print(table)


def print_download_summary(results):
    """Display download summary."""
    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    
    table = Table(
        title=f"[bold {COLORS['primary']}]Download Summary[/]",
        box=box.ROUNDED,
        border_style=COLORS['muted']
    )
    
    table.add_column("Chapter", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Images", justify="right")
    table.add_column("Path", style=COLORS['muted'])
    
    for result in results:
        if result.success:
            status = Text("✓ Success", style=f"bold {COLORS['success']}")
        else:
            status = Text("✗ Failed", style=f"bold {COLORS['error']}")
        
        images = f"{result.images_downloaded}/{result.total_images}"
        path = str(result.output_path.name)
        
        table.add_row(result.chapter.title, status, images, path)
    
    console.print(table)
    
    if success_count == total_count:
        print_success(f"All {total_count} chapters downloaded successfully!")
    else:
        print_warning(f"{success_count}/{total_count} chapters downloaded successfully")
