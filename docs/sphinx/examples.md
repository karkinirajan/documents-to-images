# Advanced Examples

## Custom Conversion Workflows

### Multi-format Document Processing

```python
from doc_converter import DocumentConverter
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

converter = DocumentConverter()


def process_document_package(input_dir, output_dir):
    """Process a directory containing mixed document types."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    results = {"pdf_to_images": [], "docx_to_pdf": [], "pptx_to_pdf": [], "errors": []}

    # Process all files
    for file_path in input_path.iterdir():
        try:
            if file_path.suffix.lower() == ".pdf":
                # Convert PDF to images
                images = converter.pdf_to_images(
                    str(file_path), output_dir=str(output_path / "images"), format="jpeg", dpi=300
                )
                results["pdf_to_images"].extend(images)

            elif file_path.suffix.lower() == ".docx":
                # Convert DOCX to PDF
                pdf_path = converter.docx_to_pdf(
                    str(file_path), output_dir=str(output_path / "pdfs")
                )
                results["docx_to_pdf"].append(pdf_path)

            elif file_path.suffix.lower() == ".pptx":
                # Convert PPTX to PDF
                pdf_path = converter.pptx_to_pdf(
                    str(file_path), output_dir=str(output_path / "pdfs")
                )
                results["pptx_to_pdf"].append(pdf_path)

        except Exception as e:
            results["errors"].append({"file": str(file_path), "error": str(e)})
            logging.error(f"Error processing {file_path}: {e}")

    return results


# Usage
results = process_document_package("./input_docs", "./output")
print(f"Processed {len(results['pdf_to_images'])} PDF pages")
print(f"Converted {len(results['docx_to_pdf'])} DOCX files")
print(f"Converted {len(results['pptx_to_pdf'])} PPTX files")
print(f"Encountered {len(results['errors'])} errors")
```

### High-Quality PDF to Image Conversion

```python
from doc_converter import DocumentConverter
import os

converter = DocumentConverter()


def create_high_quality_images(pdf_path, output_dir, settings=None):
    """Create high-quality images from PDF with custom settings."""

    default_settings = {
        "format": "png",  # PNG for better quality
        "dpi": 600,  # High resolution
        "color_mode": "RGB",  # Full color
        "alpha": True,  # Transparency support
    }

    if settings:
        default_settings.update(settings)

    # Create output directory structure
    os.makedirs(f"{output_dir}/thumbnails", exist_ok=True)
    os.makedirs(f"{output_dir}/full_size", exist_ok=True)

    # Generate full-size images
    full_images = converter.pdf_to_images(
        pdf_path, output_dir=f"{output_dir}/full_size", **default_settings
    )

    # Generate thumbnails (lower DPI)
    thumbnail_settings = default_settings.copy()
    thumbnail_settings["dpi"] = 150

    thumbnails = converter.pdf_to_images(
        pdf_path, output_dir=f"{output_dir}/thumbnails", **thumbnail_settings
    )

    return {"full_images": full_images, "thumbnails": thumbnails}


# Usage
results = create_high_quality_images(
    "important_document.pdf", "./output/document_images", settings={"dpi": 800, "format": "png"}
)
```

### Automated Report Generation

```python
from doc_converter import DocumentConverter, BatchProcessor
from pathlib import Path
import yaml
from datetime import datetime


class ReportGenerator:
    def __init__(self, config_file=None):
        self.converter = DocumentConverter(config_file=config_file)
        self.batch_processor = BatchProcessor()

    def generate_monthly_reports(self, data_dir, output_dir):
        """Generate monthly reports from various document sources."""

        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_dir = Path(output_dir) / f"monthly_report_{timestamp}"
        report_dir.mkdir(parents=True, exist_ok=True)

        # Process different document types
        sections = {
            "financial": {"pattern": "*financial*.docx", "format": "pdf"},
            "operations": {"pattern": "*operations*.pptx", "format": "pdf"},
            "analytics": {"pattern": "*analytics*.html", "format": "pdf"},
        }

        report_summary = {}

        for section, config in sections.items():
            section_dir = report_dir / section
            section_dir.mkdir(exist_ok=True)

            # Batch convert files for this section
            if config["format"] == "pdf":
                if config["pattern"].endswith(".docx"):
                    operation = "docx_to_pdf"
                elif config["pattern"].endswith(".pptx"):
                    operation = "pptx_to_pdf"
                elif config["pattern"].endswith(".html"):
                    operation = "html_to_pdf"

                results = self.batch_processor.batch_convert(
                    input_dir=data_dir,
                    output_dir=str(section_dir),
                    operation=operation,
                    pattern=config["pattern"],
                )

                report_summary[section] = {
                    "processed": len(results["successful"]),
                    "errors": len(results["failed"]),
                    "files": results["successful"],
                }

        # Generate summary report
        self._generate_summary_report(report_summary, report_dir)

        return report_dir

    def _generate_summary_report(self, summary, output_dir):
        """Generate a summary HTML report."""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Monthly Report Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                .stats {{ background-color: #f5f5f5; padding: 10px; }}
            </style>
        </head>
        <body>
            <h1>Monthly Report Summary</h1>
            <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        """

        for section, data in summary.items():
            html_content += f"""
            <div class="section">
                <h2>{section.title()}</h2>
                <div class="stats">
                    <p>Files Processed: {data["processed"]}</p>
                    <p>Errors: {data["errors"]}</p>
                </div>
                <h3>Processed Files:</h3>
                <ul>
            """

            for file_path in data["files"]:
                html_content += f"<li>{Path(file_path).name}</li>"

            html_content += "</ul></div>"

        html_content += """
        </body>
        </html>
        """

        # Save HTML report
        summary_path = output_dir / "summary.html"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Convert to PDF
        pdf_path = self.converter.html_to_pdf(str(summary_path), str(output_dir / "summary.pdf"))

        return pdf_path


# Usage
generator = ReportGenerator("report_config.yaml")
report_dir = generator.generate_monthly_reports("./data", "./reports")
print(f"Report generated in: {report_dir}")
```

