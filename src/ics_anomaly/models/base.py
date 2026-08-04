"""Common detector interface.

Every detector — heavy baseline or lightweight candidate — implements this contract so the
evaluation and benchmarking pipelines never special-case a model. Adding a detector means
subclassing this and adding a config file, not new plumbing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

import numpy as np
import numpy.typing as npt


class AnomalyDetector(ABC):
    """Fit on (predominantly benign) training windows, emit anomaly scores at inference.

    Scores are unitless and model-specific; higher means more anomalous. Binarization happens
    only via :meth:`predict` with a threshold that MUST be selected on a validation split —
    never on test data (see docs/adr/0001-scope.md and the leakage tests).
    """

    @abstractmethod
    def fit(self, X: npt.NDArray[np.floating]) -> Self:
        """Train on an array of shape (n_samples, n_features)."""

    @abstractmethod
    def score(self, X: npt.NDArray[np.floating]) -> npt.NDArray[np.float64]:
        """Return per-sample anomaly scores, shape (n_samples,). Higher = more anomalous."""

    def predict(self, X: npt.NDArray[np.floating], threshold: float) -> npt.NDArray[np.int_]:
        """Binarize scores at ``threshold``: 1 = anomaly, 0 = benign."""
        return (self.score(X) >= threshold).astype(np.int_)
