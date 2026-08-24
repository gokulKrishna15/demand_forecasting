"""Simple data adapter to allow swapping data sources via `DATA_SOURCE` env var.
Supported values: 'local' (default), 'internal' (maps to backend/data/internal), 'kaggle' (maps to data/kaggle)
"""
import os
from pathlib import Path
from backend.config import BASE_DIR

DATA_SOURCE = os.getenv('DATA_SOURCE', 'local')


def tabular_dir() -> Path:
    if DATA_SOURCE == 'internal':
        return BASE_DIR / 'backend' / 'data' / 'internal' / 'tabular'
    if DATA_SOURCE == 'kaggle':
        return BASE_DIR / 'data' / 'kaggle' / 'tabular'
    return BASE_DIR / 'data' / 'tabular'


def docs_dir() -> Path:
    if DATA_SOURCE == 'internal':
        return BASE_DIR / 'backend' / 'data' / 'internal' / 'docs'
    if DATA_SOURCE == 'kaggle':
        return BASE_DIR / 'data' / 'kaggle' / 'docs'
    return BASE_DIR / 'data' / 'docs'