### Web Scraping to PDF Archive

```python
import requests
from bs4 import BeautifulSoup
from doc_converter import DocumentConverter
from urllib.parse import urljoin, urlparse
import time
import logging


class WebArchiver:
    def __init__(self, delay=1):
        self.converter = DocumentConverter()
        self.delay = delay  # Delay between requests
        self.session = requests.Session()

        # Set up headers to mimic browser
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    def archive_website_section(self, base_url, output_dir, max_pages=10):
        """Archive multiple pages from a website to PDF."""

        archived_urls = set()
        pdf_files = []

        def get_links(url):
            """Extract links from a webpage."""
            try:
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                links = []
                for link in soup.find_all("a", href=True):
                    absolute_url = urljoin(url, link["href"])
                    if self._is_same_domain(base_url, absolute_url):
                        links.append(absolute_url)

                return links

            except Exception as e:
                logging.error(f"Error getting links from {url}: {e}")
                return []

        # Start with base URL
        urls_to_process = [base_url]

        while urls_to_process and len(archived_urls) < max_pages:
            current_url = urls_to_process.pop(0)

            if current_url in archived_urls:
                continue

            try:
                # Generate safe filename
                parsed_url = urlparse(current_url)
                filename = f"{parsed_url.netloc}_{parsed_url.path.replace('/', '_')}.pdf"
                filename = "".join(c for c in filename if c.isalnum() or c in "._-")
                output_path = f"{output_dir}/{filename}"

                # Convert to PDF
                self.converter.html_to_pdf(current_url, output_path)
                pdf_files.append(output_path)
                archived_urls.add(current_url)

                logging.info(f"Archived: {current_url}")

                # Get links for further processing
                if len(archived_urls) < max_pages:
                    new_links = get_links(current_url)
                    urls_to_process.extend(
                        [
                            link
                            for link in new_links
                            if link not in archived_urls and link not in urls_to_process
                        ]
                    )

                # Rate limiting
                time.sleep(self.delay)

            except Exception as e:
                logging.error(f"Error archiving {current_url}: {e}")

        return pdf_files

    def _is_same_domain(self, base_url, url):
        """Check if URL is from the same domain."""
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain


# Usage
archiver = WebArchiver(delay=2)  # 2-second delay between requests
pdf_files = archiver.archive_website_section(
    "https://example.com/docs", "./website_archive", max_pages=20
)
print(f"Archived {len(pdf_files)} pages to PDF")
```

## Performance Optimization

### Parallel Processing Example

```python
from doc_converter import BatchProcessor
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import os
from pathlib import Path


class OptimizedBatchProcessor:
    def __init__(self, max_workers=None):
        self.batch_processor = BatchProcessor()
        self.max_workers = max_workers or os.cpu_count()

    def parallel_pdf_to_images(self, pdf_files, output_dir, **kwargs):
        """Process multiple PDF files in parallel."""

        def process_single_pdf(pdf_path):
            try:
                converter = DocumentConverter()
                return converter.pdf_to_images(pdf_path, output_dir=output_dir, **kwargs)
            except Exception as e:
                return {"error": str(e), "file": pdf_path}

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pdf = {executor.submit(process_single_pdf, pdf): pdf for pdf in pdf_files}

            for future in future_to_pdf:
                result = future.result()
                results.append(result)

        return results


# Usage
processor = OptimizedBatchProcessor(max_workers=4)
pdf_files = list(Path("./pdfs").glob("*.pdf"))
results = processor.parallel_pdf_to_images(pdf_files, "./images", format="jpeg", dpi=300)
```

## Error Handling and Monitoring

### Comprehensive Error Handling

```python
from doc_converter import DocumentConverter, ConversionError
import logging
from pathlib import Path
import traceback


class RobustConverter:
    def __init__(self, retry_attempts=3):
        self.converter = DocumentConverter()
        self.retry_attempts = retry_attempts
        self.setup_logging()

    def setup_logging(self):
        """Set up comprehensive logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("converter.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def safe_convert(self, operation, *args, **kwargs):
        """Safely perform conversion with retry logic."""

        for attempt in range(self.retry_attempts):
            try:
                result = operation(*args, **kwargs)
                self.logger.info(f"Conversion successful: {operation.__name__}")
                return {"success": True, "result": result}

            except ConversionError as e:
                self.logger.error(f"Conversion error (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    return {"success": False, "error": str(e), "error_type": "ConversionError"}

            except FileNotFoundError as e:
                self.logger.error(f"File not found: {e}")
                return {"success": False, "error": str(e), "error_type": "FileNotFoundError"}

            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                self.logger.debug(traceback.format_exc())
                if attempt == self.retry_attempts - 1:
                    return {"success": False, "error": str(e), "error_type": "UnexpectedError"}


# Usage
robust_converter = RobustConverter(retry_attempts=3)
result = robust_converter.safe_convert(
    robust_converter.converter.pdf_to_images, "document.pdf", format="jpeg", dpi=300
)

if result["success"]:
    print(f"Generated {len(result['result'])} images")
else:
    print(f"Conversion failed: {result['error']}")
```