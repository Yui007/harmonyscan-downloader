"""
HarmonyScan Downloader - Download Manager (Async Version)
Orchestrates concurrent chapter and image downloads
"""

import asyncio
import logging
import re
import time
from pathlib import Path
from typing import List, Callable, Optional, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .image import download_image, get_image_extension
from ..scraper.manga import Chapter, MangaScraper

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Result of a chapter download."""
    chapter: Chapter
    success: bool
    images_downloaded: int
    total_images: int
    output_path: Path
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class DownloadProgress:
    """Progress information for callbacks."""
    chapter_title: str
    chapter_current: int
    chapter_total: int
    image_current: int
    image_total: int
    status: str


class DownloadManager:
    """Manages concurrent downloads of manga chapters and images."""
    
    def __init__(
        self,
        scraper: MangaScraper,
        download_dir: Path,
        max_concurrent_chapters: int = 3,
        max_concurrent_images: int = 5,
        max_retries: int = 3,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ):
        self.scraper = scraper
        self.download_dir = download_dir
        self.max_concurrent_chapters = max_concurrent_chapters
        self.max_concurrent_images = max_concurrent_images
        self.max_retries = max_retries
        self.progress_callback = progress_callback
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string to be safe for filenames."""
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.strip('. ')
        return name[:100]
    
    def _report_progress(
        self,
        chapter_title: str,
        chapter_current: int,
        chapter_total: int,
        image_current: int,
        image_total: int,
        status: str
    ):
        """Report progress via callback if available."""
        if self.progress_callback:
            self.progress_callback(DownloadProgress(
                chapter_title=chapter_title,
                chapter_current=chapter_current,
                chapter_total=chapter_total,
                image_current=image_current,
                image_total=image_total,
                status=status
            ))
    
    def _download_images_for_chapter(
        self,
        chapter: Chapter,
        image_urls: List[str],
        manga_title: str,
        chapter_index: int,
        total_chapters: int
    ) -> DownloadResult:
        """
        Download images for a chapter (runs in thread pool for image downloads).
        """
        # Create chapter folder
        safe_manga = self._sanitize_filename(manga_title)
        safe_chapter = self._sanitize_filename(chapter.title)
        chapter_path = self.download_dir / safe_manga / safe_chapter
        chapter_path.mkdir(parents=True, exist_ok=True)
        
        if not image_urls:
            return DownloadResult(
                chapter=chapter,
                success=False,
                images_downloaded=0,
                total_images=0,
                output_path=chapter_path,
                error="No images found"
            )
        
        total_images = len(image_urls)
        downloaded_count = 0
        
        self._report_progress(
            chapter.title, chapter_index, total_chapters,
            0, total_images, f"Downloading {total_images} images..."
        )
        
        # Download images concurrently using ThreadPoolExecutor
        # (requests library is thread-safe, unlike Playwright)
        def download_single(args):
            idx, url = args
            ext = get_image_extension(url)
            filename = f"{idx:03d}{ext}"
            save_path = chapter_path / filename
            return download_image(url, save_path, max_retries=3)
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_images) as executor:
            results = list(executor.map(
                download_single,
                [(i, url) for i, url in enumerate(image_urls, start=1)]
            ))
        
        downloaded_count = sum(1 for r in results if r)
        
        # Consider success if we got at least 90% of images
        success = (downloaded_count / total_images) >= 0.9 if total_images > 0 else False
        
        self._report_progress(
            chapter.title, chapter_index, total_chapters,
            downloaded_count, total_images,
            f"✓ {downloaded_count}/{total_images}" if success else f"✗ {downloaded_count}/{total_images}"
        )
        
        return DownloadResult(
            chapter=chapter,
            success=success,
            images_downloaded=downloaded_count,
            total_images=total_images,
            output_path=chapter_path,
            error=None if success else f"Only {downloaded_count}/{total_images} images"
        )
    
    async def download_chapters_async(
        self,
        chapters: List[Chapter],
        manga_title: str,
        on_chapter_complete: Optional[Callable[[Chapter, DownloadResult], None]] = None
    ) -> List[DownloadResult]:
        """
        Download multiple chapters using async scraping + concurrent image downloads.
        
        This method:
        1. Fetches all chapter image URLs concurrently (using async Playwright)
        2. Downloads images for each chapter (using thread pool)
        """
        total_chapters = len(chapters)
        logger.info(f"Starting download of {total_chapters} chapters...")
        
        # Step 1: Fetch all chapter image URLs concurrently
        logger.info("Fetching chapter image URLs concurrently...")
        chapter_images = await self.scraper.get_multiple_chapter_images(chapters)
        
        # Step 2: Download images for each chapter
        results = []
        for i, (chapter, image_urls) in enumerate(chapter_images, start=1):
            logger.info(f"Downloading images for {chapter.title} ({len(image_urls)} images)")
            
            result = self._download_images_for_chapter(
                chapter=chapter,
                image_urls=image_urls,
                manga_title=manga_title,
                chapter_index=i,
                total_chapters=total_chapters
            )
            
            results.append(result)
            
            if on_chapter_complete:
                on_chapter_complete(chapter, result)
        
        logger.info(f"Download complete: {sum(1 for r in results if r.success)}/{total_chapters} successful")
        
        return results
    
    # Synchronous wrapper for backward compatibility
    def download_chapters_concurrent(
        self,
        chapters: List[Chapter],
        manga_title: str,
        on_chapter_complete: Optional[Callable[[Chapter, DownloadResult], None]] = None
    ) -> List[DownloadResult]:
        """
        Synchronous wrapper that runs the async download.
        """
        return asyncio.get_event_loop().run_until_complete(
            self.download_chapters_async(chapters, manga_title, on_chapter_complete)
        )
