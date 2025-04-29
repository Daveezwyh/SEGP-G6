from typing import List
import pandas as pd
import numpy as np
from ScanResult import *

def scan_df_for_duplicates(df: pd.DataFrame) -> List[ScanResult]:
    """
    Scan the given DataFrame for duplicated rows.

    Purpose:
    --------
    This function identifies rows in the DataFrame that are exact duplicates of previous rows.
    It generates a list of ScanResult objects, each representing a duplicated row and providing
    an action (removal of duplication) that can be taken.

    Input:
    ------
    df : pd.DataFrame
        The DataFrame to be scanned for duplicated rows.

    Output:
    -------
    List[ScanResult]
        A list of ScanResult objects indicating where duplicated rows exist
        and suggesting cleaning actions.

    Error Handling:
    ---------------
    If any unexpected exception occurs during scanning (e.g., invalid DataFrame structure),
    the function safely returns an empty list without crashing.
    """
    scan_results = []  # Initialize an empty list to store scan results

    try:
        # Drop columns where all values are NaN to clean the DataFrame before scanning
        df = df.dropna(axis=1, how='all')

        # Find duplicated rows (keep the first occurrence as original)
        duplicated_rows = df[df.duplicated(keep="first")]

    except Exception:
        # If any error occurs, return an empty scan result list
        return scan_results

    # Iterate over the indices of duplicated rows
    for index in duplicated_rows.index:
        actions = [
            ScanResultAction(
                title="Duplication Remover",  # Name of the cleaning action
                description="Remove the duplicated rows",  # Description for the user
                cleaner="clean_df_for_duplicates",  # Cleaner function to be called
                cleaner_id=None,  # No specific cleaner ID
                activate=True  # Mark this cleaning action as activated by default
            )
        ]

        # Create a ScanResult for each duplicated row
        scan_results.append(
            ScanResult(
                row=index,  # Row index where duplication is detected
                col=-1,  # Set column index as -1 because the entire row is duplicated
                message=f"Row {index + 1} is duplicated",  # Message describing the issue
                action_type=SRActionType.ONE_MANDATORY,  # Action type is mandatory for user
                actions=actions  # Attach the cleaning actions
            )
        )

    # Return the list of ScanResults
    return scan_results


def scan_df_for_missing(df: pd.DataFrame) -> List[ScanResult]:
    """
    Scan the given DataFrame for missing values.

    Purpose:
    --------
    This function identifies missing (NaN) values within the DataFrame
    and suggests appropriate cleaning actions depending on the feature type.
    Different filling or removal strategies are provided based on whether 
    the missing value is located in a numeric or non-numeric column.

    Input:
    ------
    df : pd.DataFrame
        The DataFrame to be scanned for missing values.

    Output:
    -------
    List[ScanResult]
        A list of ScanResult objects, each representing a missing value and
        containing a set of cleaning actions for the user to choose.

    Error Handling:
    ---------------
    If any unexpected exception occurs during the scanning process
    (e.g., invalid input), the function returns an empty list.
    """
    scan_results = []  # Initialize an empty list to collect scan results

    try:
        # Generate a boolean matrix where True indicates missing values
        missing_matrix = df.isna()
    except Exception:
        # In case of failure (e.g., if df is not a DataFrame), return empty
        return scan_results

    # Iterate over all missing value positions (row index, column index)
    for row_idx, col_idx in zip(*np.where(missing_matrix)):
        try:
            # Get the column name for the current missing value
            col_name = df.columns[col_idx]
        
            # Check if the column is numeric
            if pd.api.types.is_numeric_dtype(df[col_name]):
                # Define actions for missing numeric values
                actions = [
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with mean value",  # Recommended default
                        cleaner="fill_with_mean",
                        cleaner_id=None,
                        activate=True  # Default action is activated
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with median value",
                        cleaner="fill_with_median",
                        cleaner_id=None,
                        activate=False
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with most frequent value (mode)",
                        cleaner="fill_with_mode",
                        cleaner_id=None,
                        activate=False
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with previous value (forward fill)",
                        cleaner="fill_with_ffill",
                        cleaner_id=None,
                        activate=False
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with next value (backward fill)",
                        cleaner="fill_with_bfill",
                        cleaner_id=None,
                        activate=False
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Delete the row containing missing value",
                        cleaner="delete_missing_rows",
                        cleaner_id=None,
                        activate=False
                    )
                ]
            else:
                # Define actions for missing values in non-numeric columns
                actions = [
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with most frequent value (mode)",
                        cleaner="fill_with_mode",
                        cleaner_id=None,
                        activate=True
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with previous value (forward fill)",
                        cleaner="fill_with_ffill",
                        cleaner_id=None,
                        activate=False
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Fill with next value (backward fill)",
                        cleaner="fill_with_bfill",
                        cleaner_id=None,
                        activate=False
                    ),
                    ScanResultAction(
                        title="Missing Value Filler",
                        description="Delete the row containing missing value",
                        cleaner="delete_missing_rows",
                        cleaner_id=None,
                        activate=False
                    )
                ]
        
            # Create and append a ScanResult for the missing value detected
            scan_results.append(
                ScanResult(
                    row=row_idx,  # The row where missing value occurs
                    col=col_idx,  # The column index
                    message=f"Missing value in row {row_idx+1}, column '{col_name}'",  # Human-readable message
                    action_type=SRActionType.ONE_MANDATORY,  # User must select one cleaning action
                    actions=actions  # Suggested actions for handling missing value
                )
            )
        except:
            # Ignore any unexpected error and continue scanning
            continue

    # Return the complete list of missing value findings
    return scan_results


