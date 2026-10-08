from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet"}

# Start with only the column absolutely required for a review.
# Add game_id, rating, or recommended later if your dataset requires them.
REQUIRED_COLUMNS = {"review_text"}

# Different datasets may use different names for the same concept.
COLUMN_ALIASES = {
    "review": "review_text",
    "text": "review_text",
    "appid": "game_id",
    "app_id": "game_id",
    "game": "game_name",
    "title": "game_name",
    "voted_up": "recommended",
}


def _read_one_file(path: Path) -> pd.DataFrame:
    """Read one supported file into a DataFrame."""

    extension = path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(path)

    if extension == ".json":
        return pd.read_json(path)

    if extension == ".jsonl":
        return pd.read_json(path, lines=True)

    if extension == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(f"Unsupported file type: {path.suffix}")


def _standardize_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and apply known aliases."""

    data = data.copy()

    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    data = data.rename(columns=COLUMN_ALIASES)

    # Prevent two original columns from becoming the same column name.
    duplicate_columns = data.columns[data.columns.duplicated()].tolist()

    if duplicate_columns:
        raise ValueError(
            f"Duplicate columns after standardization: {duplicate_columns}"
        )

    return data

def _validate_columns(data: pd.DataFrame, source: Path) -> None:
    """Check that one file contains the required columns."""

    missing_columns = REQUIRED_COLUMNS - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"{source.name} is missing required columns: "
            f"{sorted(missing_columns)}"
        )


def load_reviews(file_path, limit=None) -> pd.DataFrame:
    """
    Load one review file or all supported files inside a directory.

    The limit applies after files are combined, so limit=1000
    returns at most 1,000 total rows.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if limit is not None:
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("limit must be a non-negative integer")

    if path.is_file():
        files = [path]

    elif path.is_dir():
        files = sorted(
            file
            for file in path.rglob("*")
            if file.is_file()
            and file.suffix.lower() in SUPPORTED_EXTENSIONS
        )

        if not files:
            raise FileNotFoundError(
                f"No supported review files found inside: {path}"
            )

    else:
        raise ValueError(f"Path is neither a file nor a directory: {path}")

    loaded_frames = []

    for file in files:
        data = _read_one_file(file)
        data = _standardize_columns(data)
        _validate_columns(data, file)

        # Useful when debugging or comparing multiple files.
        data["source_file"] = file.name

        loaded_frames.append(data)

    reviews = pd.concat(
        loaded_frames,
        ignore_index=True,
        sort=False,
    )

    if limit is not None:
        reviews = reviews.head(limit)

    return reviews.reset_index(drop=True)


REQUIRED_COLUMNS = {
    "review_text",
}

EXPECTED_COLUMNS = {
    "review_text",
    "review_id",
    "game_id",
    "game_name",
    "rating",
    "recommended",
    "review_date",
    "hours_played",
    "helpful_votes",
    "source_file",
}

GAME_IDENTIFIER_COLUMNS = {
    "game_id",
    "game_name",
}


def validate_schema(data: pd.DataFrame) -> dict:
    """
    Check whether a DataFrame contains the expected review columns.

    Returns a report instead of immediately raising an error.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    # This creates a copy, so the original DataFrame is not changed.
    standardized_data = _standardize_columns(data)

    actual_columns = set(standardized_data.columns)

    missing_columns = sorted(REQUIRED_COLUMNS - actual_columns)
    unexpected_columns = sorted(actual_columns - EXPECTED_COLUMNS)

    warnings = []

    if not actual_columns.intersection(GAME_IDENTIFIER_COLUMNS):
        warnings.append(
            "No game_id or game_name column was found. "
            "Unique game counts may not be available."
        )

    return {
        "is_valid": len(missing_columns) == 0,
        "present_columns": sorted(actual_columns),
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "warnings": warnings,
    }


def summarize_data(data: pd.DataFrame) -> dict:
    """
    Return basic statistics about a review DataFrame.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    standardized_data = _standardize_columns(data)

    # Prefer game_id, but fall back to game_name.
    if "game_id" in standardized_data.columns:
        unique_games = int(standardized_data["game_id"].nunique())
        game_identifier_used = "game_id"

    elif "game_name" in standardized_data.columns:
        unique_games = int(standardized_data["game_name"].nunique())
        game_identifier_used = "game_name"

    else:
        unique_games = None
        game_identifier_used = None

    missing_counts = standardized_data.isna().sum()

    missing_values = {
        str(column): int(count)
        for column, count in missing_counts.items()
        if count > 0
    }

    duplicate_rows = int(standardized_data.duplicated().sum())

    if "review_id" in standardized_data.columns:
        duplicate_review_ids = int(
            standardized_data["review_id"]
            .dropna()
            .duplicated()
            .sum()
        )
    else:
        duplicate_review_ids = None

    return {
        "row_count": len(standardized_data),
        "column_count": len(standardized_data.columns),
        "unique_games": unique_games,
        "game_identifier_used": game_identifier_used,
        "missing_values": missing_values,
        "total_missing_values": sum(missing_values.values()),
        "duplicate_rows": duplicate_rows,
        "duplicate_review_ids": duplicate_review_ids,
    }
