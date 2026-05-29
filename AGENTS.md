# Project: pdf-image-compressor

## Overview
Compresses PDF files by re-encoding embedded images and optionally reducing resolution.
Output is a rasterized PDF (pages re-rendered as images), best for scanned/image-heavy PDFs.

Core logic in `pdf_image_compressor.py`:
1. Analyzes the PDF to determine current image statistics.
2. Accepts a target: max image width in pixels, or target file size in MB.
3. Two-phase compression:
   - **Phase 1:** Converts images to JPEG (quality 92) — often enough on its own.
   - **Phase 2:** Reduces resolution via binary search to land within 90-100% of file-size targets.

## Tech Stack
*   **Language:** Python (>=3.9)
*   **Dependencies:** `PyMuPDF` (fitz), `Pillow` (PIL)
*   **Build:** `hatchling`. `uv` recommended.

## Running

### Zero-install
```bash
uvx --from . pdf-image-compressor <pdf_file_path> [target]
```

After publishing to PyPI:
```bash
uvx pdf-image-compressor <pdf_file_path> [target]
```

### Development
```bash
uv sync
uv run python pdf_image_compressor.py <pdf_file_path> [target]
```

### Tests
```bash
uv run python -m unittest tests/test_pdf_image_compressor.py
```
