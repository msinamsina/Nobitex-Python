"""Nobitex: A Python SDK For Nobitex Exchange."""

# using importlib.metadata
import importlib.metadata

__version__ = importlib.metadata.version(__name__)

__all__ = ["__version__"]
