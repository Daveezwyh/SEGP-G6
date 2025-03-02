from typing import List
import pandas as pd
import numpy as np
from ScanResult import *

def scan_df_for_duplicates(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    duplicated_rows = df[df.duplicated(keep="first")]
    
    cleaner_id = 0
    for index in duplicated_rows.index:
        actions = [
            ScanResultAction(
                title="Duplication Remover",
                description="Remove the duplicated rows",
                cleaner="remove",
                cleaner_id=cleaner_id,
                activate=True
            ),
            ScanResultAction(
                title="Duplication Remover",
                description="Keep the duplicated rows",
                cleaner="keep",
                cleaner_id=cleaner_id + 1,
                activate=True
            )
        ]
        cleaner_id += 2  # Increment ID for next set of actions
        
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
    
    cleaner_id = 0
    for row_idx, col_idx in zip(*np.where(missing_matrix)):
        col_name = df.columns[col_idx]
        
        # Check if the column is numeric
        if pd.api.types.is_numeric_dtype(df[col_name]):
            actions = [
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with mean value",
                    cleaner="mean",
                    cleaner_id=cleaner_id,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with median value",
                    cleaner="median",
                    cleaner_id=cleaner_id + 1,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with most frequent value",
                    cleaner="mode",
                    cleaner_id=cleaner_id + 2,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with previous value",
                    cleaner="ffill",
                    cleaner_id=cleaner_id + 3,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with next value",
                    cleaner="bfill",
                    cleaner_id=cleaner_id + 4,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Delete the row",
                    cleaner="delete",
                    cleaner_id=cleaner_id + 5,
                    activate=True
                )
            ]
            cleaner_id += 6
        else:
            # For non-numeric columns, offer only mode, ffill, bfill, and delete
            actions = [
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with most frequent value",
                    cleaner="mode",
                    cleaner_id=cleaner_id,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with previous value",
                    cleaner="ffill",
                    cleaner_id=cleaner_id + 1,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Fill with next value",
                    cleaner="bfill",
                    cleaner_id=cleaner_id + 2,
                    activate=True
                ),
                ScanResultAction(
                    title="Missing Value Filler",
                    description="Delete the row",
                    cleaner="delete",
                    cleaner_id=cleaner_id + 3,
                    activate=True
                )
            ]
            cleaner_id += 4
        
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
    
    def auto_contamination(n):
        return min(0.1, max(0.01, 5 / np.log(n)))
    
    cleaner_id = 0
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
                    cleaner="delete",
                    cleaner_id=cleaner_id,
                    activate=True
                ),
                ScanResultAction(
                    title="Outlier Handler",
                    description="Keep the outlier",
                    cleaner="keep",
                    cleaner_id=cleaner_id + 1,
                    activate=True
                )
            ]
            cleaner_id += 2
            
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

def scan_df_for_categorical(df: pd.DataFrame, 
                            categorical_dtypes: list = ['object', 'category', 'bool']) -> List[ScanResult]:
    scan_results = []
    max_categories = int(len(df) * 0.01)
    
    non_numeric_cols = df.select_dtypes(include=categorical_dtypes)
    cleaner_id = 0

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
                cleaner_id=cleaner_id,
                activate=True
            ),
            ScanResultAction(
                title="Categorical Encoder",
                description="Apply label encoding",
                cleaner="label_encoding",
                cleaner_id=cleaner_id + 1,
                activate=True
            ),
            ScanResultAction(
                title="Categorical Encoder",
                description="Drop the column",
                cleaner="drop",
                cleaner_id=cleaner_id + 2,
                activate=True
            ),
            ScanResultAction(
                title="Categorical Encoder",
                description="Keep the column",
                cleaner="keep",
                cleaner_id=cleaner_id + 3,
                activate=True
            )
        ]
        cleaner_id += 4
        
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
        scan_results.append(
            ScanResult(
                row=row_idx,
                col=col_name,
                message=f"Target value '{target}' found in row {row_idx+1}, column '{col_name}'",
                action_type=SRActionType.DEFAULT,
                actions=[
                    ScanResultAction(
                        title="Handle '{target}'",
                        description="Handle the '{target}' value",
                        cleaner="handle_target",
                        activate=True,
                    )
                ]
            )
        )
    
    return scan_results
