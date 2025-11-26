"""Computer vision detection utilities."""

import logging
from typing import Optional, List, Tuple, Any
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class VisionDetector:
    """Handles computer vision detection tasks."""

    def __init__(self, confidence_threshold: float = 0.8):
        """
        Initialize vision detector.

        Args:
            confidence_threshold: Confidence threshold for detections (0-1)
        """
        try:
            import cv2
            self.cv2 = cv2
        except ImportError:
            raise ImportError(
                "OpenCV not installed. Install with: pip install opencv-python"
            )

        try:
            from PIL import Image
            self.Image = Image
        except ImportError:
            raise ImportError(
                "Pillow not installed. Install with: pip install pillow"
            )

        self.confidence_threshold = confidence_threshold
        logger.info(f"Vision detector initialized (threshold={confidence_threshold})")

    def find_template(
        self,
        image: np.ndarray,
        template: np.ndarray,
        threshold: Optional[float] = None,
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Find template in image using template matching.

        Args:
            image: Source image (numpy array)
            template: Template to find (numpy array)
            threshold: Optional confidence threshold override

        Returns:
            Tuple of (x, y, width, height) or None if not found
        """
        threshold = threshold or self.confidence_threshold

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            image_gray = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2GRAY)
        else:
            image_gray = image

        if len(template.shape) == 3:
            template_gray = self.cv2.cvtColor(template, self.cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template

        # Template matching
        result = self.cv2.matchTemplate(
            image_gray, template_gray, self.cv2.TM_CCOEFF_NORMED
        )
        min_val, max_val, min_loc, max_loc = self.cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = template_gray.shape
            x, y = max_loc
            logger.debug(f"Template found at ({x}, {y}) with confidence {max_val}")
            return (x, y, w, h)

        logger.debug(f"Template not found (best match: {max_val})")
        return None

    def detect_edges(
        self, image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150
    ) -> np.ndarray:
        """
        Detect edges in image using Canny edge detection.

        Args:
            image: Input image
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection

        Returns:
            Edge-detected image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        edges = self.cv2.Canny(gray, low_threshold, high_threshold)
        logger.debug("Edge detection completed")
        return edges

    def find_contours(
        self, image: np.ndarray, min_area: int = 100
    ) -> List[np.ndarray]:
        """
        Find contours in image.

        Args:
            image: Input image (should be binary/edge-detected)
            min_area: Minimum contour area to include

        Returns:
            List of contours
        """
        contours, _ = self.cv2.findContours(
            image, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter by minimum area
        filtered = [c for c in contours if self.cv2.contourArea(c) >= min_area]

        logger.debug(f"Found {len(filtered)} contours (min_area={min_area})")
        return filtered

    def get_image_stats(self, image: np.ndarray) -> dict:
        """
        Get statistics about an image.

        Args:
            image: Input image

        Returns:
            Dictionary with image statistics
        """
        stats = {
            "shape": image.shape,
            "dtype": str(image.dtype),
            "mean": float(image.mean()),
            "std": float(image.std()),
            "min": float(image.min()),
            "max": float(image.max()),
        }

        if len(image.shape) == 3:
            stats["channels"] = image.shape[2]
            for i, color in enumerate(["blue", "green", "red"]):
                stats[f"mean_{color}"] = float(image[:, :, i].mean())
        else:
            stats["channels"] = 1

        logger.debug(f"Image stats: {stats}")
        return stats

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load image from file.

        Args:
            image_path: Path to image file

        Returns:
            Image as numpy array
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = self.cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        logger.debug(f"Loaded image from {image_path}")
        return image

    def save_image(self, image: np.ndarray, output_path: str) -> None:
        """
        Save image to file.

        Args:
            image: Image to save
            output_path: Output file path
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        success = self.cv2.imwrite(str(path), image)
        if not success:
            raise ValueError(f"Failed to save image: {output_path}")

        logger.debug(f"Saved image to {output_path}")

    def resize_image(
        self, image: np.ndarray, width: int, height: int
    ) -> np.ndarray:
        """
        Resize image to specified dimensions.

        Args:
            image: Input image
            width: Target width
            height: Target height

        Returns:
            Resized image
        """
        resized = self.cv2.resize(image, (width, height))
        logger.debug(f"Resized image to {width}x{height}")
        return resized

    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale.

        Args:
            image: Input image

        Returns:
            Grayscale image
        """
        if len(image.shape) == 2:
            return image  # Already grayscale

        gray = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2GRAY)
        logger.debug("Converted image to grayscale")
        return gray
