def remove_rows(df, index_to_drop):
    """
    Remove a specific row from the dataframe based on the index.
    
    :param df: Input dataframe
    :param index_to_drop: The index of the row to be removed
    :return: Dataframe with the specific row removed
    """
    # Drop the row with the specified index
    df_cleaned = df.drop(index=index_to_drop)
    
    return df_cleaned
