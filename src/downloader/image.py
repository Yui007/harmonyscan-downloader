"""
HarmonyScan Downloader - Image Download Worker
Thread-safe image downloading with retry logic
"""

import os
import time
import requests
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse


def download_image(
    url: str,
    save_path: Path,
    max_retries: int = 3,
    timeout: int = 30,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> bool:
    """
    Download an image from URL with retry logic.
    
    Args:
        url: Image URL to download
        save_path: Path to save the image
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        progress_callback: Optional callback for progress updates (current, total)
    
    Returns:
        True if download succeeded, False otherwise
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://harmony-scan.fr/",
    }
    
    # Clean URL
    url = url.strip()
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get('content-length', 0))
            
            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download and write
            downloaded = 0
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size:
                            progress_callback(downloaded, total_size)
            
            return True
            
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = (2 ** attempt) + 1
                time.sleep(wait_time)
            else:
                return False
    
    return False


def get_image_extension(url: str) -> str:
    """Extract image extension from URL."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        if ext in path:
            return ext
    
    return '.jpg'  # Default
