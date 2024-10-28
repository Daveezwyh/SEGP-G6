def remove_duplicates(df):
    """
    Remove rows that are completely identical (i.e., all columns are the same).
    
    :param df: Input dataframe
    :return: Dataframe with duplicate rows removed
    """
    # Use drop_duplicates() to remove duplicate rows based on all columns
    df_no_duplicates = df.drop_duplicates(keep='first')
    
    return df_no_duplicates

# # Example usage
# df_clean = remove_duplicates(df)
# print(df_clean)
