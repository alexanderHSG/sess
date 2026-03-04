from sess.application.use_cases.check_factuality import format_factuality_markdown
from sess.domain.models import FactualityItem


def test_format_factuality_markdown_includes_links_for_false_claims() -> None:
    items = [
        FactualityItem(
            statement="Claim A",
            verification_result="False",
            search_string="claim a",
        ),
        FactualityItem(
            statement="Claim B",
            verification_result="T",
            search_string="claim b",
        ),
    ]

    markdown = format_factuality_markdown(items)

    assert "Verification Results" in markdown
    assert "[Consensus]" in markdown
    assert "[Google]" in markdown
    assert "Claim A" in markdown
    assert "Claim B" in markdown

