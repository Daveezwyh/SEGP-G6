from typing import List
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

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

def scan_df_for_duplicates(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    duplicated_rows = df[df.duplicated(keep=False)]

    for index in duplicated_rows.index:
        for method in {"delete","keep"}:
            scan_results.append(
                ScanResult(
                    row=index,
                    col=-1,  # No specific column as the entire row is duplicated
                    message=f"Row {index + 1} is duplicated",
                    cleaner="duplicate_removal",
                    method=method,
                    activate=True
                )
            )

    return scan_results

def scan_df_for_missing(df: pd.DataFrame) -> List[ScanResult]:
    missing_matrix = df.isna()
    scan_results = []

    for row_idx, col_idx in zip(*np.where(missing_matrix)):
        col_name = df.columns[col_idx]

        for method in {"mean", "median", "mode", "delete"}:
            scan_results.append(
                ScanResult(
                    row=row_idx,
                    col=col_name,
                    message=f"Missing value in row {row_idx+1}, column '{col_name}'",
                    cleaner="fill_missing",
                    method=method,
                    activate=True
                )
            )
    return scan_results

import numpy as np
import pandas as pd
from typing import List
from sklearn.ensemble import IsolationForest

def scan_df_for_outliers(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []

    # Automatically calculate contamination rate (proportion of anomalies)
    def auto_contamination(n):
        return min(0.1, max(0.01, 5 / np.log(n)))

    # Iterate over numerical columns
    for col in df.select_dtypes(include=[np.number]):
        col_data = df[col].dropna()

        if col_data.empty:
            continue

        # Compute IQR (Interquartile Range)
        q1, q3 = col_data.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers_iqr = (col_data < lower_bound) | (col_data > upper_bound)

        # Train Isolation Forest
        contamination = auto_contamination(len(col_data))
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        iso_preds = iso_forest.fit_predict(col_data.to_frame()) == -1  # -1 indicates anomaly

        # Combine both methods
        combined_outliers = outliers_iqr & iso_preds  # Detected as outliers by both methods
        all_outliers = outliers_iqr | iso_preds  # Detected as outliers by either method

        # Record severe outliers detected by both IQR and Isolation Forest
        for idx in col_data[combined_outliers].index:
            for method in {"delete", "keep"}:
                scan_results.append(
                    ScanResult(
                        row=idx,
                        col=df.columns.get_loc(col),
                        message=f"Severe outlier in {col} (value={df.at[idx, col]:.2f}) - Detected by IQR & Isolation Forest",
                        cleaner="outlier_handling",
                        method=method,
                        activate=True
                    )
                )

        # Record possible outliers detected by either IQR or Isolation Forest
        for idx in col_data[all_outliers & ~combined_outliers].index:
            for method in {"delete", "keep"}:
                scan_results.append(
                    ScanResult(
                        row=idx,
                        col=df.columns.get_loc(col),
                        message=f"Possible outlier in {col} (value={df.at[idx, col]:.2f}) - Detected by IQR or Isolation Forest",
                        cleaner="outlier_handling",
                        method=method,
                        activate=True
                    )
                )

    # **Multivariate anomaly detection**
    numerical_df = df.select_dtypes(include=[np.number]).dropna()
    if len(numerical_df) > 10:
        contamination = auto_contamination(len(numerical_df))
        clf = IsolationForest(contamination=contamination, random_state=42,
                              n_estimators=min(100, len(numerical_df) // 10))

        outlier_flags = clf.fit_predict(numerical_df) == -1  # -1 indicates anomaly

        for idx in numerical_df[outlier_flags].index:
            for method in {"delete", "keep"}:
                scan_results.append(
                    ScanResult(
                        row=idx,
                        col=-1,
                        message="Multivariate anomaly detected",
                        cleaner="multivariate_outlier",
                        method=method,
                        activate=True
                    )
                )

    return scan_results

def scan_df_for_categorical(df: pd.DataFrame, 
                            categorical_dtypes: list = ['object', 'category', 'bool']) -> List[ScanResult]:
    scan_results = []
    max_categories = int(len(df) * 0.01)
    
    # Select non-numeric columns
    non_numeric_cols = df.select_dtypes(include=categorical_dtypes)

    for col in non_numeric_cols.columns:
        # Skip empty columns
        if df[col].dropna().size == 0:
            continue
        
        # Calculate the number of unique values
        unique_count = df[col].nunique()
        
        # Filter out high-cardinality columns (to avoid treating free text as categorical)
        is_high_cardinality = unique_count > max_categories
        if is_high_cardinality:
            continue
        
        try:
            categories = df[col].dropna().unique()
            categories_str = ", ".join(map(str, categories[:10]))
            if len(categories) > 10:
                categories_str += f"... (Total {len(categories)} categories)"
            
            for method in {"one_hot", "label_encoding"}:
                scan_results.append(
                    ScanResult(
                        row=-1,  # -1 indicates that the entire column needs processing
                        col=col,  # Store column name directly
                        message=(f"Categorical feature '{col}' detected with {unique_count} categories: {categories_str}"),
                        cleaner="categorical_features_encoded",
                        method=method,
                        activate=True
                    )
                )
        except Exception as e:
            print(f"Error processing column {col}: {str(e)}")
            continue

    return scan_results