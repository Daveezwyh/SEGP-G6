from typing import List
import pandas as pd
import numpy as np
from ScanResult import *

def scan_df_for_duplicates(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    duplicated_rows = df[df.duplicated(keep="first")]
    
    for index in duplicated_rows.index:
        actions = [
            ScanResultAction(
                title="Duplication Remover",
                description="Remove the duplicated rows",
                cleaner="clean_df_for_duplicates",
                cleaner_id= None,
                activate=True
            )
        ]
        
        scan_results.append(
            ScanResult(
                row=index,
                col=-1,  # No specific column as the entire row is duplicated
                message=f"Row {index + 1} is duplicated",
                action_type=SRActionType.DEFAULT,
                actions=actions
            )
        )
    
    return scan_results

def scan_df_for_missing(df: pd.DataFrame) -> List[ScanResult]:
    missing_matrix = df.isna()
    scan_results = []
    
    for row_idx, col_idx in zip(*np.where(missing_matrix)):
        col_name = df.columns[col_idx]
        
        # Check if the column is numeric
        if pd.api.types.is_numeric_dtype(df[col_name]):
            actions = [
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with mean value",
                    cleaner="fill_with_mean",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with median value",
                    cleaner="fill_with_median",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with most frequent value",
                    cleaner="fill_with_mode",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with previous value",
                    cleaner="fill_with_ffill",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with next value",
                    cleaner="fill_with_bfill",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Delete the row",
                    cleaner="delete_missing_rows",
                    cleaner_id=None,
                    activate=True
                )
            ]
        else:
            # For non-numeric columns, offer only mode, ffill, bfill, and delete
            actions = [
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with most frequent value",
                    cleaner="fill_with_mode",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with previous value",
                    cleaner="fill_with_ffill",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with next value",
                    cleaner="fill_with_bfill",
                    cleaner_id=None,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Delete the row",
                    cleaner="delete_missing_rows",
                    cleaner_id=None,
                    activate=True
                )
            ]
        
        scan_results.append(
            ScanResult(
                row=row_idx,
                col=col_name,
                message=f"Missing value in row {row_idx+1}, column '{col_name}'",
                action_type=SRActionType.DEFAULT,
                actions=actions
            )
        )
    
    return scan_results


def scan_df_for_outliers(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    
    for col in df.select_dtypes(include=[np.number]):
        col_data = df[col].dropna()
        if col_data.empty:
            continue

        q1, q3 = col_data.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = (col_data < lower_bound) | (col_data > upper_bound)
        
        for idx in col_data[outliers].index:
            actions = [
                ScanResultAction(
                    title="Outlier Handler",
                    description="Delete the outlier",
                    cleaner="delete_outlier",
                    cleaner_id=None,
                    activate=True
                )
            ]
            
            scan_results.append(
                ScanResult(
                    row=idx,
                    col=col,
                    message=f"Outlier detected in column '{col}' at row {idx+1}",
                    action_type=SRActionType.DEFAULT,
                    actions=actions
                )
            )
    
    return scan_results

def scan_df_for_categorical(df: pd.DataFrame, categorical_dtypes: list = ['object', 'category', 'bool']) -> List[ScanResult]:
    scan_results = []
    max_categories = int(len(df) * 0.1)
    
    non_numeric_cols = df.select_dtypes(include=categorical_dtypes)

    for col in non_numeric_cols.columns:
        if df[col].dropna().size == 0:
            continue
        
        unique_count = df[col].nunique()
        if unique_count > max_categories:
            continue
        
        categories = df[col].dropna().unique()
        categories_str = ", ".join(map(str, categories[:10]))
        if len(categories) > 10:
            categories_str += f"... (Total {len(categories)} categories)"
        
        actions = [
            ScanResultAction(
                title="Categorical Encoder",
                description="Apply one-hot encoding",
                cleaner="one_hot",
                cleaner_id=None,
                activate=True
            ),
            ScanResultAction(
                title="Categorical Encoder",
                description="Apply label encoding",
                cleaner="label_encoding",
                cleaner_id=None,
                activate=True
            ),
            ScanResultAction(
                title="Categorical Encoder",
                description="Drop the column",
                cleaner="drop",
                cleaner_id=None,
                activate=True
            )
        ]
        
        scan_results.append(
            ScanResult(
                row=-1,
                col=col,
                message=f"Categorical feature '{col}' detected with {unique_count} categories: {categories_str}",
                action_type=SRActionType.DEFAULT,
                actions=actions
            )
        )
    
    return scan_results

def scan_df_for_target(df: pd.DataFrame, target) -> List[ScanResult]:
    scan_results = []
    matches = df.isin([target])
    
    for row_idx, col_idx in zip(*np.where(matches)):
        col_name = df.columns[col_idx]
        
        actions = [
            ScanResultAction(
                title=f"Handle '{target}' value",
                description=f"Handle the '{target}' value in column '{col_name}'",
                cleaner="handle_target",
                activate=True,
            ),
            ScanResultAction(
                title="Delete row",
                description=f"Delete row {row_idx+1} because it contains '{target}'",
                cleaner="delete_target_row",
                activate=True,
            ),
            ScanResultAction(
                title="Delete column",
                description=f"Delete column '{col_name}' because it contains '{target}'",
                cleaner="delete_target_column",
                activate=True,
            )
        ]
        
        scan_results.append(
            ScanResult(
                row=row_idx,
                col=col_name,
                message=f"Target value '{target}' found in row {row_idx+1}, column '{col_name}'",
                action_type=SRActionType.DEFAULT,
                actions=actions
            )
        )
    
    return scan_results

