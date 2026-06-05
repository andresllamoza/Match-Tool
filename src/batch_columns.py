"""Shared helpers for batch CSV column detection (no Streamlit dependency)."""

BATCH_EMPLOYER_COLUMNS = ("name", "employer", "employer_name", "company")


def detect_employer_column(columns: list[str]) -> str:
    normalized_columns = {str(column).strip().lower(): column for column in columns}
    for candidate in BATCH_EMPLOYER_COLUMNS:
        if candidate in normalized_columns:
            return normalized_columns[candidate]
    return columns[0]
