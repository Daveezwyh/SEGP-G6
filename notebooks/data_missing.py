def find_missing_values(df):
    """
    Find all rows with missing values in the DataFrame.
    
    :param df: Input DataFrame
    :return: DataFrame with only rows that contain missing values
    """
    df_with_missing = df[df.isnull().any(axis=1)]
    
    return df_with_missing

def fill_missing_with_mean(df, column):
    """
    Fill missing values in a column with the mean of that column.
    
    :param df: Input dataframe
    :param column: The column to fill missing values in
    :return: Dataframe with filled missing values
    """
    df[column].fillna(df[column].mean(), inplace=True)
    return df

def fill_missing_with_median(df, column):
    """
    Fill missing values in a column with the median of that column.
    
    :param df: Input dataframe
    :param column: The column to fill missing values in
    :return: Dataframe with filled missing values
    """
    df[column].fillna(df[column].median(), inplace=True)
    return df

def fill_missing_with_ffill(df, column):
    """
    Fill missing values using forward fill (previous value).
    
    :param df: Input dataframe
    :param column: The column to fill missing values in
    :return: Dataframe with filled missing values
    """
    df[column].fillna(method='ffill', inplace=True)
    return df

def fill_missing_with_bfill(df, column):
    """
    Fill missing values using backward fill (next value).
    
    :param df: Input dataframe
    :param column: The column to fill missing values in
    :return: Dataframe with filled missing values
    """
    df[column].fillna(method='bfill', inplace=True)
    return df

def fill_missing_with_constant(df, column, constant):
    """
    Fill missing values with a specified constant value.
    
    :param df: Input dataframe
    :param column: The column to fill missing values in
    :param constant: The constant value to use for filling
    :return: Dataframe with filled missing values
    """
    df[column].fillna(constant, inplace=True)
    return df

# # Fill missing values in a numeric column with mean
# df = fill_missing_with_mean(df, 'numeric_column')

# # Fill missing values in a time series column with forward fill
# df = fill_missing_with_ffill(df, 'time_series_column')

# # Fill missing values in a categorical column with a specific constant
# df = fill_missing_with_constant(df, 'categorical_column', constant='Unknown')
