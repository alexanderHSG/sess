"""Quality scoring and explainability helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from threading import Lock

import lime.lime_tabular
import numpy as np
import pandas as pd

from sess.domain.models import QualityScores


def prepare_explainer_training_data(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared["time_elapsed_until_Oct23"] = prepared["time_elapsed_until_Oct23"].apply(
        lambda value: 0 if value < 0 else value
    )
    prepared = prepared[prepared["content"].notnull()]
    prepared = prepared[(prepared["total_numImages"] / prepared["total_numWords"]) < 2]
    prepared = prepared.drop(columns=["url", "pdf"], errors="ignore")

    speaker_counts = prepared["speaker"].value_counts()
    prepared["speaker"] = prepared["speaker"].apply(
        lambda value: value if speaker_counts.get(value, 0) > 20 else "other"
    )
    prepared = prepared[prepared.groupby("category").category.transform("size") > 20]
    prepared = prepared[prepared["views"] != 0]
    prepared = pd.get_dummies(prepared, columns=["speaker", "category"])
    prepared["views"] = np.log(prepared["views"] + 0.1)
    prepared = prepared.reindex(sorted(prepared.columns), axis=1)
    return prepared


def build_explainer(prepared_df: pd.DataFrame) -> lime.lime_tabular.LimeTabularExplainer:
    test_data = prepared_df.sample(frac=0.2, random_state=1)
    remainder = prepared_df.drop(test_data.index)
    validation_data = remainder.sample(frac=0.25, random_state=1)
    train_data = remainder.drop(validation_data.index)

    feature_frame = train_data.drop(columns=["id", "stars", "views", "content"], errors="ignore")
    feature_names = list(feature_frame.columns)
    categorical_columns = feature_frame.select_dtypes(include="bool").columns
    categorical_indices = [feature_frame.columns.get_loc(name) for name in categorical_columns]

    return lime.lime_tabular.LimeTabularExplainer(
        training_data=feature_frame.to_numpy(),
        feature_names=feature_names,
        class_names=["views"],
        categorical_features=categorical_indices,
        verbose=True,
        mode="regression",
    )


@dataclass
class LimeExplainerProvider:
    loader: Callable[[], pd.DataFrame]

    def __post_init__(self) -> None:
        self._explainer: lime.lime_tabular.LimeTabularExplainer | None = None
        self._lock = Lock()

    def get(self) -> lime.lime_tabular.LimeTabularExplainer:
        if self._explainer is not None:
            return self._explainer
        with self._lock:
            if self._explainer is None:
                raw_df = self.loader()
                prepared = prepare_explainer_training_data(raw_df)
                self._explainer = build_explainer(prepared)
        return self._explainer


def aggregate_quality_scores(
    explanation_rows: Iterable[tuple[str, float]],
    author: str,
) -> QualityScores:
    reputational_score = 0.0
    contextual_score = 0.0
    representational_score = 0.0
    intrinsic_score = 0.0

    for label, value in explanation_rows:
        if label.startswith(author):
            reputational_score += value
        if "numPages" in label or "total_numImages" in label or "std_numImages" in label:
            contextual_score += value
        if (
            label.startswith("mean_numWords")
            or label.startswith("std_numWords")
            or label.startswith("total_numWords")
        ):
            representational_score += value
        if "entropy" in label:
            intrinsic_score += value

    return QualityScores(
        intrinsic=intrinsic_score,
        contextual=contextual_score,
        representational=representational_score,
        reputational=reputational_score * 3,
    )
