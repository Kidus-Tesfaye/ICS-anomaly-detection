"""Interface-conformance tests for the AnomalyDetector contract.

Uses a trivial reference detector so the contract (fit -> score -> predict) is exercised
without any real dataset. Every real detector added in M3/M4 gets registered into
DETECTOR_CLASSES below and inherits these checks for free.
"""

from __future__ import annotations

from typing import Self

import numpy as np
import numpy.typing as npt
import pytest

from ics_anomaly.models import AnomalyDetector


class MeanDistanceDetector(AnomalyDetector):
    """Reference detector: anomaly score = Euclidean distance from the training mean."""

    def fit(self, X: npt.NDArray[np.floating]) -> Self:
        self.mean_: npt.NDArray[np.float64] = X.mean(axis=0)
        return self

    def score(self, X: npt.NDArray[np.floating]) -> npt.NDArray[np.float64]:
        return np.linalg.norm(X - self.mean_, axis=1).astype(np.float64)


DETECTOR_CLASSES = [MeanDistanceDetector]


@pytest.fixture
def benign_and_anomalous() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(0)
    benign = rng.normal(0.0, 1.0, size=(200, 4))
    anomalous = rng.normal(8.0, 1.0, size=(20, 4))
    return benign, anomalous


@pytest.mark.parametrize("detector_cls", DETECTOR_CLASSES)
def test_fit_returns_self(detector_cls: type[AnomalyDetector]) -> None:
    det = detector_cls()
    assert det.fit(np.zeros((10, 3))) is det


@pytest.mark.parametrize("detector_cls", DETECTOR_CLASSES)
def test_score_shape_and_ordering(
    detector_cls: type[AnomalyDetector],
    benign_and_anomalous: tuple[np.ndarray, np.ndarray],
) -> None:
    benign, anomalous = benign_and_anomalous
    det = detector_cls().fit(benign)

    benign_scores = det.score(benign)
    anomalous_scores = det.score(anomalous)

    assert benign_scores.shape == (len(benign),)
    # Higher score must mean more anomalous.
    assert anomalous_scores.mean() > benign_scores.mean()


@pytest.mark.parametrize("detector_cls", DETECTOR_CLASSES)
def test_predict_binarizes_at_threshold(
    detector_cls: type[AnomalyDetector],
    benign_and_anomalous: tuple[np.ndarray, np.ndarray],
) -> None:
    benign, anomalous = benign_and_anomalous
    det = detector_cls().fit(benign)
    X = np.vstack([benign, anomalous])

    scores = det.score(X)
    threshold = float(np.quantile(scores, 0.9))
    preds = det.predict(X, threshold=threshold)

    assert set(np.unique(preds)) <= {0, 1}
    np.testing.assert_array_equal(preds, (scores >= threshold).astype(int))
