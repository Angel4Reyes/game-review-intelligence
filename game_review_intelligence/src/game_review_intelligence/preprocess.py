'''

normalize_review(text):
    handle missing values
    convert text to lowercase
    remove unnecessary whitespace
    optionally remove URLs or HTML
    return cleaned text

clean_reviews(data):
    copy the input data
    clean the review-text column
    remove unusable rows
    create useful columns such as review_length
    return cleaned data

'''