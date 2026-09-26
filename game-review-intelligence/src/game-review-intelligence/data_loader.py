
'''

load_reviews(file_path, limit=None):
    verify that the file exists
    read the file
    standardize column names
    verify required columns
    optionally limit the number of rows
    return the loaded data

validate_schema(data):
    check that required columns exist
    report missing or unexpected columns
    return validation results

summarize_data(data):
    count rows
    count unique games
    calculate missing-value totals
    calculate duplicate totals
    return a summary

'''