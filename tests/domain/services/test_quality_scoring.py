import pytest

from sess.domain.services.quality_scoring import aggregate_quality_scores


def test_aggregate_quality_scores_groups_contributions() -> None:
    rows = [
        ("speaker_other <= 0.5", 0.4),
        ("numPages > 10", 0.3),
        ("total_numImages <= 3", 0.2),
        ("mean_numWords <= 20", 0.1),
        ("std_numWords > 2", 0.05),
        ("entropy <= 0.7", -0.12),
    ]

    result = aggregate_quality_scores(rows, "speaker_other")

    assert result.reputational == pytest.approx(1.2)
    assert result.contextual == pytest.approx(0.5)
    assert result.representational == pytest.approx(0.15)
    assert result.intrinsic == pytest.approx(-0.12)

