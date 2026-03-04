"""Backward-compatible wrapper for quality HTML rendering."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sess.domain.models import QualityScores  # noqa: E402
from sess.interfaces.renderers.quality_dimension_renderer import (  # noqa: E402
    calculate_gradients,
    html_transformer,
)


def html_tranformer(
    predicted_views: int,
    intrinsic_score: float,
    contextual_score: float,
    representational_score: float,
    reputational_score: float,
) -> tuple[str, str]:
    scores = QualityScores(
        intrinsic=intrinsic_score,
        contextual=contextual_score,
        representational=representational_score,
        reputational=reputational_score,
    )
    return html_transformer(predicted_views=predicted_views, scores=scores)


__all__ = ["calculate_gradients", "html_tranformer"]

