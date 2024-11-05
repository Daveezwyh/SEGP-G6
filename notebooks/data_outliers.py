import numpy as np

def find_outliers_zscore(df, column, threshold=3):
    """
    Find outliers based on Z-score.
    
    :param df: Input dataframe
    :param column: The column to check for outliers
    :param threshold: Z-score threshold for identifying outliers (default is 3)
    :return: Dataframe with outliers
    """
    mean = df[column].mean()
    std = df[column].std()
    
    # Calculate Z-scores
    z_scores = (df[column] - mean) / std
    # Filter data where Z-score is beyond the threshold
    df_outliers = df[np.abs(z_scores) >= threshold]  # Outliers
    
    return df_outliers


def find_outliers_iqr(df, column):
    """
    Find outliers based on the Interquartile Range (IQR).
    
    :param df: Input dataframe
    :param column: The column to check for outliers
    :return: Dataframe with outliers
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Define the lower and upper bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Filter data outside the bounds
    df_outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]  # Outliers
    
    return df_outliers


def find_outliers_percentile(df, column, lower_percentile=0.01, upper_percentile=0.99):
    """
    Find outliers based on percentiles.
    
    :param df: Input dataframe
    :param column: The column to check for outliers
    :param lower_percentile: Lower percentile threshold (default is 1%)
    :param upper_percentile: Upper percentile threshold (default is 99%)
    :return: Dataframe with outliers
    """
    lower_bound = df[column].quantile(lower_percentile)
    upper_bound = df[column].quantile(upper_percentile)
    
    # Filter data outside the lower and upper percentile bounds
    df_outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]  # Outliers
    
    return df_outliers
