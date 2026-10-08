from game_review_intelligence.data_loader import (
    load_reviews,
    validate_schema,
    summarize_data,
)
def run_file_checks(file_path):
    """
    Load a review file or directory and print validation results.
    """

    print(f"Loading: {file_path}")

    try:
        data = load_reviews(file_path)

    except Exception as error:
        print(f"\nCould not load file:\n{error}")
        return None

    schema_report = validate_schema(data)
    summary_report = summarize_data(data)

    print("\n--- Schema Report ---")
    print(f"Valid schema: {schema_report['is_valid']}")
    print(f"Missing columns: {schema_report['missing_columns']}")
    print(f"Unexpected columns: {schema_report['unexpected_columns']}")

    if schema_report["warnings"]:
        print("Warnings:")
        for warning in schema_report["warnings"]:
            print(f"- {warning}")

    print("\n--- Data Summary ---")
    print(f"Rows: {summary_report['row_count']}")
    print(f"Columns: {summary_report['column_count']}")
    print(f"Unique games: {summary_report['unique_games']}")
    print(
        f"Game identifier used: "
        f"{summary_report['game_identifier_used']}"
    )
    print(f"Total missing values: {summary_report['total_missing_values']}")
    print(f"Duplicate rows: {summary_report['duplicate_rows']}")
    print(
        f"Duplicate review IDs: "
        f"{summary_report['duplicate_review_ids']}"
    )

    print("\nMissing values by column:")
    if summary_report["missing_values"]:
        for column, count in summary_report["missing_values"].items():
            print(f"- {column}: {count}")
    else:
        print("None")

    return {
        "data": data,
        "schema": schema_report,
        "summary": summary_report,
    }


if __name__ == "__main__":
    file_path = input(
        "Enter the file or directory path: "
    ).strip()

    run_file_checks(file_path)