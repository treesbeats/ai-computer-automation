"""OCR (Optical Character Recognition) utilities."""

import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class OCRReader:
    """Handles OCR tasks using Tesseract."""

    def __init__(self, lang: str = "eng"):
        """
        Initialize OCR reader.

        Args:
            lang: Language code for OCR (default: 'eng' for English)
        """
        try:
            import pytesseract
            self.pytesseract = pytesseract
        except ImportError:
            raise ImportError(
                "pytesseract not installed. Install with: pip install pytesseract\n"
                "Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
            )

        self.lang = lang
        logger.info(f"OCR reader initialized (lang={lang})")

    def read_text(self, image: np.ndarray, config: Optional[str] = None) -> str:
        """
        Extract text from image.

        Args:
            image: Input image (numpy array)
            config: Optional Tesseract configuration string

        Returns:
            Extracted text
        """
        try:
            if config:
                text = self.pytesseract.image_to_string(
                    image, lang=self.lang, config=config
                )
            else:
                text = self.pytesseract.image_to_string(image, lang=self.lang)

            logger.debug(f"Extracted text (length={len(text)})")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise

    def read_text_with_boxes(
        self, image: np.ndarray
    ) -> list:
        """
        Extract text with bounding boxes.

        Args:
            image: Input image

        Returns:
            List of dictionaries with text and box coordinates
        """
        try:
            data = self.pytesseract.image_to_data(
                image, lang=self.lang, output_type=self.pytesseract.Output.DICT
            )

            results = []
            n_boxes = len(data["text"])

            for i in range(n_boxes):
                text = data["text"][i].strip()
                if text:  # Only include non-empty text
                    results.append(
                        {
                            "text": text,
                            "x": data["left"][i],
                            "y": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i],
                            "confidence": data["conf"][i],
                        }
                    )

            logger.debug(f"Extracted {len(results)} text boxes")
            return results
        except Exception as e:
            logger.error(f"OCR with boxes failed: {e}")
            raise
