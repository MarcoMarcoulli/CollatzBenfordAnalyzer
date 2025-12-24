# gui/__init__.py
"""
GUI package for the Collatz Visualizer.

This package contains:
- app: main GUI controller (CollatzGui)
- widgets: custom rounded UI widgets
- theme: centralized styling constants
"""

from gui.app import CollatzGui

__all__ = [
    "CollatzGui",
]
