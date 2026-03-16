"""
OCR Processor
Extracts text from images using Tesseract OCR
"""
from PIL import Image
import pytesseract
from typing import Dict, Any
import logging
import io

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Processes images and extracts text using OCR"""

    def __init__(self, lang: str = "eng+jpn"):
        """
        Initialize OCR Processor

        Args:
            lang: Language(s) for OCR (default: English + Japanese)
        """
        self.lang = lang

    async def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract text from image

        Args:
            image_data: Image file bytes

        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))

            # Extract text
            text = pytesseract.image_to_string(image, lang=self.lang)

            # Get detailed data
            data = pytesseract.image_to_data(
                image, lang=self.lang, output_type=pytesseract.Output.DICT
            )

            # Calculate confidence
            confidences = [
                int(conf) for conf in data["conf"] if conf != "-1"
            ]
            avg_confidence = (
                sum(confidences) / len(confidences) if confidences else 0
            )

            return {
                "text": text.strip(),
                "confidence": round(avg_confidence, 2),
                "word_count": len(text.split()),
                "language": self.lang,
                "image_size": {
                    "width": image.width,
                    "height": image.height,
                },
            }

        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            raise

    async def process_image_with_boxes(
        self, image_data: bytes
    ) -> Dict[str, Any]:
        """
        Extract text with bounding box information

        Args:
            image_data: Image file bytes

        Returns:
            Dictionary with text and bounding box data
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Get bounding boxes
            data = pytesseract.image_to_data(
                image, lang=self.lang, output_type=pytesseract.Output.DICT
            )

            # Extract words with boxes
            words = []
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                if int(data["conf"][i]) > 0:  # Filter out low confidence
                    words.append(
                        {
                            "text": data["text"][i],
                            "confidence": int(data["conf"][i]),
                            "bbox": {
                                "x": data["left"][i],
                                "y": data["top"][i],
                                "width": data["width"][i],
                                "height": data["height"][i],
                            },
                        }
                    )

            return {
                "words": words,
                "total_words": len(words),
                "full_text": " ".join([w["text"] for w in words]),
            }

        except Exception as e:
            logger.error(f"OCR with boxes error: {e}")
            raise
