"""
HarmonyScan Downloader - QML-Python Bridge
Exposes Python functionality to QML via Qt signals and slots
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, List

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QThread, QVariant


class DownloadWorker(QThread):
    """Worker thread for async download operations."""
    
    # Signals
    mangaLoaded = pyqtSignal(object)  # manga info dict as object
    chaptersLoaded = pyqtSignal(list)  # list of chapter dicts
    downloadProgress = pyqtSignal(str, int, int)  # chapter_title, current, total
    chapterComplete = pyqtSignal(str, bool, str)  # chapter_title, success, message
    downloadComplete = pyqtSignal(bool, str, int, int)  # success, message, downloaded, total
    errorOccurred = pyqtSignal(str)  # error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._url: str = ""
        self._chapters: List[dict] = []
        self._output_format: str = "images"
        self._keep_images: bool = True
        self._operation: str = ""  # "fetch" or "download"
        self._cancel_requested: bool = False
        
        # Import here to avoid circular imports
        from src.scraper.manga import MangaScraper
        from config import config
        
        self._config = config
        self._scraper: Optional[MangaScraper] = None
        self._manga_info = None
    
    def setFetchOperation(self, url: str):
        """Setup for fetching manga info."""
        self._url = url
        self._operation = "fetch"
    
    def setDownloadOperation(self, chapters: List[dict], output_format: str, keep_images: bool):
        """Setup for downloading chapters."""
        self._chapters = chapters
        self._output_format = output_format
        self._keep_images = keep_images
        self._operation = "download"
    
    def requestCancel(self):
        """Request cancellation of current operation."""
        self._cancel_requested = True
    
    def run(self):
        """Run the async operation in a new event loop."""
        self._cancel_requested = False
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if self._operation == "fetch":
                loop.run_until_complete(self._fetch_manga())
            elif self._operation == "download":
                loop.run_until_complete(self._download_chapters())
        except Exception as e:
            self.errorOccurred.emit(str(e))
        finally:
            loop.close()
    
    async def _fetch_manga(self):
        """Fetch manga information."""
        from src.scraper.manga import MangaScraper
        
        try:
            self._scraper = MangaScraper(max_concurrent=self._config.max_concurrent_chapters)
            await self._scraper.start()
            
            manga = await self._scraper.get_manga_info(self._url)
            
            if manga is None:
                self.errorOccurred.emit("Failed to fetch manga information")
                return
            
            self._manga_info = manga
            
            # Convert to dict for QML - use simple dict
            manga_dict = {
                "title": manga.title or "",
                "url": manga.url or "",
                "cover_url": manga.cover_url or "",
                "rating": float(manga.rating) if manga.rating else 0.0,
                "rating_count": int(manga.rating_count) if manga.rating_count else 0,
                "alternative_names": manga.alternative_names or "",
                "authors": ", ".join(manga.authors) if manga.authors else "",
                "artists": ", ".join(manga.artists) if manga.artists else "",
                "genres": ", ".join(manga.genres) if manga.genres else "",
                "status": manga.status or "",
                "manga_type": manga.manga_type or "",
                "release_year": manga.release_year or "",
            }
            
            # Convert chapters to list of dicts
            chapters = []
            for ch in manga.chapters:
                chapters.append({
                    "title": ch.title or "",
                    "url": ch.url or "",
                    "number": float(ch.number) if ch.number else 0.0,
                    "thumbnail": ch.thumbnail or "",
                    "views": int(ch.views) if ch.views else 0,
                    "selected": False
                })
            
            self.mangaLoaded.emit(manga_dict)
            self.chaptersLoaded.emit(chapters)
            
        except Exception as e:
            self.errorOccurred.emit(f"Error fetching manga: {str(e)}")
        finally:
            if self._scraper:
                await self._scraper.stop()
    
    async def _download_chapters(self):
        """Download selected chapters."""
        from src.scraper.manga import MangaScraper, Chapter
        from src.downloader.manager import DownloadManager
        from src.converters.pdf import convert_to_pdf
        from src.converters.cbz import convert_to_cbz
        
        if not self._chapters or not self._manga_info:
            self.errorOccurred.emit("No chapters selected or manga info missing")
            return
        
        try:
            self._scraper = MangaScraper(max_concurrent=self._config.max_concurrent_chapters)
            await self._scraper.start()
            
            # Convert dict chapters back to Chapter objects
            chapter_objects = []
            for ch_dict in self._chapters:
                chapter_objects.append(Chapter(
                    title=ch_dict["title"],
                    url=ch_dict["url"],
                    number=ch_dict["number"],
                    thumbnail=ch_dict.get("thumbnail"),
                    views=ch_dict.get("views")
                ))
            
            # Setup download manager
            download_dir = self._config.get_download_path()
            manager = DownloadManager(
                scraper=self._scraper,
                download_dir=download_dir,
                max_concurrent_chapters=self._config.max_concurrent_chapters,
                max_concurrent_images=self._config.max_concurrent_images
            )
            
            total_chapters = len(chapter_objects)
            completed = 0
            success_count = 0
            
            def on_chapter_complete(chapter, result):
                nonlocal completed, success_count
                completed += 1
                if result.success:
                    success_count += 1
                self.chapterComplete.emit(
                    chapter.title,
                    result.success,
                    f"{result.images_downloaded}/{result.total_images} images"
                )
                self.downloadProgress.emit(chapter.title, completed, total_chapters)
            
            # Download all chapters
            results = await manager.download_chapters_async(
                chapters=chapter_objects,
                manga_title=self._manga_info.get("title", "Unknown") if isinstance(self._manga_info, dict) else self._manga_info.title,
                on_chapter_complete=on_chapter_complete
            )
            
            # Convert if needed
            if self._output_format != "images":
                for result in results:
                    if result.success and not self._cancel_requested:
                        if self._output_format == "pdf":
                            convert_to_pdf(result.output_path, delete_images=not self._keep_images)
                        elif self._output_format == "cbz":
                            convert_to_cbz(result.output_path, delete_images=not self._keep_images)
            
            self.downloadComplete.emit(
                success_count > 0,
                f"Downloaded {success_count}/{total_chapters} chapters",
                success_count,
                total_chapters
            )
            
        except Exception as e:
            self.errorOccurred.emit(f"Download error: {str(e)}")
        finally:
            if self._scraper:
                await self._scraper.stop()


class MangaBridge(QObject):
    """Bridge between QML UI and Python backend."""
    
    # Signals for QML
    mangaInfoChanged = pyqtSignal()
    chaptersLoaded = pyqtSignal(list)
    downloadProgress = pyqtSignal(str, int, int)
    chapterComplete = pyqtSignal(str, bool, str)
    downloadComplete = pyqtSignal(bool, str, int, int)
    errorOccurred = pyqtSignal(str)
    loadingChanged = pyqtSignal(bool)
    downloadingChanged = pyqtSignal(bool)
    
    # Settings change signals
    downloadDirChanged = pyqtSignal()
    outputFormatChanged = pyqtSignal()
    keepImagesChanged = pyqtSignal()
    maxConcurrentChaptersChanged = pyqtSignal()
    maxConcurrentImagesChanged = pyqtSignal()
    enableLogsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading = False
        self._downloading = False
        self._worker: Optional[DownloadWorker] = None
        self._manga_info = None
        self._manga_dict: dict = {}
        
        from config import config
        self._config = config
    
    # Properties
    @pyqtProperty(bool, notify=loadingChanged)
    def loading(self):
        return self._loading
    
    @pyqtProperty(bool, notify=downloadingChanged)
    def downloading(self):
        return self._downloading
    
    # Manga info properties - exposed individually
    @pyqtProperty(str, notify=mangaInfoChanged)
    def mangaTitle(self):
        return self._manga_dict.get("title", "")
    
    @pyqtProperty(str, notify=mangaInfoChanged)
    def mangaUrl(self):
        return self._manga_dict.get("url", "")
    
    @pyqtProperty(str, notify=mangaInfoChanged)
    def mangaCoverUrl(self):
        return self._manga_dict.get("cover_url", "")
    
    @pyqtProperty(float, notify=mangaInfoChanged)
    def mangaRating(self):
        return self._manga_dict.get("rating", 0.0)
    
    @pyqtProperty(int, notify=mangaInfoChanged)
    def mangaRatingCount(self):
        return self._manga_dict.get("rating_count", 0)
    
    @pyqtProperty(str, notify=mangaInfoChanged)
    def mangaAuthors(self):
        return self._manga_dict.get("authors", "")
    
    @pyqtProperty(str, notify=mangaInfoChanged)
    def mangaArtists(self):
        return self._manga_dict.get("artists", "")
    
    @pyqtProperty(str, notify=mangaInfoChanged)
    def mangaGenres(self):
        return self._manga_dict.get("genres", "")
    
    @pyqtProperty(str, notify=mangaInfoChanged)
    def mangaStatus(self):
        return self._manga_dict.get("status", "")
    
    @pyqtProperty(bool, notify=mangaInfoChanged)
    def hasMangaInfo(self):
        return len(self._manga_dict) > 0 and self._manga_dict.get("title", "") != ""
    
    @pyqtProperty(str, notify=downloadDirChanged)
    def downloadDir(self):
        return str(self._config.get_download_path())
    
    @pyqtProperty(str, notify=outputFormatChanged)
    def outputFormat(self):
        return self._config.output_format
    
    @pyqtProperty(bool, notify=keepImagesChanged)
    def keepImages(self):
        return self._config.keep_images
    
    @pyqtProperty(int, notify=maxConcurrentChaptersChanged)
    def maxConcurrentChapters(self):
        return self._config.max_concurrent_chapters
    
    @pyqtProperty(int, notify=maxConcurrentImagesChanged)
    def maxConcurrentImages(self):
        return self._config.max_concurrent_images
    
    @pyqtProperty(bool, notify=enableLogsChanged)
    def enableLogs(self):
        return self._config.enable_logs
    
    # Slots callable from QML
    @pyqtSlot(str)
    def fetchManga(self, url: str):
        """Fetch manga information from URL."""
        if self._loading or self._downloading:
            return
        
        # Validate URL
        if not url.startswith("https://harmony-scan.fr/manga/"):
            self.errorOccurred.emit("Invalid URL. Must be a harmony-scan.fr manga page.")
            return
        
        self._loading = True
        self.loadingChanged.emit(True)
        
        # Create and start worker
        self._worker = DownloadWorker(self)
        self._worker.setFetchOperation(url)
        
        # Connect signals
        self._worker.mangaLoaded.connect(self._on_manga_loaded)
        self._worker.chaptersLoaded.connect(self._on_chapters_loaded)
        self._worker.errorOccurred.connect(self._on_error)
        self._worker.finished.connect(self._on_fetch_finished)
        
        self._worker.start()
    
    @pyqtSlot(list, str, bool)
    def downloadChapters(self, chapters: list, output_format: str, keep_images: bool):
        """Download selected chapters."""
        if self._loading or self._downloading:
            return
        
        if not chapters:
            self.errorOccurred.emit("No chapters selected")
            return
        
        self._downloading = True
        self.downloadingChanged.emit(True)
        
        # Create and start worker
        self._worker = DownloadWorker(self)
        self._worker._manga_info = self._manga_info
        self._worker.setDownloadOperation(chapters, output_format, keep_images)
        
        # Connect signals
        self._worker.downloadProgress.connect(self.downloadProgress)
        self._worker.chapterComplete.connect(self.chapterComplete)
        self._worker.downloadComplete.connect(self._on_download_complete)
        self._worker.errorOccurred.connect(self._on_error)
        self._worker.finished.connect(self._on_download_finished)
        
        self._worker.start()
    
    @pyqtSlot()
    def cancelDownload(self):
        """Cancel current download operation."""
        if self._worker:
            self._worker.requestCancel()
    
    @pyqtSlot()
    def clearMangaInfo(self):
        """Clear the current manga info."""
        self._manga_dict = {}
        self._manga_info = None
        self.mangaInfoChanged.emit()
    
    @pyqtSlot()
    def openDownloadFolder(self):
        """Open the download folder in file explorer."""
        download_path = self._config.get_download_path()
        os.startfile(str(download_path))
    
    @pyqtSlot(str)
    def setDownloadDir(self, path: str):
        """Set the download directory."""
        self._config.download_dir = path
        self._config.save()
        self.downloadDirChanged.emit()
    
    @pyqtSlot(str)
    def setOutputFormat(self, format: str):
        """Set the output format."""
        if format in ("images", "pdf", "cbz"):
            self._config.output_format = format
            self._config.save()
            self.outputFormatChanged.emit()
    
    @pyqtSlot(bool)
    def setKeepImages(self, keep: bool):
        """Set whether to keep images after conversion."""
        self._config.keep_images = keep
        self._config.save()
        self.keepImagesChanged.emit()
    
    @pyqtSlot(int)
    def setMaxConcurrentChapters(self, value: int):
        """Set max concurrent chapters."""
        if 1 <= value <= 10:
            self._config.max_concurrent_chapters = value
            self._config.save()
            self.maxConcurrentChaptersChanged.emit()
    
    @pyqtSlot(int)
    def setMaxConcurrentImages(self, value: int):
        """Set max concurrent images."""
        if 1 <= value <= 20:
            self._config.max_concurrent_images = value
            self._config.save()
            self.maxConcurrentImagesChanged.emit()
    
    @pyqtSlot(bool)
    def setEnableLogs(self, enable: bool):
        """Set whether to enable debug logs."""
        self._config.enable_logs = enable
        self._config.save()
        self.enableLogsChanged.emit()
    
    # Internal handlers
    def _on_manga_loaded(self, manga_dict):
        """Handle manga loaded from worker."""
        self._manga_dict = manga_dict if isinstance(manga_dict, dict) else {}
        self._manga_info = manga_dict  # Store for worker
        self.mangaInfoChanged.emit()
    
    def _on_chapters_loaded(self, chapters: list):
        self.chaptersLoaded.emit(chapters)
    
    def _on_error(self, error: str):
        self._loading = False
        self._downloading = False
        self.loadingChanged.emit(False)
        self.downloadingChanged.emit(False)
        self.errorOccurred.emit(error)
    
    def _on_fetch_finished(self):
        self._loading = False
        self.loadingChanged.emit(False)
    
    def _on_download_complete(self, success: bool, message: str, downloaded: int, total: int):
        self.downloadComplete.emit(success, message, downloaded, total)
    
    def _on_download_finished(self):
        self._downloading = False
        self.downloadingChanged.emit(False)
