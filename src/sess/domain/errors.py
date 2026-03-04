"""Custom exception hierarchy for the project."""


class SessError(Exception):
    """Base exception for known application failures."""


class ConfigurationError(SessError):
    """Raised for missing or invalid runtime configuration."""


class ArtifactNotFoundError(SessError):
    """Raised when a required local artifact is missing."""


class FeatureExtractionError(SessError):
    """Raised when PDF feature extraction fails."""


class ExternalServiceError(SessError):
    """Raised when an external API call fails."""


class ParsingError(SessError):
    """Raised when parser output is invalid or unavailable."""

