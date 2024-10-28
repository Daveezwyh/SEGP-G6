import numpy as np

def remove_outliers_zscore(df, column, threshold=3):
    """
    Remove outliers based on Z-score.
    
    :param df: Input dataframe
    :param column: The column to check for outliers
    :param threshold: Z-score threshold for identifying outliers (default is 3)
    :return: Dataframe without outliers
    """
    mean = df[column].mean()
    std = df[column].std()
    
    # Calculate Z-scores
    z_scores = (df[column] - mean) / std
    # Filter data where Z-score is within the threshold
    df_no_outliers = df[np.abs(z_scores) < threshold] # Normal data
    df_outliers = df[np.abs(z_scores) >= threshold]  # Outliers
    
    return df_no_outliers, df_outliers


def remove_outliers_iqr(df, column):
    """
    Remove outliers based on the Interquartile Range (IQR).
    
    :param df: Input dataframe
    :param column: The column to check for outliers
    :return: Dataframe without outliers
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Define the lower and upper bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Filter data within the bounds
    df_no_outliers = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]  # Normal data
    df_outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]  # Outliers
    
    return df_no_outliers,df_outliers


def remove_outliers_percentile(df, column, lower_percentile=0.01, upper_percentile=0.99):
    """
    Remove outliers based on percentiles.
    
    :param df: Input dataframe
    :param column: The column to check for outliers
    :param lower_percentile: Lower percentile threshold (default is 1%)
    :param upper_percentile: Upper percentile threshold (default is 99%)
    :return: Dataframe without outliers
    """
    lower_bound = df[column].quantile(lower_percentile)
    upper_bound = df[column].quantile(upper_percentile)
    
    # Filter data between the lower and upper percentile bounds
    df_no_outliers = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]  # Normal data
    df_outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]  # Outliers
    
    return df_no_outliers, df_outliers

# # Example usage
# df_clean, df_outliers = remove_outliers(df, 'column_name')
