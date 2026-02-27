from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

# face_recognition (dlib) provides:
# - face_locations: face detection
# - face_encodings: embedding extraction (128-D vector)
# - face_distance: similarity metric between embeddings
import face_recognition


@dataclass
class EncodeResult:
    status: str  # "OK" | "NO_FACE" | "MULTIPLE_FACES"
    encoding: Optional[np.ndarray]


def encode_single_face(rgb_image: np.ndarray) -> EncodeResult:
    """Detect exactly one face and return its encoding."""
    locations = face_recognition.face_locations(rgb_image, model="hog")
    if len(locations) == 0:
        return EncodeResult("NO_FACE", None)
    if len(locations) > 1:
        return EncodeResult("MULTIPLE_FACES", None)

    encodings = face_recognition.face_encodings(rgb_image, known_face_locations=locations)
    if not encodings:
        return EncodeResult("NO_FACE", None)
    return EncodeResult("OK", encodings[0])


@dataclass
class MatchResult:
    matched_student_id: Optional[int]
    distance: Optional[float]
    confidence: Optional[float]
    status: str  # "MATCH" | "UNKNOWN" | "NO_KNOWN_FACES"


def _distance_to_confidence(distance: float, threshold: float) -> float:
    # 0..1 score for UI (not a probability)
    conf = 1.0 - (distance / threshold)
    return float(max(0.0, min(1.0, conf)))


def match_face(
    encoding: np.ndarray,
    known_encodings: List[np.ndarray],
    known_student_ids: List[int],
    threshold: float = 0.55,
) -> MatchResult:
    if not known_encodings:
        return MatchResult(None, None, None, "NO_KNOWN_FACES")

    distances = face_recognition.face_distance(known_encodings, encoding)
    best_idx = int(np.argmin(distances))
    best_distance = float(distances[best_idx])
    confidence = _distance_to_confidence(best_distance, threshold)

    if best_distance <= threshold:
        return MatchResult(known_student_ids[best_idx], best_distance, confidence, "MATCH")

    return MatchResult(None, best_distance, confidence, "UNKNOWN")
