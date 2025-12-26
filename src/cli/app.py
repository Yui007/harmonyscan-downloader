"""
HarmonyScan Downloader - Main CLI Application
Orchestrates the download workflow with async support
"""

import asyncio
import sys
from pathlib import Path
from typing import List

from rich.console import Console

from .display import (
    console, print_banner, print_manga_info, print_chapter_list,
    print_success, print_error, print_warning, print_info,
    create_download_progress, print_download_summary, COLORS
)
from .prompts import (
    prompt_manga_url, prompt_chapter_selection, prompt_output_format,
    prompt_keep_images, prompt_save_settings, prompt_continue,
    prompt_main_menu, prompt_settings_menu, prompt_setting_value
)
from ..scraper.manga import MangaScraper, Chapter
from ..downloader.manager import DownloadManager, DownloadProgress
from ..converters.pdf import convert_to_pdf
from ..converters.cbz import convert_to_cbz
from config import config, Config


class HarmonyScanApp:
    """Main application class for HarmonyScan Downloader."""
    
    def __init__(self):
        self.scraper: MangaScraper = None
        self.config = config
    
    def run(self):
        """Run the main application loop."""
        print_banner()
        
        # Run the async main loop
        try:
            asyncio.run(self._async_main())
        except KeyboardInterrupt:
            console.print()
            print_warning("Interrupted by user")
    
    async def _async_main(self):
        """Async main loop."""
        try:
            # Initialize scraper
            print_info("Initializing browser...")
            self.scraper = MangaScraper(max_concurrent=self.config.max_concurrent_chapters)
            await self.scraper.start()
            print_success("Browser ready!")
            
            # Main loop
            while True:
                choice = prompt_main_menu()
                
                if choice == "download":
                    await self._download_flow()
                elif choice == "settings":
                    self._settings_flow()
                else:
                    break
            
            print_info("Goodbye! 👋")
            
        finally:
            if self.scraper:
                print_info("Closing browser...")
                await self.scraper.stop()
    
    async def _download_flow(self):
        """Handle the download workflow."""
        # Get manga URL
        url = prompt_manga_url()
        
        if not url.startswith("https://harmony-scan.fr/manga/"):
            print_error("Invalid URL. Must be a harmony-scan.fr manga page.")
            return
        
        # Fetch manga info
        console.print()
        with console.status(f"[{COLORS['primary']}]Fetching manga info...[/]", spinner="dots"):
            try:
                manga = await self.scraper.get_manga_info(url)
            except Exception as e:
                print_error(f"Failed to fetch manga info: {e}")
                return
        
        if not manga:
            print_error("Failed to get manga information")
            return
        
        # Display manga info
        print_manga_info(manga)
        
        if not manga.chapters:
            print_error("No chapters found!")
            return
        
        # Show chapters
        print_chapter_list(manga.chapters)
        
        # Get chapter selection
        mode, start, end = prompt_chapter_selection(len(manga.chapters))
        
        # Filter chapters
        selected_chapters = self._select_chapters(manga.chapters, mode, start, end)
        
        if not selected_chapters:
            print_error("No chapters selected")
            return
        
        print_info(f"Selected {len(selected_chapters)} chapter(s)")
        
        # Get output format
        output_format = prompt_output_format()
        
        # Ask about keeping images if converting
        keep_images = True
        if output_format != "images":
            keep_images = prompt_keep_images()
        
        # Download chapters
        console.print()
        print_info(f"Starting download to: {self.config.get_download_path()}")
        
        progress = create_download_progress()
        task_ids = {}
        results = []
        
        # Create download manager
        manager = DownloadManager(
            scraper=self.scraper,
            download_dir=self.config.get_download_path(),
            max_concurrent_chapters=self.config.max_concurrent_chapters,
            max_concurrent_images=self.config.max_concurrent_images
        )
        
        with progress:
            # Create progress tasks for all chapters
            for chapter in selected_chapters:
                task_id = progress.add_task(
                    f"[{COLORS['primary']}]{chapter.title}[/]",
                    total=100,
                    status="Queued..."
                )
                task_ids[chapter.number] = task_id
            
            # Callback when each chapter completes
            def on_chapter_complete(chapter, result):
                task_id = task_ids.get(chapter.number)
                if task_id is not None:
                    if result.success:
                        status = f"✓ {result.images_downloaded}/{result.total_images}"
                    else:
                        status = f"✗ Failed"
                    progress.update(task_id, completed=100, status=status)
            
            # Download all chapters (async scraping + concurrent image downloads)
            results = await manager.download_chapters_async(
                chapters=selected_chapters,
                manga_title=manga.title,
                on_chapter_complete=on_chapter_complete
            )
        
        # Sort results
        results.sort(key=lambda r: r.chapter.number)
        
        # Convert if needed
        if output_format != "images":
            console.print()
            print_info(f"Converting to {output_format.upper()}...")
            
            for result in results:
                if result.success:
                    if output_format == "pdf":
                        pdf_path = convert_to_pdf(
                            result.output_path,
                            delete_images=not keep_images
                        )
                        if pdf_path:
                            print_success(f"Created: {pdf_path.name}")
                    elif output_format == "cbz":
                        cbz_path = convert_to_cbz(
                            result.output_path,
                            delete_images=not keep_images
                        )
                        if cbz_path:
                            print_success(f"Created: {cbz_path.name}")
        
        # Show summary
        console.print()
        print_download_summary(results)
        
        # Ask to save settings
        if prompt_save_settings():
            self.config.output_format = output_format
            self.config.keep_images = keep_images
            self.config.save()
            print_success("Settings saved!")
    
    def _select_chapters(
        self,
        chapters: List[Chapter],
        mode: str,
        start: int,
        end: int
    ) -> List[Chapter]:
        """Select chapters based on user input."""
        if mode == "all":
            return chapters
        
        selected = []
        for i, chapter in enumerate(chapters, 1):
            if start <= i <= end:
                selected.append(chapter)
        
        return selected
    
    def _settings_flow(self):
        """Handle the settings workflow."""
        while True:
            setting = prompt_settings_menu(self.config)
            
            if setting is None:
                break
            
            current_value = getattr(self.config, setting)
            new_value = prompt_setting_value(setting, current_value)
            
            setattr(self.config, setting, new_value)
            self.config.save()
            print_success(f"Setting '{setting}' updated!")


def run_app():
    """Entry point for the application."""
    app = HarmonyScanApp()
    app.run()
