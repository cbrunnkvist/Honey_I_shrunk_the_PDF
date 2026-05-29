"""
PDF Image Compressor
Analyzes image dimensions in a PDF and compresses them based on a target specification.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from PIL import Image
import fitz  # PyMuPDF

def analyze_pdf_images(pdf_path: str) -> Optional[Dict[str, Any]]:
    """Extract and analyze all images in the PDF."""
    print(f"\nAnalyzing PDF: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    images_info: List[Dict[str, Any]] = []
    total_size = os.path.getsize(pdf_path)
    
    print(f"Total pages: {total_pages}")
    print(f"Current PDF file size: {total_size / (1024*1024):.2f} MB\n")
    
    # Extract images from PDF
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            
            # Get image dimensions
            width = pix.width
            height = pix.height
            size_bytes = len(pix.tobytes())
            
            images_info.append({
                'page': page_num + 1,
                'index': img_index,
                'width': width,
                'height': height,
                'size_kb': size_bytes / 1024,
                'xref': xref
            })
    
    doc.close()
    
    if not images_info:
        print("No images found in PDF.")
        return None
    
    # Print summary
    print(f"Found {len(images_info)} image(s):\n")
    print("Page | Index | Dimensions       | Size (KB)")
    print("-" * 50)
    
    total_image_size = 0.0
    max_width = 0
    
    for img in images_info:
        print(f"{img['page']:4d} | {img['index']:5d} | {img['width']:4d}x{img['height']:4d} | {img['size_kb']:8.1f}")
        total_image_size += img['size_kb']
        max_width = max(max_width, img['width'])
    
    print("-" * 50)
    print(f"{'Total image size:':45s} {total_image_size:.1f} KB")
    print(f"{'Max image width:':45s} {max_width} px")
    print(f"{'PDF file size:':45s} {total_size / (1024*1024):.2f} MB\n")
    
    return {
        'images': images_info,
        'total_image_size_kb': total_image_size,
        'total_pdf_size': total_size,
        'max_width': max_width,
        'total_pages': total_pages
    }

def get_target_from_user() -> Dict[str, Union[str, float, int]]:
    """Get compression target from user."""
    print("\n" + "="*60)
    print("COMPRESSION TARGET OPTIONS:")
    print("="*60)
    print("1. Max image width in pixels (e.g., 1500 for smaller, 2000 for quality)")
    print("2. Target file size in MB (e.g., 5 for 5MB final PDF)")
    print("\nExamples:")
    print("  - Type '1500' for max width of 1500px")
    print("  - Type '5MB' for target file size of 5MB")
    print("  - Type '10MB' for target file size of 10MB")
    print("-" * 60)
    
    while True:
        user_input = input("Enter target (pixels or MB): ").strip()
        
        if user_input.lower().endswith('mb'):
            try:
                target_mb = float(user_input[:-2].strip())
                return {'type': 'file_size', 'value_mb': target_mb}
            except ValueError:
                print("Invalid input. Please enter a number followed by 'MB'")
                continue
        else:
            try:
                target_width = int(user_input)
                if target_width > 0:
                    return {'type': 'max_width', 'value_px': target_width}
                else:
                    print("Width must be positive")
                    continue
            except ValueError:
                print("Invalid input. Please enter either a number or number+MB")
                continue

def calculate_compression_ratio(analysis: Dict[str, Any], target: Dict[str, Union[str, float, int]]) -> float:
    """Calculate what compression ratio is needed."""
    if target['type'] == 'max_width':
        # Simple ratio based on width
        current_max = float(analysis['max_width'])
        target_width = float(target['value_px'])
        ratio = target_width / current_max
        print(f"\nCompressing images: {current_max}px → {target_width}px")
        print(f"Compression ratio: {ratio:.2%}")
        return ratio
    else:
        # Based on file size
        current_size = float(analysis['total_pdf_size']) / (1024*1024)
        target_size = float(target['value_mb'])
        print(f"\nCompressing PDF: {current_size:.2f}MB → {target_size}MB")
        
        # Empirical: actual output ≈ 0.65 * target_size (PIL re-encoding adds overhead)
        # To reach target, multiply by ~1.54: zoom ≈ (target * 1.54 / 20) ^ 0.5
        compression_ratio = max(0.2, min(1.0, ((target_size * 1.54) / 20) ** 0.5))
        print(f"Estimated compression ratio: {compression_ratio:.2%}")
        return compression_ratio

def _pixmap_to_rgb_image(pix: fitz.Pixmap) -> Image.Image:
    if pix.colorspace is None or pix.colorspace.n != 3 or pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

def compress_pdf_phase1(input_path: str, output_path: str) -> str:
    """Phase 1: Convert non-JPEG images to JPEG format (same resolution)."""
    print(f"\nPhase 1: Converting images to JPEG format...")
    
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    print(f"Processing {total_pages} pages for format conversion...")
    resized_images: List[Image.Image] = []
    
    for page_num in range(total_pages):
        page = doc[page_num]
        
        # Render page at full resolution (zoom=1.0)
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), colorspace=fitz.csRGB, alpha=False)
        
        # Convert to PIL and re-encode as JPEG
        img = _pixmap_to_rgb_image(pix)
        resized_images.append(img)
        
        if (page_num + 1) % max(1, total_pages // 4) == 0:
            print(f"  Processed {page_num + 1}/{total_pages} pages")
    
    doc.close()
    
    # Save as PDF with high JPEG quality
    print(f"Saving with JPEG compression (quality=92)...")
    if resized_images:
        resized_images[0].save(
            output_path,
            save_all=True,
            append_images=resized_images[1:],
            format="PDF",
            quality=92,
            optimize=True
        )
    
    return output_path


def _jpeg_quality_for_target(target_size_mb: Optional[float]) -> int:
    if target_size_mb and target_size_mb >= 100:
        return 95
    if target_size_mb and target_size_mb >= 50:
        return 90
    if target_size_mb and target_size_mb >= 20:
        return 88
    return 85

def _render_pdf_as_jpeg_pdf(
    input_path: str,
    output_path: str,
    zoom: float,
    jpeg_quality: int,
) -> str:
    doc = fitz.open(input_path)
    total_pages = len(doc)
    resized_images: List[Image.Image] = []
    
    for page_num in range(total_pages):
        page = doc[page_num]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=False)
        img = _pixmap_to_rgb_image(pix)
        resized_images.append(img)
        
        if (page_num + 1) % max(1, total_pages // 4) == 0:
            print(f"  Processed {page_num + 1}/{total_pages} pages")
    
    doc.close()
    
    if resized_images:
        resized_images[0].save(
            output_path,
            save_all=True,
            append_images=resized_images[1:],
            format="PDF",
            quality=jpeg_quality,
            optimize=True,
        )
    
    return output_path

def _binary_search_target_size(
    input_path: str,
    output_path: str,
    target_size_mb: float,
    min_zoom: float,
    max_zoom: float,
    lower_ratio: float = 0.9,
    max_iters: int = 7,
) -> Tuple[str, float]:
    lower_bound = target_size_mb * lower_ratio
    upper_bound = target_size_mb
    jpeg_quality = _jpeg_quality_for_target(target_size_mb)
    best_path = ""
    best_size = 0.0
    temp_paths: List[str] = []
    low = min_zoom
    high = max_zoom
    
    for i in range(max_iters):
        zoom = (low + high) / 2
        temp_path = f"{Path(output_path).stem}_iter{i}.pdf"
        print(f"  Trying zoom={zoom:.4f}...")
        _render_pdf_as_jpeg_pdf(input_path, temp_path, zoom, jpeg_quality)
        temp_paths.append(temp_path)
        size_mb = os.path.getsize(temp_path) / (1024 * 1024)
        
        if size_mb <= upper_bound and size_mb > best_size:
            best_size = size_mb
            best_path = temp_path
        
        if lower_bound <= size_mb <= upper_bound:
            best_path = temp_path
            best_size = size_mb
            break
        
        if size_mb > upper_bound:
            high = zoom
        else:
            low = zoom
    
    if not best_path:
        best_path = temp_paths[-1]
        best_size = os.path.getsize(best_path) / (1024 * 1024)
    
    os.rename(best_path, output_path)
    for path in temp_paths:
        if path != output_path and path != best_path and os.path.exists(path):
            os.remove(path)
    
    return output_path, best_size

def compress_pdf_phase2(
    input_path: str,
    output_path: str,
    compression_ratio: float,
    target_size_mb: Optional[float] = None,
    min_zoom: float = 0.3,
) -> str:
    """Phase 2: Reduce resolution if file still exceeds target."""
    print(f"\nPhase 2: Reducing resolution (compression ratio: {compression_ratio:.2%})...")
    
    # Calculate zoom
    zoom = min(1.0, max(min_zoom, compression_ratio))
    jpeg_quality = _jpeg_quality_for_target(target_size_mb)
    
    print(f"Processing pages with dimension reduction (zoom={zoom:.3f})...")
    print(f"Saving with JPEG quality={jpeg_quality}...")
    _render_pdf_as_jpeg_pdf(input_path, output_path, zoom, jpeg_quality)
    
    return output_path

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python pdf_image_compressor.py <pdf_file> [target_width_px or target_MB]")
        print("\nExamples:")
        print("  python pdf_image_compressor.py 'SN Passport pages.pdf' 1000")
        print("  python pdf_image_compressor.py 'SN Passport pages.pdf' 15MB")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found")
        sys.exit(1)
    
    # Analyze current PDF
    analysis = analyze_pdf_images(pdf_file)
    
    if not analysis:
        sys.exit(1)
    
    # Get target from user or command line
    target: Dict[str, Union[str, float, int]]
    if len(sys.argv) >= 3:
        target_input = sys.argv[2]
        try:
            if target_input.lower().endswith('mb'):
                value_mb = float(target_input[:-2].strip())
                if value_mb <= 0:
                    raise ValueError("Target size must be positive")
                target = {'type': 'file_size', 'value_mb': value_mb}
            else:
                value_px = int(target_input)
                if value_px <= 0:
                    raise ValueError("Target width must be positive")
                target = {'type': 'max_width', 'value_px': value_px}
        except ValueError as exc:
            print(f"Error: invalid target '{target_input}'. {exc}")
            sys.exit(1)
    else:
        target = get_target_from_user()
    
    # Calculate compression ratio
    compression_ratio = calculate_compression_ratio(analysis, target)
    
    # Check if compression is actually needed
    if target['type'] == 'file_size':
        current_size_mb = float(analysis['total_pdf_size']) / (1024*1024)
        target_size_mb = float(target['value_mb'])
        if target_size_mb >= current_size_mb:
            print("\nTarget size meets or exceeds original - no compression performed.")
            print("No output file created; the original remains unchanged.")
            sys.exit(0)
    
    # Auto-proceed if target was provided via CLI, else confirm
    print("\n" + "="*60)
    if len(sys.argv) >= 3:
        print("Proceeding with compression...")
    else:
        confirm = input("Proceed with compression? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Generate output filename
    base_name = Path(pdf_file).stem
    output_file = f"{base_name}_compressed.pdf"
    
    print(f"\nOutput file: {output_file}")
    
    # Compress PDF - Two Phase Approach
    try:
        target_size = float(target['value_mb']) if target['type'] == 'file_size' else None
        original_size_mb = float(analysis['total_pdf_size']) / (1024*1024)
        
        # Phase 1: Format conversion to JPEG
        temp_file = f"{Path(pdf_file).stem}_phase1.pdf"
        compress_pdf_phase1(pdf_file, temp_file)
        phase1_size = os.path.getsize(temp_file) / (1024*1024)
        
        print(f"\nPhase 1 result: {original_size_mb:.2f} MB → {phase1_size:.2f} MB")
        
        # Check if we still need Phase 2
        if target['type'] == 'file_size' and phase1_size > target_size and target_size is not None:
            print(f"Still over target ({phase1_size:.2f} > {target_size:.2f}), applying Phase 2...")
            print("Adjusting zoom to land within 90-100% of target...")
            _binary_search_target_size(
                temp_file,
                output_file,
                target_size_mb=target_size,
                min_zoom=0.1,
                max_zoom=1.0,
            )
            output_size = os.path.getsize(output_file) / (1024 * 1024)
            os.remove(temp_file)
        elif target['type'] == 'max_width' and compression_ratio < 1.0:
            print("Applying Phase 2 to meet max width target...")
            compress_pdf_phase2(temp_file, output_file, compression_ratio, min_zoom=0.01)
            output_size = os.path.getsize(output_file) / (1024*1024)
            os.remove(temp_file)
        else:
            # Phase 1 was enough
            os.rename(temp_file, output_file)
            output_size = phase1_size
        
        # Show results
        print(f"\n" + "="*60)
        print("COMPRESSION COMPLETE")
        print("="*60)
        print(f"Original size: {original_size_mb:.2f} MB")
        print(f"Compressed size: {output_size:.2f} MB")
        print(f"Reduction: {(1 - output_size / original_size_mb) * 100:.1f}%")
        print(f"Output: {output_file}")
        print("="*60)
        
    except Exception as e:
        print(f"Error during compression: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
