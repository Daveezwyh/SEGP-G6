import pandas as pd
from ScanResult import ScanResult

def clean_df_for_duplicates(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicated rows from the DataFrame based on user-selected actions.

    Purpose:
    --------
    This function checks the actions provided by the ScanResult object.
    If the "clean_df_for_duplicates" cleaner is activated, it removes duplicated rows
    while keeping the first occurrence.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing actions decided by the user.
    df : pd.DataFrame
        The DataFrame to be cleaned.

    Output:
    -------
    pd.DataFrame
        A new DataFrame with duplicated rows removed if the action is activated.

    Error Handling:
    ---------------
    If any unexpected error occurs, the function continues without interruption.
    """
    for action in scan_result.actions:
        try:
            # Check if the action matches this cleaner and is activated
            if action.cleaner == clean_df_for_duplicates.__name__ and action.activate:
                # Drop duplicated rows, keeping the first occurrence
                df = df.drop_duplicates(keep='first')
        except:
            # Ignore errors and continue to the next action
            continue
    return df


def fill_with_mean(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a column with the mean value.

    Purpose:
    --------
    This function checks if the "fill_with_mean" cleaner action is activated 
    in the provided ScanResult. If activated, it fills missing (NaN) values
    in the specified column with its mean.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing user-selected actions.
    df : pd.DataFrame
        The DataFrame containing missing values.

    Output:
    -------
    pd.DataFrame
        A DataFrame with missing values in the selected column filled by the mean.

    Error Handling:
    ---------------
    If any unexpected error occurs during filling, it will be silently ignored.
    """
    for action in scan_result.actions:
        try:
            # Check if the action is "fill_with_mean" and activated
            if action.cleaner == "fill_with_mean" and action.activate:
                # Safely retrieve the column name
                col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
                if col_name:
                    # Convert the column to numeric type and fill missing values with mean
                    df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                    df[col_name].fillna(df[col_name].mean(), inplace=True)
        except:
            # Ignore exceptions and continue
            continue
    return df


def fill_with_median(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a column with the median value.

    Purpose:
    --------
    This function checks if the "fill_with_median" cleaner action is activated 
    in the provided ScanResult. If activated, it fills missing (NaN) values
    in the specified column with its median.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing user-selected actions.
    df : pd.DataFrame
        The DataFrame containing missing values.

    Output:
    -------
    pd.DataFrame
        A DataFrame with missing values in the selected column filled by the median.

    Error Handling:
    ---------------
    If any unexpected error occurs during filling, it will be silently ignored.
    """
    for action in scan_result.actions:
        try:
            # Check if the action is "fill_with_median" and activated
            if action.cleaner == "fill_with_median" and action.activate:
                # Safely retrieve the column name
                col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
                if col_name:
                    # Convert the column to numeric type and fill missing values with median
                    df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                    df[col_name].fillna(df[col_name].median(), inplace=True)
        except:
            # Ignore exceptions and continue
            continue
    return df


def fill_with_mode(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a column with the most frequent (mode) value.

    Purpose:
    --------
    This function checks if the "fill_with_mode" cleaner action is activated 
    in the provided ScanResult. If activated, it fills missing (NaN) values
    in the specified column with the mode.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing user-selected actions.
    df : pd.DataFrame
        The DataFrame containing missing values.

    Output:
    -------
    pd.DataFrame
        A DataFrame with missing values in the selected column filled by the mode.

    Error Handling:
    ---------------
    If any unexpected error occurs during filling, it will be silently ignored.
    """
    for action in scan_result.actions:
        try:
            # Check if the action is "fill_with_mode" and activated
            if action.cleaner == "fill_with_mode" and action.activate:
                # Safely retrieve the column name
                col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
                if col_name:
                    # Find the mode value and fill missing values
                    mode_values = df[col_name].mode()
                    if not mode_values.empty:
                        df[col_name].fillna(mode_values[0], inplace=True)
        except:
            # Ignore exceptions and continue
            continue
    return df


def fill_with_ffill(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a column using forward fill (previous value).

    Purpose:
    --------
    This function checks if the "fill_with_ffill" cleaner action is activated 
    in the provided ScanResult. If activated, it fills missing (NaN) values
    with the last valid value before the missing entry.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing user-selected actions.
    df : pd.DataFrame
        The DataFrame containing missing values.

    Output:
    -------
    pd.DataFrame
        A DataFrame with missing values filled by forward filling.

    Error Handling:
    ---------------
    If any unexpected error occurs during filling, it will be silently ignored.
    """
    for action in scan_result.actions:
        try:
            # Check if the action is "fill_with_ffill" and activated
            if action.cleaner == "fill_with_ffill" and action.activate:
                # Safely retrieve the column name
                col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
                if col_name:
                    # Apply forward fill
                    df[col_name].fillna(method='ffill', inplace=True)
        except:
            # Ignore exceptions and continue
            continue
    return df


def fill_with_bfill(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a column using backward fill (next value).

    Purpose:
    --------
    This function checks if the "fill_with_bfill" cleaner action is activated 
    in the provided ScanResult. If activated, it fills missing (NaN) values
    with the next valid value after the missing entry.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing user-selected actions.
    df : pd.DataFrame
        The DataFrame containing missing values.

    Output:
    -------
    pd.DataFrame
        A DataFrame with missing values filled by backward filling.

    Error Handling:
    ---------------
    If any unexpected error occurs during filling, it will be silently ignored.
    """
    for action in scan_result.actions:
        try:
            # Check if the action is "fill_with_bfill" and activated
            if action.cleaner == "fill_with_bfill" and action.activate:
                # Safely retrieve the column name
                col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
                if col_name:
                    # Apply backward fill
                    df[col_name].fillna(method='bfill', inplace=True)
        except:
            # Ignore exceptions and continue
            continue
    return df


def delete_missing_rows(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Delete rows that contain missing values in a specific column.

    Purpose:
    --------
    This function checks if the "delete_missing_rows" cleaner action is activated 
    in the provided ScanResult. If activated, it deletes rows where the selected
    column has missing (NaN) values.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing user-selected actions.
    df : pd.DataFrame
        The DataFrame to delete rows from.

    Output:
    -------
    pd.DataFrame
        A DataFrame with rows containing missing values deleted.

    Error Handling:
    ---------------
    If any unexpected error occurs during row deletion, it will be silently ignored.
    """
    for action in scan_result.actions:
        try:
            # Check if the action is "delete_missing_rows" and activated
            if action.cleaner == "delete_missing_rows" and action.activate:
                # Safely retrieve the column name
                col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
                if col_name:
                    # Drop rows where the selected column is NaN
                    df.dropna(subset=[col_name], inplace=True)
        except:
            # Ignore exceptions and continue
            continue
    return df


##-------------------------------------------
# Deprecated
def clean_df_for_missing(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "fill_with_mean":
                df[scan_result.col].fillna(df[scan_result.col].mean(), inplace=True)
            elif action.cleaner == "fill_with_median":
                df[scan_result.col].fillna(df[scan_result.col].median(), inplace=True)
            elif action.cleaner == "fill_with_mode":
                df[scan_result.col].fillna(df[scan_result.col].mode()[0], inplace=True)
            elif action.cleaner == "fill_with_ffill":
                df[scan_result.col].fillna(method='ffill', inplace=True)
            elif action.cleaner == "fill_with_bfill":
                df[scan_result.col].fillna(method='bfill', inplace=True)
            elif action.cleaner == "delete_missing_rows":
                df.dropna(subset=[scan_result.col], inplace=True)
    return df
##-------------------------------------------


def clean_df_for_outlier(scan_result, df):
    """
    Delete the row identified as containing an outlier.

    Purpose:
    --------
    This function deletes the row at the specified index if the "clean_df_for_outlier"
    action is activated in the provided ScanResult.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing the row index and action.
    df : pd.DataFrame
        The DataFrame from which the row should be removed.

    Output:
    -------
    pd.DataFrame
        The DataFrame with the outlier row removed, if the action was activated.

    Error Handling:
    ---------------
    Any unexpected exception is silently ignored.
    """
    for action in scan_result.actions:
        try:
            if action.cleaner == "clean_df_for_outlier" and action.activate:
                if scan_result.row in df.index:
                    df.drop(index=scan_result.row, inplace=True)
        except:
            continue
    return df


def clean_df_cat_one_hot(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply one-hot encoding to the categorical column.

    Purpose:
    --------
    This function transforms the specified categorical column into binary indicator
    columns using one-hot encoding, and removes the original column.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object that includes the column name to encode.
    df : pd.DataFrame
        The DataFrame containing the categorical column.

    Output:
    -------
    pd.DataFrame
        A new DataFrame with one-hot encoded features.

    Error Handling:
    ---------------
    If encoding fails, the function skips and returns the unchanged DataFrame.
    """
    for action in scan_result.actions:
        try:
            if action.cleaner == "clean_df_cat_one_hot" and action.activate:
                col = scan_result.col
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
        except:
            continue
    return df


def clean_df_cat_label_encoding(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply label encoding to the categorical column.

    Purpose:
    --------
    This function replaces each unique category in the column with an integer code.
    The column is converted to 'category' type and its codes are used as values.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object that contains the column name.
    df : pd.DataFrame
        The DataFrame containing the categorical column.

    Output:
    -------
    pd.DataFrame
        A DataFrame where the specified column has been label encoded.

    Error Handling:
    ---------------
    Any exceptions are ignored, and the DataFrame is returned unchanged.
    """
    for action in scan_result.actions:
        try:
            if action.cleaner == "clean_df_cat_label_encoding" and action.activate:
                col = scan_result.col
                df[col] = df[col].astype('category').cat.codes
        except:
            continue
    return df


def clean_df_cat_drop(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop the specified categorical column.

    Purpose:
    --------
    This function removes the column identified in the ScanResult if the drop action is activated.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object indicating which column to drop.
    df : pd.DataFrame
        The DataFrame containing the column.

    Output:
    -------
    pd.DataFrame
        The DataFrame with the specified column dropped.

    Error Handling:
    ---------------
    If any issue occurs (e.g., column not found), the DataFrame is returned unchanged.
    """
    for action in scan_result.actions:
        try:
            if action.cleaner == "clean_df_cat_drop" and action.activate:
                df = df.drop(scan_result.col, axis=1)
        except:
            continue
    return df


##-------------------------------------------
# Deprecated
def clean_df_for_categorical(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        try:
            if action.activate:
                col = scan_result.col
                if col not in df.columns:
                    continue
                if action.cleaner == "one_hot":
                    dummies = pd.get_dummies(df[col], prefix=col)
                    df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
                elif action.cleaner == "label_encoding":
                    df[col] = df[col].astype('category').cat.codes
                elif action.cleaner == "drop":
                    df = df.drop(col, axis=1)
        except:
            continue
    return df
##-------------------------------------------

def apply_target_cleaning(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the user-selected action for handling a specific target value occurrence.

    Purpose:
    --------
    This function processes a target value found in the DataFrame based on the 
    selected user action, which could be:
    - Deleting the row containing the target value.
    - Deleting the column containing the target value.

    Inputs:
    -------
    scan_result : ScanResult
        The ScanResult object containing the row or column associated with the target value.
    df : pd.DataFrame
        The DataFrame to clean by deleting the row or column.

    Output:
    -------
    pd.DataFrame
        A DataFrame after applying the selected target value cleaning action.

    Error Handling:
    ---------------
    Any exceptions are ignored and the function continues silently.
    """
    for action in scan_result.actions:
        try:
            if action.activate:
                if action.cleaner == "delete_target_row":
                    # Delete the row containing the target value
                    df.drop(index=scan_result.row, inplace=True)
                elif action.cleaner == "delete_target_column":
                    # Delete the column containing the target value
                    df.drop(columns=[scan_result.col], inplace=True)
        except:
            continue
    return df
