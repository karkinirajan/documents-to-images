"""
Command-line interface for document converter.
"""

import argparse
import logging
import sys
from pathlib import Path

from ..core.batch_processor import BatchProcessor
from ..core.document_converter import DocumentConverter

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def progress_callback(current: int, total: int, filename: str = "") -> None:
    """Progress callback for batch operations."""
    percentage = (current / total) * 100
    print(
        f"\rProgress: {current}/{total} ({percentage:.1f}%) - {filename}",
        end="",
        flush=True,
    )
    if current == total:
        print()  # New line when complete


def convert_pdf_to_images(args: argparse.Namespace) -> None:
    """Convert PDF to images command."""
    converter = DocumentConverter()

    try:
        output_files = converter.pdf_to_images(
            pdf_path=args.input,
            output_dir=args.output_dir,
            format=args.format,
            dpi=args.dpi,
        )

        print(f"✅ Successfully converted PDF to {len(output_files)} images")
        default_dir = Path(args.input).with_name(f"{Path(args.input).stem}_images")
        print(f"📁 Output directory: {args.output_dir or default_dir}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def convert_docx_to_pdf(args: argparse.Namespace) -> None:
    """Convert DOCX to PDF command."""
    converter = DocumentConverter()

    try:
        output_file = converter.docx_to_pdf(docx_path=args.input, output_path=args.output)

        print("✅ Successfully converted DOCX to PDF")
        print(f"📄 Output file: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def convert_pptx_to_pdf(args: argparse.Namespace) -> None:
    """Convert PPTX to PDF command."""
    converter = DocumentConverter()

    try:
        output_file = converter.pptx_to_pdf(pptx_path=args.input, output_path=args.output)

        print("✅ Successfully converted PPTX to PDF")
        print(f"📄 Output file: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def convert_txt_to_pdf(args: argparse.Namespace) -> None:
    """Convert TXT to PDF command."""
    converter = DocumentConverter()

    try:
        output_file = converter.txt_to_pdf(txt_path=args.input, output_path=args.output)

        print("✅ Successfully converted TXT to PDF")
        print(f"📄 Output file: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def convert_html_to_pdf(args: argparse.Namespace) -> None:
    """Convert HTML to PDF command."""
    converter = DocumentConverter()

    try:
        output_file = converter.html_to_pdf(
            html_source=args.input,
            output_path=args.output,
            options=getattr(args, "options", None),
        )

        print("✅ Successfully converted HTML to PDF")
        print(f"📄 Output file: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def convert_docx_to_html(args: argparse.Namespace) -> None:
    """Convert DOCX to HTML command."""
    converter = DocumentConverter()

    try:
        output_file = converter.docx_to_html(docx_path=args.input, output_path=args.output)

        print("✅ Successfully converted DOCX to HTML")
        print(f"📄 Output file: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def batch_convert(args: argparse.Namespace) -> None:
    """Batch convert command."""
    processor = BatchProcessor(max_workers=args.workers)

    try:
        print("🚀 Starting batch conversion...")
        print(f"📂 Input: {args.input_dir}")
        print(f"📁 Output: {args.output_dir}")
        print(f"🎯 Target format: {args.format}")

        results = processor.convert_directory(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            target_format=args.format,
            file_patterns=args.patterns,
            recursive=args.recursive,
            progress_callback=progress_callback,
        )

        print("\n📊 Batch conversion completed:")
        print(f"   ✅ Successful: {results['successful']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📈 Total: {results['total_files']}")

        if results["errors"]:
            print("\n❌ Errors:")
            for error in results["errors"]:
                print(f"   - {error['file']}: {error['error']}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    """Main CLI entry point. ``argv`` defaults to ``sys.argv[1:]``."""
    parser = argparse.ArgumentParser(
        description=("Document Converter - Convert documents between various formats"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDF to images
  python -m doc_converter pdf-to-images document.pdf \\
    --output-dir ./images --format jpeg --dpi 300

  # Convert DOCX to PDF
  python -m doc_converter docx-to-pdf document.docx --output document.pdf

  # Convert HTML to PDF
  python -m doc_converter html-to-pdf https://example.com --output webpage.pdf

  # Batch convert directory
  python -m doc_converter batch-convert --input-dir ./docs \\
    --output-dir ./converted --format pdf
        """,
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # PDF to images
    pdf_to_img_parser = subparsers.add_parser("pdf-to-images", help="Convert PDF to images")
    pdf_to_img_parser.add_argument("input", help="Input PDF file")
    pdf_to_img_parser.add_argument("--output-dir", "-o", help="Output directory for images")
    pdf_to_img_parser.add_argument(
        "--format",
        "-f",
        choices=["jpeg", "png"],
        default="jpeg",
        help="Output format",
    )
    pdf_to_img_parser.add_argument("--dpi", type=int, default=200, help="Resolution in DPI")
    pdf_to_img_parser.set_defaults(func=convert_pdf_to_images)

    # DOCX to PDF
    docx_to_pdf_parser = subparsers.add_parser("docx-to-pdf", help="Convert DOCX to PDF")
    docx_to_pdf_parser.add_argument("input", help="Input DOCX file")
    docx_to_pdf_parser.add_argument("--output", "-o", help="Output PDF file")
    docx_to_pdf_parser.set_defaults(func=convert_docx_to_pdf)

    # PPTX to PDF
    pptx_to_pdf_parser = subparsers.add_parser("pptx-to-pdf", help="Convert PPTX to PDF")
    pptx_to_pdf_parser.add_argument("input", help="Input PPTX file")
    pptx_to_pdf_parser.add_argument("--output", "-o", help="Output PDF file")
    pptx_to_pdf_parser.set_defaults(func=convert_pptx_to_pdf)

    # TXT to PDF
    txt_to_pdf_parser = subparsers.add_parser("txt-to-pdf", help="Convert TXT to PDF")
    txt_to_pdf_parser.add_argument("input", help="Input TXT file")
    txt_to_pdf_parser.add_argument("--output", "-o", help="Output PDF file")
    txt_to_pdf_parser.set_defaults(func=convert_txt_to_pdf)

    # HTML to PDF
    html_to_pdf_parser = subparsers.add_parser("html-to-pdf", help="Convert HTML to PDF")
    html_to_pdf_parser.add_argument("input", help="Input HTML file or URL")
    html_to_pdf_parser.add_argument("--output", "-o", required=True, help="Output PDF file")
    html_to_pdf_parser.set_defaults(func=convert_html_to_pdf)

    # DOCX to HTML
    docx_to_html_parser = subparsers.add_parser("docx-to-html", help="Convert DOCX to HTML")
    docx_to_html_parser.add_argument("input", help="Input DOCX file")
    docx_to_html_parser.add_argument("--output", "-o", help="Output HTML file")
    docx_to_html_parser.set_defaults(func=convert_docx_to_html)

    # Batch convert
    batch_parser = subparsers.add_parser("batch-convert", help="Batch convert files")
    batch_parser.add_argument("--input-dir", "-i", required=True, help="Input directory")
    batch_parser.add_argument("--output-dir", "-o", required=True, help="Output directory")
    batch_parser.add_argument(
        "--format",
        "-f",
        required=True,
        choices=["pdf", "html", "jpeg", "png"],
        help="Target format",
    )
    batch_parser.add_argument(
        "--patterns",
        nargs="+",
        help="File patterns to include (e.g., *.docx *.pdf)",
    )
    batch_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Process subdirectories"
    )
    batch_parser.add_argument(
        "--workers", "-w", type=int, default=4, help="Number of worker threads"
    )
    batch_parser.set_defaults(func=batch_convert)

    # Parse arguments
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    # Run command
    args.func(args)


if __name__ == "__main__":
    main()