def scan_df_for_outliers(df: pd.DataFrame) -> List[ScanResult]:
    """
    Scan the given DataFrame for outliers based on the IQR (Interquartile Range) method.

    Purpose:
    --------
    This function detects statistical outliers in numerical columns of the DataFrame
    using the IQR rule (values below Q1 - 1.5*IQR or above Q3 + 1.5*IQR are considered outliers).
    It generates a ScanResult for each detected outlier with a suggested action to remove it.

    Input:
    ------
    df : pd.DataFrame
        The DataFrame to be scanned for outliers.

    Output:
    -------
    List[ScanResult]
        A list of ScanResult objects indicating outlier positions
        and offering cleaning actions (deleting the outlier row).

    Error Handling:
    ---------------
    If any unexpected exception occurs during scanning, 
    the function safely continues without interruption.
    """
    scan_results = []  # Initialize an empty list to store scan results

    try:
        # Loop through all numeric columns only
        for col in df.select_dtypes(include=[np.number]):
            # Drop missing values before outlier detection
            col_data = df[col].dropna()
            if col_data.empty:
                # Skip if the column has no valid data
                continue

            # Calculate first quartile (Q1) and third quartile (Q3)
            q1, q3 = col_data.quantile([0.25, 0.75])
            iqr = q3 - q1  # Interquartile Range

            # Define lower and upper bounds for non-outlier data
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Identify outliers outside the bounds
            outliers = (col_data < lower_bound) | (col_data > upper_bound)

            # Loop through each detected outlier
            for idx in col_data[outliers].index:
                # Get column index for the ScanResult
                col_idx = df.columns.get_loc(col)

                # Define a single mandatory cleaning action: delete the outlier
                actions = [
                    ScanResultAction(
                        title="Outlier Handler",  # Name of the action
                        description="Delete the outlier",  # Description for UI
                        cleaner="clean_df_for_outlier",  # Corresponding cleaning function name
                        cleaner_id=None,
                        activate=True  # Default action is activated
                    )
                ]

                # Create and append a ScanResult for each outlier
                scan_results.append(
                    ScanResult(
                        row=idx,  # Row index where the outlier is found
                        col=col_idx,  # Column index where the outlier is found
                        message=f"Outlier detected in column '{col}' at row {idx+1}",  # Message to user
                        action_type=SRActionType.ONE_MANDATORY,  # Action must be taken
                        actions=actions  # Associated cleaning actions
                    )
                )
    except:
        # Catch any exception silently and continue
        pass

    # Return the list of detected outlier issues
    return scan_results


