"""
HarmonyScan Downloader - CSS Selectors
Based on the provided HTML structure from harmony-scan.fr
"""

# Manga Page Selectors
MANGA_TITLE = ".post-title h1"
MANGA_COVER = ".summary_image img"
MANGA_RATING = "#averagerate"
MANGA_RATING_COUNT = "#countrate"
MANGA_ALTERNATIVE_NAMES = ".post-content_item:has(.summary-heading h5:text('Autre(s) nom(s)')) .summary-content"
MANGA_AUTHORS = ".author-content a"
MANGA_ARTISTS = ".artist-content a"
MANGA_GENRES = ".genres-content a"
MANGA_STATUS = ".post-content_item:has(.summary-heading h5:text('Statut')) .summary-content"
MANGA_TYPE = ".post-content_item:has(.summary-heading h5:text('Type')) .summary-content"
MANGA_RELEASE_YEAR = ".post-content_item:has(.summary-heading h5:text('Sortie')) .summary-content a"

# Chapter List Selectors
CHAPTER_LIST_CONTAINER = "#manga-chapters-holder"
CHAPTER_ITEMS = "ul.main.version-chap li.wp-manga-chapter"
CHAPTER_LINK = "a"
CHAPTER_THUMBNAIL = ".chapter-thumbnail img"
CHAPTER_VIEWS = ".view"

# Chapter Page Selectors (for images)
READING_CONTENT = ".reading-content"
CHAPTER_IMAGES = ".wp-manga-chapter-img"

# Base URL
BASE_URL = "https://harmony-scan.fr"
