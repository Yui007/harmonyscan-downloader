"""
HarmonyScan Downloader - CSS Selectors
Based on the provided HTML structure from harmony-scan.fr
"""

# Manga Page Selectors
MANGA_TITLE = ".post-title h1"
MANGA_COVER = ".summary_image img"
MANGA_RATING = "#averagerate"
MANGA_RATING_COUNT = "#countrate"
MANGA_AUTHORS = ".author-content a"
MANGA_ARTISTS = ".artist-content a, .artist-content font a"
MANGA_GENRES = ".genres-content a"
MANGA_SYNOPSIS = ".description-summary .summary__content p"
MANGA_FAVORITES = ".add-bookmark .action_detail span"

# These use simpler selectors that work with both French and English headings
# We'll extract them dynamically in the scraper instead

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
