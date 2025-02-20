from autoclean.scanners.result import ScanResult, ScannerAttribute
import pandas as pd
from typing import List
from sklearn.ensemble import IsolationForest

def scan_df_for_duplicates(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    duplicated_rows = df[df.duplicated()]

    for index in duplicated_rows.index:
        scan_results.append(
            ScanResult(
                row=index,
                col=-1,  # No specific column as the entire row is duplicated
                message=f"Row {index + 1} is duplicated",
            )
        )

    return scan_results

def scan_df_for_missing(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []

    for row_index, row in df.iterrows():
        for col_index, col_name in enumerate(df.columns):
            if pd.isna(row[col_name]):
                scan_results.append(
                    ScanResult(
                        row=row_index,
                        col=col_index,
                        message=f"Missing value in row {row_index + 1}, column {col_name}",
                    )
                )

    return scan_results

def scan_df_for_outliers(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    X = df.select_dtypes(include=[float, int])

    if X.empty:
        return []
    
    X_no_missing = X.dropna()

    iforest = IsolationForest(
        n_estimators=100, 
        max_samples='auto',
        contamination=0.05, 
        max_features=X_no_missing.shape[1],
        bootstrap=False, 
        n_jobs=-1, 
        random_state=1
    )
    
    labels = iforest.fit_predict(X_no_missing)
    outlier_indices = X_no_missing.index[labels == -1]

    for idx in outlier_indices:
        scan_results.append(
            ScanResult(
                row=idx,
                col=-1,
                message=f"Row {idx + 1} contains an outlier",
            )
        )

    return scan_results