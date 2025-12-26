"""
HarmonyScan Downloader - CBZ Converter
Convert chapter images to CBZ (Comic Book ZIP) format
"""

import zipfile
from pathlib import Path
from typing import List, Optional


def get_image_files(directory: Path) -> List[Path]:
    """Get sorted list of image files from directory."""
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    images = []
    
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            images.append(file)
    
    # Sort by filename
    images.sort(key=lambda x: x.stem)
    return images


def convert_to_cbz(
    image_dir: Path,
    output_path: Optional[Path] = None,
    delete_images: bool = False
) -> Optional[Path]:
    """
    Convert all images in a directory to a CBZ archive.
    
    Args:
        image_dir: Directory containing images
        output_path: Optional output CBZ path. If None, uses directory name.
        delete_images: If True, delete source images after conversion
    
    Returns:
        Path to created CBZ, or None on failure
    """
    images = get_image_files(image_dir)
    
    if not images:
        return None
    
    # Determine output path
    if output_path is None:
        output_path = image_dir.parent / f"{image_dir.name}.cbz"
    
    try:
        # Create CBZ (ZIP archive with .cbz extension)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
            for img_path in images:
                # Add with just the filename, not the full path
                cbz.write(img_path, img_path.name)
        
        # Delete source images if requested
        if delete_images:
            for img_path in images:
                try:
                    img_path.unlink()
                except:
                    pass
        
        return output_path
        
    except Exception as e:
        return None


def batch_convert_to_cbz(
    chapter_dirs: List[Path],
    delete_images: bool = False
) -> List[tuple[Path, Optional[Path]]]:
    """
    Convert multiple chapter directories to CBZ archives.
    
    Args:
        chapter_dirs: List of directories containing chapter images
        delete_images: If True, delete source images after conversion
    
    Returns:
        List of tuples (chapter_dir, cbz_path or None)
    """
    results = []
    
    for chapter_dir in chapter_dirs:
        cbz_path = convert_to_cbz(chapter_dir, delete_images=delete_images)
        results.append((chapter_dir, cbz_path))
    
    return results
