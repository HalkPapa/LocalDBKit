"""
PDF Processor
Extracts text, images, and metadata from PDF files
"""
import fitz  # PyMuPDF
from typing import Dict, Any, List
import logging
import io

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processes PDF files and extracts content"""

    async def process_pdf(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF

        Args:
            pdf_data: PDF file bytes

        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            # Open PDF
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

            # Extract metadata
            metadata = pdf_document.metadata

            # Extract text from all pages
            pages = []
            total_text = []

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text = page.get_text()

                pages.append({
                    "page_number": page_num + 1,
                    "text": text.strip(),
                    "word_count": len(text.split()),
                })
                total_text.append(text)

            pdf_document.close()

            return {
                "metadata": {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                },
                "page_count": len(pages),
                "pages": pages,
                "full_text": "\n\n".join(total_text).strip(),
                "total_word_count": sum(p["word_count"] for p in pages),
            }

        except Exception as e:
            logger.error(f"PDF processing error: {e}")
            raise

    async def extract_images(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Extract images from PDF

        Args:
            pdf_data: PDF file bytes

        Returns:
            Dictionary with extracted images
        """
        try:
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

            images = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)

                    images.append({
                        "page_number": page_num + 1,
                        "image_index": img_index,
                        "width": base_image["width"],
                        "height": base_image["height"],
                        "colorspace": base_image["colorspace"],
                        "ext": base_image["ext"],
                        "size_bytes": len(base_image["image"]),
                    })

            pdf_document.close()

            return {
                "image_count": len(images),
                "images": images,
            }

        except Exception as e:
            logger.error(f"PDF image extraction error: {e}")
            raise

    async def extract_tables(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Extract table structures from PDF

        Args:
            pdf_data: PDF file bytes

        Returns:
            Dictionary with table data
        """
        try:
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

            tables = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Get tables using PyMuPDF's table extraction
                tabs = page.find_tables()

                for tab_index, tab in enumerate(tabs):
                    if tab.header:
                        tables.append({
                            "page_number": page_num + 1,
                            "table_index": tab_index,
                            "row_count": tab.row_count,
                            "col_count": tab.col_count,
                            "bbox": tab.bbox,
                        })

            pdf_document.close()

            return {
                "table_count": len(tables),
                "tables": tables,
            }

        except Exception as e:
            logger.error(f"PDF table extraction error: {e}")
            raise
