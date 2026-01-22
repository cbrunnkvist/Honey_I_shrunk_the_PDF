uv run pdf_image_compressor.py 'tests/Scanned Document.pdf' 100MB
seq 10 -1 1 | xargs -n1 -I{} sh -c "uv run pdf_image_compressor.py 'tests/Scanned Document.pdf' {}MB ; mv 'Scanned Document_compressed.pdf' 'Scanned Document_compressed_target_{}.pdf'"
