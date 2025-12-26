"""
HarmonyScan Downloader - PDF Converter
Convert chapter images to PDF format
"""

import img2pdf
from pathlib import Path
from typing import List, Optional
from PIL import Image
import io


def get_image_files(directory: Path) -> List[Path]:
    """Get sorted list of image files from directory."""
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    images = []
    
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            images.append(file)
    
    # Sort by filename (assuming numeric naming like 001.jpg, 002.jpg)
    images.sort(key=lambda x: x.stem)
    return images


def convert_image_for_pdf(image_path: Path) -> bytes:
    """
    Convert an image to JPEG bytes suitable for PDF.
    Handles formats like WebP that img2pdf may not support directly.
    """
    with Image.open(image_path) as img:
        # Convert to RGB if necessary (for PNG with alpha, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        return buffer.getvalue()


def convert_to_pdf(
    image_dir: Path,
    output_path: Optional[Path] = None,
    delete_images: bool = False
) -> Optional[Path]:
    """
    Convert all images in a directory to a single PDF.
    
    Args:
        image_dir: Directory containing images
        output_path: Optional output PDF path. If None, uses directory name.
        delete_images: If True, delete source images after conversion
    
    Returns:
        Path to created PDF, or None on failure
    """
    images = get_image_files(image_dir)
    
    if not images:
        return None
    
    # Determine output path
    if output_path is None:
        output_path = image_dir.parent / f"{image_dir.name}.pdf"
    
    try:
        # Convert all images to PDF-compatible format
        image_bytes = []
        for img_path in images:
            try:
                # First try direct img2pdf (faster for JPEGs)
                with open(img_path, 'rb') as f:
                    data = f.read()
                # Test if img2pdf can handle it
                try:
                    img2pdf.get_imgmetadata(data)
                    image_bytes.append(data)
                except img2pdf.ImageOpenError:
                    # Convert via PIL
                    image_bytes.append(convert_image_for_pdf(img_path))
            except Exception:
                # Convert via PIL as fallback
                image_bytes.append(convert_image_for_pdf(img_path))
        
        # Create PDF
        pdf_bytes = img2pdf.convert(image_bytes)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
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


def batch_convert_to_pdf(
    chapter_dirs: List[Path],
    delete_images: bool = False
) -> List[tuple[Path, Optional[Path]]]:
    """
    Convert multiple chapter directories to PDFs.
    
    Args:
        chapter_dirs: List of directories containing chapter images
        delete_images: If True, delete source images after conversion
    
    Returns:
        List of tuples (chapter_dir, pdf_path or None)
    """
    results = []
    
    for chapter_dir in chapter_dirs:
        pdf_path = convert_to_pdf(chapter_dir, delete_images=delete_images)
        results.append((chapter_dir, pdf_path))
    
    return results
