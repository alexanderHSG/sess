"""HTML renderers for quality dimensions and predicted views."""

from __future__ import annotations

from sess.domain.models import QualityScores


def calculate_gradients(scores: list[float]) -> list[str]:
    max_score = 10.0
    for score in scores:
        if abs(score) > 10:
            max_score = abs(score)

    gradients: list[str] = []
    for score in scores:
        percentage = (abs(score) / max_score) * 100
        if score >= 0:
            pivot = percentage + 50
            gradient = (
                "linear-gradient(to right, #00ff00 0%, #00ff00 "
                f"{pivot}%, #ff0000 {pivot}%, #ff0000 100%)"
            )
        else:
            green_percentage = 50 - percentage
            gradient = (
                "linear-gradient(to right, #00ff00 0%, #00ff00 "
                f"{green_percentage}%, #ff0000 {green_percentage}%, #ff0000 100%)"
            )
        gradients.append(gradient)
    return gradients


def html_transformer(predicted_views: int, scores: QualityScores) -> tuple[str, str]:
    gradients = calculate_gradients(
        [
            scores.intrinsic,
            scores.contextual,
            scores.representational,
            scores.reputational,
        ]
    )

    predicted_views_html = f"""
    <style>
        .predicted-views-container {{
            padding: 20px;
            border-radius: 8px;
            background-color: #ffffff;
            text-align: center;
            margin-top: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            color: #000000;
        }}
        .predicted-views-title {{
            margin: 0;
            font-size: 20px;
            font-weight: bold;
        }}
        .predicted-views-number {{
            margin: 10px 0;
            font-size: 26px;
            font-weight: bold;
        }}
        @media (prefers-color-scheme: dark) {{
            .predicted-views-container {{
                background-color: #1F2937;
                color: #f0f0f0;
            }}
        }}
    </style>
    <div class="predicted-views-container">
        <p class="predicted-views-title">
            Predicted views 30 days after your upload to a slide-sharing platform
            (e.g. Speakerdeck.com)
        </p>
        <p class="predicted-views-number">{predicted_views}</p>
    </div>
    """

    quality_dimensions_html = f"""
    <style>
        .quality-display {{
            margin-bottom: 20px;
            text-align: center;
        }}
        .quality-display h3 {{
            margin-bottom: 10px;
            color: #ffffff;
        }}
        .quality-gradient {{
            height: 20px;
            border-radius: 5px;
            width: 100%;
        }}
        #intrinsic-quality .quality-gradient {{ background: {gradients[0]}; }}
        #contextual-quality .quality-gradient {{ background: {gradients[1]}; }}
        #representational-quality .quality-gradient {{ background: {gradients[2]}; }}
        #reputational-quality .quality-gradient {{ background: {gradients[3]}; }}
    </style>

    <div id="ai-feedback">
        <h2 style="color: #ffffff;">AI Feedback Viewer</h2>
        <div class="quality-display" id="intrinsic-quality">
            <h3>Intrinsic Quality</h3>
            <div class="quality-gradient"></div>
        </div>
        <div class="quality-display" id="contextual-quality">
            <h3>Contextual Quality</h3>
            <div class="quality-gradient"></div>
        </div>
        <div class="quality-display" id="representational-quality">
            <h3>Representational Quality</h3>
            <div class="quality-gradient"></div>
        </div>
        <div class="quality-display" id="reputational-quality">
            <h3>Reputational Quality</h3>
            <div class="quality-gradient"></div>
        </div>
    </div>
    """

    return quality_dimensions_html, predicted_views_html
