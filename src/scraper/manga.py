"""
HarmonyScan Downloader - Manga Scraper (Async Version)
Playwright async API for concurrent chapter scraping
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple
from playwright.async_api import async_playwright, Browser, Page, Playwright, BrowserContext
import re

from . import selectors

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class Chapter:
    """Represents a manga chapter."""
    title: str
    url: str
    number: float
    thumbnail: Optional[str] = None
    views: Optional[int] = None


@dataclass
class MangaInfo:
    """Represents manga metadata."""
    title: str
    url: str
    cover_url: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    alternative_names: Optional[str] = None
    authors: List[str] = None
    artists: List[str] = None
    genres: List[str] = None
    status: Optional[str] = None
    manga_type: Optional[str] = None
    release_year: Optional[str] = None
    chapters: List[Chapter] = None
    
    def __post_init__(self):
        if self.authors is None:
            self.authors = []
        if self.artists is None:
            self.artists = []
        if self.genres is None:
            self.genres = []
        if self.chapters is None:
            self.chapters = []


class MangaScraper:
    """
    Async scraper for harmony-scan.fr manga pages.
    Uses Playwright async API for concurrent operations.
    """
    
    def __init__(self, max_concurrent: int = 3):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._max_concurrent = max_concurrent
        self._semaphore: Optional[asyncio.Semaphore] = None
        logger.info(f"MangaScraper initialized with max_concurrent={max_concurrent}")
    
    async def start(self) -> None:
        """Initialize Playwright and browser."""
        logger.info("Starting Playwright (async)...")
        self._playwright = await async_playwright().start()
        
        logger.info("Launching browser...")
        self._browser = await self._playwright.chromium.launch(headless=False)
        
        # Semaphore to limit concurrent operations
        self._semaphore = asyncio.Semaphore(self._max_concurrent)
        
        logger.info("Browser ready!")
    
    async def stop(self) -> None:
        """Close browser and cleanup Playwright."""
        logger.info("Stopping browser...")
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser stopped")
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
    
    def _extract_chapter_number(self, title: str) -> float:
        """Extract chapter number from title string."""
        match = re.search(r'chapitre[- ]?(\d+(?:\.\d+)?)', title.lower())
        if match:
            return float(match.group(1))
        match = re.search(r'(\d+(?:\.\d+)?)', title)
        if match:
            return float(match.group(1))
        return 0.0
    
    async def _new_context(self) -> BrowserContext:
        """Create a new browser context."""
        return await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
    
    async def get_manga_info(self, url: str) -> MangaInfo:
        """Fetch manga information from a manga page URL."""
        logger.info(f"Fetching manga info from: {url}")
        
        context = await self._new_context()
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector(selectors.MANGA_TITLE, timeout=10000)
            
            # Extract basic info
            title = await page.locator(selectors.MANGA_TITLE).inner_text()
            title = title.strip()
            logger.info(f"Found manga: {title}")
            
            # Cover image
            cover_url = None
            cover_elem = page.locator(selectors.MANGA_COVER)
            if await cover_elem.count() > 0:
                cover_url = await cover_elem.first.get_attribute("src") or await cover_elem.first.get_attribute("data-src")
            
            # Rating
            rating = None
            rating_elem = page.locator(selectors.MANGA_RATING)
            if await rating_elem.count() > 0:
                try:
                    rating_text = await rating_elem.inner_text()
                    rating = float(rating_text.strip())
                except ValueError:
                    pass
            
            # Rating count
            rating_count = None
            rating_count_elem = page.locator(selectors.MANGA_RATING_COUNT)
            if await rating_count_elem.count() > 0:
                try:
                    count_text = await rating_count_elem.inner_text()
                    rating_count = int(count_text.strip())
                except ValueError:
                    pass
            
            # Authors
            authors = []
            author_elems = page.locator(selectors.MANGA_AUTHORS)
            count = await author_elems.count()
            for i in range(count):
                text = await author_elems.nth(i).inner_text()
                authors.append(text.strip())
            
            # Artists
            artists = []
            artist_elems = page.locator(selectors.MANGA_ARTISTS)
            count = await artist_elems.count()
            for i in range(count):
                text = await artist_elems.nth(i).inner_text()
                artists.append(text.strip())
            
            # Genres
            genres = []
            genre_elems = page.locator(selectors.MANGA_GENRES)
            count = await genre_elems.count()
            for i in range(count):
                text = await genre_elems.nth(i).inner_text()
                genres.append(text.strip())
            
            # Status
            status = None
            status_items = page.locator(".post-content_item")
            count = await status_items.count()
            for i in range(count):
                item = status_items.nth(i)
                heading = item.locator(".summary-heading h5")
                if await heading.count() > 0:
                    heading_text = await heading.inner_text()
                    if "Statut" in heading_text:
                        status = await item.locator(".summary-content").inner_text()
                        status = status.strip()
                        break
            
            # Type
            manga_type = None
            for i in range(count):
                item = status_items.nth(i)
                heading = item.locator(".summary-heading h5")
                if await heading.count() > 0:
                    heading_text = await heading.inner_text()
                    if "Type" in heading_text:
                        manga_type = await item.locator(".summary-content").inner_text()
                        manga_type = manga_type.strip()
                        break
            
            # Release year
            release_year = None
            release_elem = page.locator(selectors.MANGA_RELEASE_YEAR)
            if await release_elem.count() > 0:
                release_year = await release_elem.first.inner_text()
                release_year = release_year.strip()
            
            # Get chapters
            chapters = await self._extract_chapters(page)
            logger.info(f"Found {len(chapters)} chapters")
            
            return MangaInfo(
                title=title,
                url=url,
                cover_url=cover_url,
                rating=rating,
                rating_count=rating_count,
                authors=authors,
                artists=artists,
                genres=genres,
                status=status,
                manga_type=manga_type,
                release_year=release_year,
                chapters=chapters
            )
            
        finally:
            await page.close()
            await context.close()
    
    async def _extract_chapters(self, page: Page) -> List[Chapter]:
        """Extract chapter list from loaded page."""
        chapters = []
        
        try:
            await page.wait_for_selector(selectors.CHAPTER_ITEMS, timeout=10000)
        except:
            logger.warning("No chapters found")
            return chapters
        
        chapter_items = page.locator(selectors.CHAPTER_ITEMS)
        count = await chapter_items.count()
        
        for i in range(count):
            item = chapter_items.nth(i)
            
            link = item.locator(selectors.CHAPTER_LINK).first
            if await link.count() == 0:
                continue
            
            title = await link.inner_text()
            title = title.strip()
            url = await link.get_attribute("href")
            number = self._extract_chapter_number(title)
            
            thumbnail = None
            thumb_elem = item.locator(selectors.CHAPTER_THUMBNAIL)
            if await thumb_elem.count() > 0:
                thumbnail = await thumb_elem.get_attribute("src")
            
            views = None
            views_elem = item.locator(selectors.CHAPTER_VIEWS)
            if await views_elem.count() > 0:
                views_text = await views_elem.inner_text()
                views_text = views_text.strip()
                match = re.search(r'(\d+)', views_text.replace(',', '').replace(' ', ''))
                if match:
                    views = int(match.group(1))
            
            chapters.append(Chapter(
                title=title,
                url=url,
                number=number,
                thumbnail=thumbnail,
                views=views
            ))
        
        chapters.sort(key=lambda c: c.number)
        return chapters
    
    async def get_chapter_images(self, chapter_url: str) -> List[str]:
        """Get all image URLs from a chapter page."""
        async with self._semaphore:
            logger.info(f"Getting images from: {chapter_url}")
            
            context = await self._new_context()
            page = await context.new_page()
            
            try:
                await page.goto(chapter_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_selector(selectors.CHAPTER_IMAGES, timeout=15000)
                
                # Wait for lazy loading
                await page.wait_for_timeout(2000)
                
                # Scroll to trigger lazy load
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                
                images = []
                img_elems = page.locator(selectors.CHAPTER_IMAGES)
                count = await img_elems.count()
                
                for i in range(count):
                    img = img_elems.nth(i)
                    src = await img.get_attribute("src") or await img.get_attribute("data-src")
                    if src:
                        src = src.strip()
                        if src and not src.startswith("data:"):
                            images.append(src)
                
                logger.info(f"Found {len(images)} images in {chapter_url}")
                return images
                
            finally:
                await page.close()
                await context.close()
    
    async def get_multiple_chapter_images(
        self, 
        chapters: List[Chapter],
        max_retries: int = 3
    ) -> List[Tuple[Chapter, List[str]]]:
        """
        Get images from multiple chapters CONCURRENTLY using asyncio.gather().
        Includes retry logic with exponential backoff.
        
        Returns:
            List of (chapter, image_urls) tuples
        """
        logger.info(f"Fetching images for {len(chapters)} chapters concurrently...")
        
        async def fetch_with_retry(chapter: Chapter) -> Tuple[Chapter, List[str]]:
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        wait_time = 2 ** (attempt + 1)  # 4s, 8s
                        logger.info(f"Retry {attempt + 1}/{max_retries} for {chapter.title} in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    
                    images = await self.get_chapter_images(chapter.url)
                    
                    if images:  # Success
                        if attempt > 0:
                            logger.info(f"Retry successful for {chapter.title}")
                        return (chapter, images)
                    else:
                        logger.warning(f"No images found for {chapter.title}, retrying...")
                        last_error = "No images found"
                        
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"Attempt {attempt + 1} failed for {chapter.title}: {e}")
            
            # All retries exhausted
            logger.error(f"All {max_retries} retries failed for {chapter.title}: {last_error}")
            return (chapter, [])
        
        # Run all fetches concurrently (semaphore limits actual concurrency)
        results = await asyncio.gather(*[fetch_with_retry(ch) for ch in chapters])
        
        return list(results)

