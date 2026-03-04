"""Model loading and registry."""

from __future__ import annotations

import pickle
from pathlib import Path
from threading import Lock
from typing import Any

from sess.domain.errors import ArtifactNotFoundError


class ModelRegistry:
    """Lazy-loading singleton model registry."""

    _instance: ModelRegistry | None = None
    _instance_lock = Lock()

    def __init__(self, mlp_path: Path, svr_path: Path, rfr_path: Path) -> None:
        self._mlp_path = mlp_path
        self._svr_path = svr_path
        self._rfr_path = rfr_path
        self._loaded = False
        self._load_lock = Lock()
        self._mlp_model: Any = None
        self._svr_model: Any = None
        self._rfr_model: Any = None

    @classmethod
    def get_instance(cls, mlp_path: Path, svr_path: Path, rfr_path: Path) -> ModelRegistry:
        if cls._instance is not None:
            return cls._instance
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls(mlp_path=mlp_path, svr_path=svr_path, rfr_path=rfr_path)
        return cls._instance

    def _load_model(self, path: Path) -> Any:
        if not path.exists():
            raise ArtifactNotFoundError(f"Required model artifact not found: {path}")
        with path.open("rb") as file_handle:
            return pickle.load(file_handle)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        with self._load_lock:
            if self._loaded:
                return
            self._mlp_model = self._load_model(self._mlp_path)
            self._svr_model = self._load_model(self._svr_path)
            self._rfr_model = self._load_model(self._rfr_path)
            self._loaded = True

    @property
    def mlp(self) -> Any:
        self._ensure_loaded()
        return self._mlp_model

    @property
    def svr(self) -> Any:
        self._ensure_loaded()
        return self._svr_model

    @property
    def rfr(self) -> Any:
        self._ensure_loaded()
        return self._rfr_model
