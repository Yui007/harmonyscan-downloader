<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Playwright-Async-green.svg" alt="Playwright">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/github/stars/Yui007/harmonyscan-downloader?style=social" alt="Stars">
</p>

<h1 align="center">
  <br>
  🎨 HarmonyScan Downloader
  <br>
</h1>

<h4 align="center">A beautiful, modern CLI manga downloader for <a href="https://harmony-scan.fr" target="_blank">harmony-scan.fr</a></h4>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## ✨ Features

- 🚀 **Concurrent Downloads** - Download multiple chapters simultaneously using async Playwright
- 🎯 **Smart Retry Logic** - Automatic retry with exponential backoff for failed downloads
- 📦 **Multiple Output Formats** - Save as raw images, PDF, or CBZ (comic book archive)
- 🎨 **Beautiful CLI** - Rich terminal interface with progress bars, colors, and styled panels
- ⚡ **Fast Image Downloads** - Threaded image downloads with configurable concurrency
- 💾 **Persistent Settings** - Save your preferences in a JSON config file
- 🔄 **Interactive & CLI Modes** - Use interactively or via command-line arguments

## 📸 Preview

```
╔═══════════════════════════════════════════════════════════════════╗
║   ██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ ██████╗ ███╗   ██╗██╗   ██╗ ║
║   ██║  ██║██╔══██╗██╔══██╗████╗ ████║██╔═══██╗████╗  ██║╚██╗ ██╔╝ ║
║   ███████║███████║██████╔╝██╔████╔██║██║   ██║██╔██╗ ██║ ╚████╔╝  ║
║   ██╔══██║██╔══██║██╔══██╗██║╚██╔╝██║██║   ██║██║╚██╗██║  ╚██╔╝   ║
║   ██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║   ██║    ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    ║
║                      SCAN DOWNLOADER                              ║
╚═══════════════════════════════════════════════════════════════════╝
```

## 🔧 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yui007/harmonyscan-downloader.git
   cd harmonyscan-downloader
   ```

2. **Create a virtual environment** (Recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## 🚀 Usage

### Interactive Mode

Simply run without arguments to start the interactive menu:

```bash
python main.py
```

You'll be greeted with a beautiful menu where you can:
- Enter a manga URL
- Select chapters (single, range, or all)
- Choose output format (images, PDF, CBZ)
- Configure settings

### Command-Line Mode

For quick downloads, use the `download` command:

```bash
# Download all chapters as images
python main.py download "https://harmony-scan.fr/manga/your-manga/"

# Download chapters 1-10 as PDF
python main.py download "https://harmony-scan.fr/manga/your-manga/" -c 1-10 -f pdf

# Download chapter 5 as CBZ, keep original images
python main.py download "https://harmony-scan.fr/manga/your-manga/" -c 5 -f cbz -k

# Specify custom output directory
python main.py download "https://harmony-scan.fr/manga/your-manga/" -o ./my-manga
```

### Available Options

| Option | Short | Description |
|--------|-------|-------------|
| `--chapters` | `-c` | Chapters to download: `all`, single number, or range (e.g., `1-10`) |
| `--format` | `-f` | Output format: `images`, `pdf`, or `cbz` |
| `--keep-images` | `-k` | Keep original images after conversion |
| `--output` | `-o` | Custom output directory |

### Configuration Commands

```bash
# Show current configuration
python main.py config --show

# Reset configuration to defaults
python main.py config --reset
```

## ⚙️ Configuration

Settings are stored in `config.json` and can be modified via the interactive menu or directly:

| Setting | Default | Description |
|---------|---------|-------------|
| `download_dir` | `./downloads` | Default download directory |
| `output_format` | `images` | Default format: `images`, `pdf`, `cbz` |
| `keep_images` | `true` | Keep images after PDF/CBZ conversion |
| `max_concurrent_chapters` | `3` | Parallel chapter downloads |
| `max_concurrent_images` | `5` | Parallel image downloads per chapter |

## 🏗️ Architecture

```
harmonyscan-downloader/
├── main.py                      # Typer CLI entry point
├── config.py                    # Configuration management
├── requirements.txt             # Dependencies
├── downloads/                   # Default download directory
└── src/
    ├── cli/
    │   ├── app.py               # Main application logic
    │   ├── display.py           # Rich UI components
    │   └── prompts.py           # Interactive prompts
    ├── scraper/
    │   ├── selectors.py         # CSS selectors
    │   └── manga.py             # Async Playwright scraper
    ├── downloader/
    │   ├── image.py             # Image download worker
    │   └── manager.py           # Download orchestration
    └── converters/
        ├── pdf.py               # PDF conversion
        └── cbz.py               # CBZ conversion
```

### Key Technologies

- **[Playwright](https://playwright.dev/python/)** - Async browser automation for scraping
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal UI
- **[Typer](https://typer.tiangolo.com/)** - Modern CLI framework
- **[asyncio](https://docs.python.org/3/library/asyncio.html)** - Concurrent chapter fetching
- **[ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html)** - Parallel image downloads
- **[Pillow](https://pillow.readthedocs.io/)** - Image processing
- **[img2pdf](https://pypi.org/project/img2pdf/)** - Lossless PDF conversion

## 🔄 How It Works

1. **Manga Info Fetching** - Playwright navigates to the manga page and extracts metadata (title, authors, genres, chapters)

2. **Concurrent Chapter Scraping** - Using `asyncio.gather()`, multiple chapter pages are scraped simultaneously to get image URLs

3. **Threaded Image Downloads** - Images are downloaded using `ThreadPoolExecutor` with retry logic and exponential backoff

4. **Format Conversion** - Optionally convert downloaded images to PDF or CBZ format

5. **Progress Reporting** - Real-time progress bars show download status for each chapter

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/Yui007/harmonyscan-downloader.git
cd harmonyscan-downloader
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run in development
python main.py
```

### Project Dependencies

- `playwright` - Browser automation
- `rich` - Terminal formatting
- `typer` - CLI framework
- `Pillow` - Image processing
- `img2pdf` - PDF conversion
- `requests` - HTTP client for image downloads

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please respect the website's terms of service and support the creators by visiting the official website.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Yui007">Yui007</a>
</p>

<p align="center">
  <a href="https://github.com/Yui007/harmonyscan-downloader/issues">Report Bug</a> •
  <a href="https://github.com/Yui007/harmonyscan-downloader/issues">Request Feature</a>
</p>
