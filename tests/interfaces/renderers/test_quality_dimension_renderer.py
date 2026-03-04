from sess.domain.models import QualityScores
from sess.interfaces.renderers.quality_dimension_renderer import (
    calculate_gradients,
    html_transformer,
)


def test_calculate_gradients_returns_one_gradient_per_score() -> None:
    gradients = calculate_gradients([1.0, -2.0, 0.5, 0.0])
    assert len(gradients) == 4
    assert all("linear-gradient" in gradient for gradient in gradients)


def test_html_transformer_contains_key_sections() -> None:
    quality_html, views_html = html_transformer(
        predicted_views=1234,
        scores=QualityScores(
            intrinsic=0.1,
            contextual=0.2,
            representational=0.3,
            reputational=0.4,
        ),
    )
    assert "Intrinsic Quality" in quality_html
    assert "Predicted views" in views_html
    assert "1234" in views_html