def scan_df_for_categorical(df: pd.DataFrame) -> List[ScanResult]:
    """
    Scan the given DataFrame for categorical columns.

    Purpose:
    --------
    This function detects categorical-type columns (object, category, or bool),
    and creates ScanResult objects suggesting appropriate encoding actions 
    (one-hot encoding, label encoding, or column removal).

    Input:
    ------
    df : pd.DataFrame
        The DataFrame to be scanned for categorical features.

    Output:
    -------
    List[ScanResult]
        A list of ScanResult objects indicating categorical columns 
        and offering different encoding or dropping strategies.

    Error Handling:
    ---------------
    If any unexpected exception occurs during the scanning process,
    the function safely returns an empty list.
    """
    scan_results = []  # Initialize an empty list to store scan results

    try:
        # Define the types considered as categorical
        categorical_dtypes = ['object', 'category', 'bool']
        # Select columns with categorical data types
        non_numeric_cols = df.select_dtypes(include=categorical_dtypes)
    except Exception:
        # Return empty list if selection fails
        return scan_results

    # Iterate over each detected categorical column
    for col in non_numeric_cols.columns:
        # Skip columns where all values are missing
        if df[col].dropna().size == 0:
            continue
        
        # Count the number of unique categories
        unique_count = df[col].nunique()

        # Extract unique categories (up to first 10 for display)
        categories = df[col].dropna().unique()
        categories_str = ", ".join(map(str, categories[:10]))
        if len(categories) > 10:
            categories_str += f"... (Total {len(categories)} categories)"

        # Define actions for encoding or dropping the categorical feature
        actions = [
            ScanResultAction(
                title="Categorical Encoder",
                description="Apply one-hot encoding",
                cleaner="clean_df_cat_one_hot",
                cleaner_id=None,
                activate=True  # Default action is activated
            ),
            ScanResultAction(
                title="Categorical Encoder",
                description="Apply label encoding",
                cleaner="clean_df_cat_label_encoding",
                cleaner_id=None,
                activate=False
            ),
            ScanResultAction(
                title="Categorical Encoder",
                description="Drop the column",
                cleaner="clean_df_cat_drop",
                cleaner_id=None,
                activate=False
            )
        ]

        # Append the scan result for this categorical feature
        scan_results.append(
            ScanResult(
                row=-1,  # No specific row; applies to the whole column
                col=col,  # Column name where the categorical feature is detected
                message=f"Categorical feature '{col}' detected with {unique_count} categories: {categories_str}",  # User-friendly message
                action_type=SRActionType.ONE_MANDATORY,  # One action must be taken
                actions=actions  # Associated encoding or dropping actions
            )
        )
    
    # Return all scan results for categorical features
    return scan_results


def scan_df_for_target(df: pd.DataFrame, target) -> List[ScanResult]:
    """
    Scan the given DataFrame for occurrences of a specific target value.

    Purpose:
    --------
    This function finds all cells in the DataFrame that match the given target value,
    and generates ScanResult objects suggesting appropriate handling actions
    (handling the target value, deleting the row, or deleting the column).

    Input:
    ------
    df : pd.DataFrame
        The DataFrame to scan.
    target : Any
        The specific value to search for in the DataFrame.

    Output:
    -------
    List[ScanResult]
        A list of ScanResult objects indicating locations of the target value 
        and offering possible remediation actions.

    Error Handling:
    ---------------
    If any unexpected exception occurs, the function proceeds silently.
    """
    scan_results = []  # Initialize an empty list to collect scan results

    try:
        # Create a boolean matrix where True means a match with the target value
        matches = df.isin([target])

        # Iterate over all positions where the target value appears
        for row_idx, col_idx in zip(*np.where(matches)):
            # Get the column name for the matched cell
            col_name = df.columns[col_idx]

            # Define actions for handling the found target
            actions = [
                ScanResultAction(
                    title=f"Handle '{target}' value",
                    description=f"Handle the '{target}' value in column '{col_name}'",
                    cleaner="handle_target",
                    activate=True  # Default to activated handling
                ),
                ScanResultAction(
                    title="Delete row",
                    description=f"Delete row {row_idx+1} because it contains '{target}'",
                    cleaner="delete_target_row",
                    activate=True
                ),
                ScanResultAction(
                    title="Delete column",
                    description=f"Delete column '{col_name}' because it contains '{target}'",
                    cleaner="delete_target_column",
                    activate=True
                )
            ]

            # Append the scan result for this occurrence
            scan_results.append(
                ScanResult(
                    row=row_idx,  # Row index where target is found
                    col=col_name,  # Column name where target is found
                    message=f"Target value '{target}' found in row {row_idx+1}, column '{col_name}'",  # User-readable message
                    action_type=SRActionType.MANY_OPTIONAL,  # User can choose multiple actions
                    actions=actions  # Associated remediation actions
                )
            )
    except Exception:
        # Ignore exceptions and continue
        pass

    # Return all scan results for found target values
    return scan_results