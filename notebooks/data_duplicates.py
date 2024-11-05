def find_duplicates(df):
    """
    Find rows that are completely identical (i.e., all columns are the same).
    
    :param df: Input dataframe
    :return: Dataframe with only duplicate rows
    """
    # Use duplicated() with keep=False to identify all duplicated rows
    df_duplicates = df[df.duplicated(keep=False)]
    
    return df_duplicates
