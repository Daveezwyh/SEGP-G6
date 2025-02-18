from ScanResult import ScanResult  # Importing the ScanResult class
from typing import List
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from rapidfuzz import fuzz

def scan_df_for_duplicates(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    duplicated_rows = df[df.duplicated()]

    for index in duplicated_rows.index:
        scan_results.append(
            ScanResult(
                row=index,
                col=-1,  # No specific column as the entire row is duplicated
                message=f"Row {index + 1} is duplicated",
                cleaner="duplicate_removal",
                activate=True
            )
        )

    return scan_results

def scan_df_for_missing(df: pd.DataFrame) -> List[ScanResult]:
    missing_matrix = df.isna()
    return [
        ScanResult(
            row=row_idx,
            col=df.columns[col_idx],
            message=f"Missing value in row {row_idx+1}, column {col_idx}",
            cleaner="fill_missing",
            activate=True
        )
        for (row_idx, col_idx) in zip(*np.where(missing_matrix))
    ]

def scan_df_for_outliers(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    
    # Dynamically calculate contamination
    def auto_contamination(n):
        return min(0.1, max(0.01, 5/np.log(n)))
    
    for col in df.select_dtypes(include=[np.number]):
        # Automatically switch detection methods
        skewness = df[col].skew()
        if abs(skewness) > 1:  # Use MAD for detection
            median = df[col].median()
            mad = (df[col] - median).abs().median()
            threshold = 3 * mad
            outliers = df[col].sub(median).abs().gt(threshold)
        else:  # Use IQR
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers = ~df[col].between(q1-1.5*iqr, q3+1.5*iqr)
        
        # Record results
        scan_results.extend(
            ScanResult(
                row=idx,
                col=df.columns.get_loc(col),
                message=f"Outlier in {col} (value={df.at[idx, col]:.2f})",
                cleaner="outlier_handling",
                activate=True
            )
            for idx in df[outliers].index
        )
    
    # Multivariate detection
    numerical_df = df.select_dtypes(include=[np.number]).dropna()
    if len(numerical_df) > 10:
        contamination = auto_contamination(len(numerical_df))
        clf = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=min(100, len(numerical_df)//10))
        
        outlier_flags = clf.fit_predict(numerical_df) == -1
        for idx in numerical_df[outlier_flags].index:
            scan_results.append(
                ScanResult(
                    row=idx,
                    col=-1,
                    message="Multivariate anomaly detected",
                    cleaner="multivariate_outlier",
                    activate=True
                )
            )
    
    return scan_results

def scan_df_for_categorical(df: pd.DataFrame, 
                           max_categories: int = 50,
                           categorical_dtypes: list = ['object', 'category', 'bool']) -> List[ScanResult]:
    scan_results = []
    
    # Drop fully numeric columns
    non_numeric_cols = df.select_dtypes(exclude=[np.number])
    
    for col in non_numeric_cols.columns:
        # Skip empty or all-null columns
        if df[col].dropna().empty:
            continue
            
        # Conditions for detecting categorical features
        is_categorical = (
            df[col].dtype in categorical_dtypes or 
            (df[col].dtype.kind in 'iuf' and df[col].nunique() <= min(max_categories, len(df)**0.5)) or
            df[col].dtype == 'bool'
        )
        
        # Exclude high-cardinality columns (e.g., free text)
        unique_count = df[col].nunique()
        is_high_cardinality = unique_count > max_categories
        
        if is_categorical and not is_high_cardinality:
            try:
                categories = df[col].dropna().unique()
                categories_str = ", ".join([str(x) for x in categories[:10]])
                if len(categories) > 10:
                    categories_str += f"... (Total {len(categories)} categories)"
                
                scan_results.append(
                    ScanResult(
                        row=-1,  # Mark for column-wide processing
                        col=df.columns.get_loc(col),
                        message=(f"Categorical feature column '{col}' detected with {len(categories)} categories: {categories_str}"),
                        cleaner="categorical_features_encoded",
                        activate=True
                    )
                )
            except Exception as e:
                print(f"Error processing column {col}: {str(e)}")
                continue

                
    return scan_results
