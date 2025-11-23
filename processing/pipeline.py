"""
Image Processing Pipeline with PyTorch GPU Acceleration
"""
import torch
import torch.nn as nn
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class ProcessingResult:
    """Container for processing results"""
    processed_image: np.ndarray
    features: Dict[str, float]
    metadata: Dict[str, Any]


class ProcessingPipeline:
    """Configurable image processing pipeline"""

    def __init__(self, use_gpu: bool = True):
        """
        Initialize processing pipeline

        Args:
            use_gpu: Use GPU acceleration if available
        """
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() 
                                   else 'cpu')
        self.logger.info(f"Processing pipeline using device: {self.device}")

        self.processors: List[Callable] = []
        self.ml_model: Optional[nn.Module] = None

    def add_processor(self, processor: Callable):
        """Add processing step to pipeline"""
        self.processors.append(processor)
        self.logger.info(f"Added processor: {processor.__name__}")

    def load_ml_model(self, model: nn.Module):
        """Load PyTorch model for GPU-accelerated processing"""
        self.ml_model = model.to(self.device)
        self.ml_model.eval()
        self.logger.info("Loaded ML model to GPU")

    def process(self, image: np.ndarray) -> ProcessingResult:
        """
        Process image through pipeline

        Args:
            image: Input image as numpy array

        Returns:
            ProcessingResult with processed image and extracted features
        """
        processed = image.copy()
        features = {}

        # Apply sequential processors
        for processor in self.processors:
            try:
                processed, proc_features = processor(processed)
                features.update(proc_features)
            except Exception as e:
                self.logger.error(f"Processor {processor.__name__} failed: {e}")

        # Apply ML model if loaded
        if self.ml_model is not None:
            ml_features = self._apply_ml_model(processed)
            features.update(ml_features)

        return ProcessingResult(
            processed_image=processed,
            features=features,
            metadata={"pipeline_steps": len(self.processors)}
        )

    def _apply_ml_model(self, image: np.ndarray) -> Dict[str, float]:
        """Apply ML model for feature extraction"""
        try:
            # Convert to torch tensor
            img_tensor = torch.from_numpy(image).float().unsqueeze(0).unsqueeze(0)
            img_tensor = img_tensor.to(self.device)

            # Normalize
            img_tensor = (img_tensor - img_tensor.min()) / (img_tensor.max() - img_tensor.min())

            with torch.no_grad():
                output = self.ml_model(img_tensor)

            # Extract features from output
            features = {
                f"ml_feature_{i}": float(val) 
                for i, val in enumerate(output.cpu().numpy().flatten())
            }
            return features

        except Exception as e:
            self.logger.error(f"ML model inference failed: {e}")
            return {}


# Standard Image Processors

def background_subtraction(image: np.ndarray, 
                          background: Optional[np.ndarray] = None) -> tuple:
    """Subtract background from image"""
    if background is None:
        background = np.median(image)

    result = np.clip(image.astype(np.float32) - background, 0, None)
    features = {"mean_intensity": float(np.mean(result))}

    return result.astype(image.dtype), features


def gaussian_filter(image: np.ndarray, sigma: float = 1.0) -> tuple:
    """Apply Gaussian smoothing"""
    from scipy.ndimage import gaussian_filter as gf

    result = gf(image.astype(np.float32), sigma=sigma)
    features = {"filter_sigma": sigma}

    return result.astype(image.dtype), features


def find_centroids(image: np.ndarray, threshold: float = 0.5) -> tuple:
    """Find bright spots and calculate centroids"""
    from scipy.ndimage import label, center_of_mass

    # Threshold image
    normalized = (image - image.min()) / (image.max() - image.min())
    binary = normalized > threshold

    # Label connected components
    labeled, num_features = label(binary)

    # Calculate centroids
    centroids = center_of_mass(image, labeled, range(1, num_features + 1))

    features = {
        "num_spots": num_features,
        "centroid_x": centroids[0][1] if num_features > 0 else 0,
        "centroid_y": centroids[0][0] if num_features > 0 else 0
    }

    return image, features


class SimpleFeatureExtractor(nn.Module):
    """Simple CNN for feature extraction"""

    def __init__(self, output_features: int = 16):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(64, output_features)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x
