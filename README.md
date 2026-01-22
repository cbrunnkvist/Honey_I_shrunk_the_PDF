# pdf-image-compressor

Compress PDF files by re-encoding embedded images and optionally reducing their
resolution. The output is a rasterized PDF (pages are re-rendered as images),
best suited for scanned documents or image-heavy PDFs. Note: Phase 1 JPEG
re-encoding alone can dramatically shrink files (even before any downscaling).

## Requirements
- Python 3.9+
- Optional: `uv` for dependency management

## Install
```bash
uv sync
```

## Usage
```bash
uv run python pdf_image_compressor.py <pdf_path> [target]
```

Targets:
- Max image width in pixels (e.g., `1500`)
- Target file size in MB (e.g., `5MB`)

Examples:
```bash
uv run python pdf_image_compressor.py "Scanned Document.pdf" 1500
uv run python pdf_image_compressor.py "Scanned Document.pdf" 5MB
```

Output is written to `<input>_compressed.pdf` in the same directory.
For file-size targets, the tool iteratively adjusts resolution to land within
90-100% of the target when possible.

## Tests
```bash
uv run python -m unittest tests/test_pdf_image_compressor.py
```

## License
MIT. See `LICENSE`.
