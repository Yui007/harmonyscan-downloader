"""
HarmonyScan Downloader - CLI Prompts
Interactive prompts using Rich and Typer
"""

from rich.prompt import Prompt, Confirm, IntPrompt
from rich.console import Console
from typing import List, Tuple, Optional

from .display import COLORS, console


def prompt_manga_url() -> str:
    """Prompt user for manga URL."""
    console.print()
    url = Prompt.ask(
        f"[bold {COLORS['accent']}]Enter manga URL[/]",
        default="https://harmony-scan.fr/manga/"
    )
    return url.strip()


def prompt_chapter_selection(total_chapters: int) -> Tuple[str, Optional[int], Optional[int]]:
    """
    Prompt user for chapter selection.
    
    Returns:
        Tuple of (mode, start, end) where mode is 'single', 'range', or 'all'
    """
    console.print()
    console.print(f"[bold {COLORS['primary']}]Chapter Selection[/]")
    console.print(f"  [1] Download a single chapter")
    console.print(f"  [2] Download a range of chapters")
    console.print(f"  [3] Download all chapters")
    console.print()
    
    choice = Prompt.ask(
        f"[{COLORS['accent']}]Select option[/]",
        choices=["1", "2", "3"],
        default="3"
    )
    
    if choice == "1":
        chapter_num = IntPrompt.ask(
            f"[{COLORS['accent']}]Enter chapter number[/]",
            default=1
        )
        return ("single", chapter_num, chapter_num)
    
    elif choice == "2":
        start = IntPrompt.ask(
            f"[{COLORS['accent']}]Start chapter[/]",
            default=1
        )
        end = IntPrompt.ask(
            f"[{COLORS['accent']}]End chapter[/]",
            default=total_chapters
        )
        return ("range", min(start, end), max(start, end))
    
    else:
        return ("all", 1, total_chapters)


def prompt_output_format() -> str:
    """Prompt user for output format."""
    console.print()
    console.print(f"[bold {COLORS['primary']}]Output Format[/]")
    console.print(f"  [1] Images (raw image files)")
    console.print(f"  [2] PDF (combined PDF per chapter)")
    console.print(f"  [3] CBZ (comic book archive)")
    console.print()
    
    choice = Prompt.ask(
        f"[{COLORS['accent']}]Select format[/]",
        choices=["1", "2", "3"],
        default="1"
    )
    
    formats = {"1": "images", "2": "pdf", "3": "cbz"}
    return formats[choice]


def prompt_keep_images() -> bool:
    """Prompt user whether to keep images after conversion."""
    return Confirm.ask(
        f"[{COLORS['accent']}]Keep original images after conversion?[/]",
        default=True
    )


def prompt_save_settings() -> bool:
    """Prompt user whether to save current settings as default."""
    return Confirm.ask(
        f"[{COLORS['accent']}]Save these settings as default?[/]",
        default=False
    )


def prompt_continue() -> bool:
    """Prompt user to continue or exit."""
    return Confirm.ask(
        f"[{COLORS['accent']}]Download another manga?[/]",
        default=True
    )


def prompt_main_menu() -> str:
    """
    Display main menu and get user choice.
    
    Returns:
        'download', 'settings', or 'exit'
    """
    console.print()
    console.print(f"[bold {COLORS['primary']}]Main Menu[/]")
    console.print(f"  [1] 📥 Download Manga")
    console.print(f"  [2] ⚙️  Settings")
    console.print(f"  [3] 🚪 Exit")
    console.print()
    
    choice = Prompt.ask(
        f"[{COLORS['accent']}]Select option[/]",
        choices=["1", "2", "3"],
        default="1"
    )
    
    return {"1": "download", "2": "settings", "3": "exit"}[choice]


def prompt_settings_menu(config) -> Optional[str]:
    """
    Display settings menu and get user choice.
    
    Returns:
        Setting key to modify, or None to go back
    """
    from .display import print_settings
    print_settings(config)
    
    console.print()
    console.print(f"[bold {COLORS['primary']}]Modify Settings[/]")
    console.print(f"  [1] Download Directory")
    console.print(f"  [2] Output Format")
    console.print(f"  [3] Keep Images")
    console.print(f"  [4] Concurrent Chapters")
    console.print(f"  [5] Concurrent Images")
    console.print(f"  [6] ← Back to Main Menu")
    console.print()
    
    choice = Prompt.ask(
        f"[{COLORS['accent']}]Select option[/]",
        choices=["1", "2", "3", "4", "5", "6"],
        default="6"
    )
    
    return {
        "1": "download_dir",
        "2": "output_format",
        "3": "keep_images",
        "4": "max_concurrent_chapters",
        "5": "max_concurrent_images",
        "6": None
    }[choice]


def prompt_setting_value(setting_key: str, current_value):
    """Prompt user for a new setting value."""
    if setting_key == "download_dir":
        return Prompt.ask(
            f"[{COLORS['accent']}]Download directory[/]",
            default=str(current_value)
        )
    
    elif setting_key == "output_format":
        console.print(f"  [1] images  [2] pdf  [3] cbz")
        choice = Prompt.ask(
            f"[{COLORS['accent']}]Format[/]",
            choices=["1", "2", "3"],
            default={"images": "1", "pdf": "2", "cbz": "3"}.get(current_value, "1")
        )
        return {"1": "images", "2": "pdf", "3": "cbz"}[choice]
    
    elif setting_key == "keep_images":
        return Confirm.ask(
            f"[{COLORS['accent']}]Keep images after conversion?[/]",
            default=current_value
        )
    
    elif setting_key in ("max_concurrent_chapters", "max_concurrent_images"):
        return IntPrompt.ask(
            f"[{COLORS['accent']}]Value (1-10)[/]",
            default=current_value
        )
    
    return current_value
