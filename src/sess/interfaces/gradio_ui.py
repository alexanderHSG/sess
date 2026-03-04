"""Gradio UI composition."""

from __future__ import annotations

import asyncio
from typing import Any

import gradio as gr
import nest_asyncio

from sess.bootstrap import AppContainer
from sess.domain.constants import AUTHOR_CHOICES, CATEGORY_CHOICES
from sess.domain.models import SlideDeckRequest
from sess.domain.services.pdf_rendering import process_pdf_to_images
from sess.logging import get_logger

logger = get_logger(__name__)


def _run_async(coro: Any) -> Any:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    nest_asyncio.apply()
    return loop.run_until_complete(coro)


def _extract_selected_image_path(images: Any, index: int) -> str:
    selected = images[index]
    if isinstance(selected, (list, tuple)):
        return str(selected[0])
    return str(selected)


def _popup_content_category() -> None:
    gr.Info(
        "Choose a content category: Indicate the purpose for which you intend to publish the slide deck and the evaluation will be adjusted accordingly."
    )


def _popup_author() -> None:
    gr.Info("Select the author's name: Select the author's name to assign the slide deck to the author accordingly.")


def _popup_timeline() -> None:
    gr.Info(
        "Customize your view prediction timeline: Choose how many days after upload you would like to predict the viewer engagement."
    )


def _popup_education_level() -> None:
    gr.Info(
        "Enter ISCED-level of education of your audience: Indicate the educational degree of your audience to make the evaluation align with the educational aspiration."
    )


def _popup_start() -> None:
    gr.Info(
        "Start to evaluate your slide deck: Based on your specified requirements and the uploaded slide deck, you can now start the AI-based evaluation."
    )


def _popup_fact() -> None:
    gr.Info("Check the content of your slide deck: Verify the veracity of the content on the slides with our factuality check.")


def create_demo(container: AppContainer) -> gr.TabbedInterface:
    def process_deck(uploaded_file: str, category: str, prediction_days: int, author: str) -> tuple[str, str, str]:
        if not uploaded_file:
            return "", "", "Please upload a PDF file before processing."

        try:
            request = SlideDeckRequest(
                uploaded_file=uploaded_file,
                category=category,
                prediction_days=int(prediction_days),
                author=author,
            )

            result = _run_async(container.process_slide_deck_use_case.execute(request))
            return (
                result.quality_dimensions_html,
                result.predicted_views_html,
                result.factuality_markdown,
            )
        except Exception as error:
            logger.exception("Slide deck processing failed: %s", error)
            return "", "", f"Processing failed: {error}"

    async def handle_upload(pdf_file: str) -> list[Any]:
        if not pdf_file:
            return []
        return process_pdf_to_images(pdf_file)

    def get_select_index(evt: gr.SelectData) -> int:
        return int(evt.index)

    def on_feedback_button_click(images: Any, index: float) -> str:
        if images is None or index is None:
            return "Select a slide first."
        try:
            selected_image_path = _extract_selected_image_path(images, int(index))
            return container.generate_slide_feedback_use_case.execute(selected_image_path)
        except Exception as error:
            logger.exception("Slide feedback generation failed: %s", error)
            return f"Feedback generation failed: {error}"

    with gr.Blocks() as demo_tab1:
        gr.Markdown("# Slide Deck Evaluation Dashboard")
        gr.Markdown(
            """
            Welcome to the Slide Deck Evaluation Dashboard, where advanced AI evaluates the content,
            design, and communication efficacy of your presentations. Enhance your insights with customized
            feedback, automated fact-checks, and AI-driven verification. Upload your slide deck in PDF format,
            tailor your settings, and start evaluation.
            """
        )

        with gr.Row():
            upload = gr.File(label="Upload your slide deck", file_types=[".pdf"])

            category = gr.Dropdown(
                choices=list(CATEGORY_CHOICES),
                label="Content Category",
                value="Education",
            )

            author = gr.Dropdown(
                choices=list(AUTHOR_CHOICES),
                label="Author's name",
                value="speaker_other",
            )
            author.change(lambda _: _popup_timeline(), inputs=[author], outputs=[])

            prediction_days = gr.Slider(
                minimum=0,
                maximum=10000,
                label="Select number of days after upload for view forecast",
                value=30,
                visible=False,
            )
            level_of_education = gr.Dropdown(
                choices=["High School", "Undergraduate", "Graduate", "PhD"],
                label="Level of education of the audience",
                value="Undergraduate",
            )

        with gr.Row():
            process_btn = gr.Button("Process the whole slide deck")
            process_btn.click(lambda _: _popup_fact(), inputs=[process_btn], outputs=[])

            category.change(lambda _: _popup_author(), inputs=[category], outputs=[])
            prediction_days.change(lambda _: _popup_education_level(), inputs=[prediction_days], outputs=[])
            level_of_education.change(lambda _: _popup_start(), inputs=[level_of_education], outputs=[])

        with gr.Row():
            fact_display = gr.Markdown(label="Fact checker results:")

        with gr.Accordion(label="Decoding the Measurements: How are quality dimensions assessed?", open=False):
            gr.Markdown(
                """## Intrinsic Quality
Intrinsic quality refers to the inherent value of content, assessed through organization, clarity, and relevance.
## Contextual Quality
Contextual quality assesses how informative and relevant content is, considering pages, image density, and category.
## Representational Quality
Representational quality gauges clarity and informativeness by analyzing mean words per slide and word count variance.
## Reputational Quality
Reputational quality evaluates authority and trustworthiness by examining author recognition and field credibility.
"""
            )
        quality_dimensions_output = gr.HTML()
        predicted_views_output = gr.HTML()

    with gr.Blocks() as demo_tab2:
        with gr.Row():
            image_slider = gr.Gallery(label="Slide Viewer", allow_preview=True, interactive=False)
            upload.change(handle_upload, inputs=[upload], outputs=[image_slider])
            category.change(lambda _: _popup_author(), inputs=[category], outputs=[])
            prediction_days.change(lambda _: _popup_education_level(), inputs=[prediction_days], outputs=[])
            level_of_education.change(lambda _: _popup_start(), inputs=[level_of_education], outputs=[])

        process_btn.click(
            process_deck,
            inputs=[upload, category, prediction_days, author],
            outputs=[quality_dimensions_output, predicted_views_output, fact_display],
        )

        with gr.Column():
            with gr.Row():
                feedback_button = gr.Button("Give me feedback on this slide")
                selected = gr.Number(show_label=False, visible=False)

        with gr.Accordion(label="Decoding the Feedback: How are checkpoints assessed?", open=False):
            gr.Markdown(
                """We analyze slide design based on checkpoints including pictograms, subheadings,
emphasis, hierarchy, flow, structure, and citation consistency."""
            )

        with gr.Row():
            feedback_output = gr.Textbox(label="Slide Feedback")

        image_slider.select(get_select_index, None, selected)
        feedback_button.click(on_feedback_button_click, inputs=[image_slider, selected], outputs=[feedback_output])

    return gr.TabbedInterface(
        [demo_tab1, demo_tab2],
        ["Overall Slide Evaluation", "Single Slide Feedback"],
    )
