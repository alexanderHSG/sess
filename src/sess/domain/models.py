"""Typed domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SlideDeckRequest:
    uploaded_file: str
    category: str
    prediction_days: int
    author: str


@dataclass(frozen=True)
class QualityScores:
    intrinsic: float
    contextual: float
    representational: float
    reputational: float


@dataclass(frozen=True)
class ViewPredictionResult:
    predicted_views: int
    quality_scores: QualityScores
    quality_dimensions_html: str
    predicted_views_html: str


@dataclass(frozen=True)
class SlideDeckProcessingResult:
    quality_dimensions_html: str
    predicted_views_html: str
    factuality_markdown: str


@dataclass(frozen=True)
class FactualityItem:
    statement: str
    verification_result: str
    search_string: str

