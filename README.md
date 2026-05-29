# pdf-image-compressor

Compress PDF files by re-encoding embedded images and optionally reducing their
resolution. Best suited for scanned documents or image-heavy PDFs.

## Usage

Requires [uv](https://docs.astral.sh/uv/).

```bash
# Local checkout
uvx --from . pdf-image-compressor "scan.pdf" 1500
uvx --from . pdf-image-compressor "scan.pdf" 5MB

# After publishing to PyPI
uvx pdf-image-compressor "scan.pdf" 1500
```

Targets: max image width in pixels (e.g. `1500`) or target file size (e.g. `5MB`).
Output: `<input>_compressed.pdf` in the same directory.

## Development

```bash
uv sync
uv run python pdf_image_compressor.py <pdf_path> [target]
uv run python -m unittest tests/test_pdf_image_compressor.py
```

## License
MIT. See `LICENSE`.
