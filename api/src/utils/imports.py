"""
Import utilities for handling module imports across the application.
"""

import sys
from pathlib import Path


def setup_imports():
    """
    Setup Python path for imports to work correctly.
    This should be called at the start of the application.
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    api_src = project_root / "api" / "src"

    # Add to Python path if not already there
    api_src_str = str(api_src)
    if api_src_str not in sys.path:
        sys.path.insert(0, api_src_str)

    return api_src


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_api_src() -> Path:
    """Get the API source directory."""
    return get_project_root() / "api" / "src"


# Auto-setup imports when module is imported
setup_imports()
