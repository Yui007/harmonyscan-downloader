"""
HarmonyScan Downloader - Configuration Management
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Literal


CONFIG_FILE = Path(__file__).parent / "config.json"

@dataclass
class Config:
    """Application configuration with defaults."""
    download_dir: str = "./downloads"
    output_format: Literal["images", "pdf", "cbz"] = "images"
    keep_images: bool = True
    max_concurrent_chapters: int = 3
    max_concurrent_images: int = 5
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file or create default."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
    
    def get_download_path(self) -> Path:
        """Get download directory as Path, creating if needed."""
        path = Path(self.download_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global config instance
config = Config.load()
