# Project: pdf-image-compressor

## Overview
This project provides a Python tool to compress PDF files by analyzing and resizing/re-encoding embedded images. The output is a rasterized PDF (pages re-rendered as images), so it is particularly useful for scanned documents or image-heavy PDFs.

The core logic resides in `pdf_image_compressor.py`, which:
1.  Analyzes the PDF to determine current image statistics.
2.  Accepts a target compression metric (either maximum image width in pixels or a target file size in MB).
3.  Executes a two-phase compression strategy:
    *   **Phase 1:** Converts images to JPEG format (quality 92) to reduce size without significant resolution loss.
    *   **Phase 2:** Reduces the image resolution based on a calculated compression ratio (file size target or max width target). For file-size targets, it iteratively adjusts resolution to land within 90-100% of the target when possible.

Note: Phase 1 JPEG re-encoding alone can dramatically shrink files (even before any downscaling), depending on the source format.

## Tech Stack
*   **Language:** Python (>=3.9)
*   **Dependencies used by the code:**
    *   `PyMuPDF` (fitz): PDF parsing, rendering, and image extraction.
    *   `Pillow` (PIL): Image re-encoding and PDF output.
*   **Other dependencies in `pyproject.toml`:**
    *   `pdf2image`, `pypdf` (currently unused).
*   **Package/Build System:** `hatchling` (backend). `uv` is optional but recommended.

## Setup & Usage

### Prerequisites
*   Python 3.9 or higher.
*   `uv` is optional for dependency management and running tests.

### Installation
```bash
uv sync
```

### Running the Compressor
`uv run` is recommended to ensure the correct environment:

**Basic Syntax:**
```bash
uv run python pdf_image_compressor.py <pdf_file_path> [target]
```

**Examples:**
1.  **Compress by Target Width (pixels):**
    ```bash
    uv run python pdf_image_compressor.py "my_document.pdf" 1500
    ```

2.  **Compress by Target File Size (MB):**
    ```bash
    uv run python pdf_image_compressor.py "scan.pdf" 5MB
    ```

### Running Tests
Execute the test suite (with `uv` or your active environment):
```bash
uv run python -m unittest test_pdf_image_compressor.py
```

## Development

### Project Structure
*   `pdf_image_compressor.py`: Main script containing all logic.
*   `pyproject.toml`: Project configuration and dependencies.
*   `uv.lock`: Dependency lock file.

### Conventions
*   **Code Style:** Follows standard Python (PEP 8) conventions.
*   **Comments:** Docstrings are used for functions to explain purpose and logic.
*   **Type Hinting:** Present on most functions for maintainability.
*   **Testing:** Unit and functional tests included in `tests/test_pdf_image_compressor.py`.
*   **Error Handling:** Basic error handling is implemented for file existence and input validation.
