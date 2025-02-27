import numpy as np
import pandas as pd
from typing import List
from sklearn.preprocessing import LabelEncoder

class ScanResult:
    def __init__(self, row=0, col=0, message="", cleaner="", method="", activate=False):
        self.row = row
        self.col = col
        self.message = message
        self.cleaner = cleaner
        self.method = method
        self.activate = activate

    def __repr__(self):
        return f"ScanResult(row={self.row}, col={self.col}, message='{self.message}', cleaner='{self.cleaner}', method='{self.method}', activate={self.activate})"

def apply_scan_results(df: pd.DataFrame, scan_results: List[ScanResult]) -> pd.DataFrame:
    df = df.copy()  # Avoid modifying the original DataFrame
    
    # Group scan results by row and column to ensure only one method is applied per issue
    unique_scan_results = {}
    for result in scan_results:
        if result.activate:
            key = (result.row, result.col)
            unique_scan_results[key] = result  # Keep only the last selected method
    
    for (row, col), result in unique_scan_results.items():
        if result.cleaner == "duplicate_removal" and result.method == "delete":
            df.drop(index=row, inplace=True)
        elif result.cleaner == "fill_missing":
            if result.method == "mean":
                df.iloc[row, col] = df.iloc[:, col].mean()
            elif result.method == "median":
                df.iloc[row, col] = df.iloc[:, col].median()
            elif result.method == "mode":
                df.iloc[row, col] = df.iloc[:, col].mode()[0]
            elif result.method == "delete":
                df.drop(index=row, inplace=True)
        elif result.cleaner == "outlier_handling" and result.method == "delete":
            df.drop(index=row, inplace=True)
        elif result.cleaner == "multivariate_outlier" and result.method == "delete":
            df.drop(index=row, inplace=True)
        elif result.cleaner == "categorical_features_encoded":
            if result.method == "one_hot":
                df = pd.get_dummies(df, columns=[col], prefix=[col])
            elif result.method == "label_encoding":
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
            elif result.method == "drop":
                columns_to_drop = [df.columns[col] for col in columns_to_drop]
                return df.drop(columns=columns_to_drop, errors='ignore')
    
    df.reset_index(drop=True, inplace=True)  # Reset index after deletions
    return df