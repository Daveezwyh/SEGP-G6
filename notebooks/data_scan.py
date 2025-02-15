from ScanResult import ScanResult  # Importing the ScanResult class
from typing import List
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import Counter

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
    scan_results = []

    for row_index, row in df.iterrows():
        for col_index, col_name in enumerate(df.columns):
            if pd.isna(row[col_name]):
                scan_results.append(
                    ScanResult(
                        row=row_index,
                        col=col_index,
                        message=f"Missing value in row {row_index + 1}, column {col_name}",
                        cleaner="fill_missing",
                        activate=True
                    )
                )

    return scan_results

def scan_df_for_outliers(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    
    for col_name in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col_name].quantile(0.25)
        Q3 = df[col_name].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outlier_rows = df[(df[col_name] < lower_bound) | (df[col_name] > upper_bound)].index
        
        for idx in outlier_rows:
            scan_results.append(
                ScanResult(
                    row=idx,
                    col=df.columns.get_loc(col_name),
                    message=f"Row {idx + 1} contains an outlier in column '{col_name}'",
                    cleaner="outlier_detection",
                    activate=True
                )
            )

    clf = IsolationForest(contamination=0.05, random_state=42)
    numerical_df = df.select_dtypes(include=[np.number]).dropna()
    if not numerical_df.empty:
        outlier_predictions = clf.fit_predict(numerical_df)
        for idx, prediction in enumerate(outlier_predictions):
            if prediction == -1:
                scan_results.append(
                    ScanResult(
                        row=numerical_df.index[idx],
                        col=-1,
                        message=f"Row {numerical_df.index[idx] + 1} is an anomaly detected by Isolation Forest",
                        cleaner="outlier_detection",
                        activate=True
                    )
                )

    return scan_results

def scan_df_for_categorical(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    
    for col_name in df.select_dtypes(include=['object', 'category']).columns:  
        value_counts = df[col_name].value_counts()
        rare_categories = value_counts[value_counts < 3].index  # set limits of 3 

        for idx, value in df[col_name].items():
            if value in rare_categories:
                scan_results.append(
                    ScanResult(
                        row=idx,
                        col=df.columns.get_loc(col_name),
                        message=f"Rare category '{value}' in column '{col_name}'",
                        cleaner="category_encoding",
                        activate=True
                    )
                )

        unique_values = df[col_name].dropna().unique()
        cleaned_values = [str(v).strip().lower() for v in unique_values]  # Normalization
        value_counts = Counter(cleaned_values)

        for idx, value in df[col_name].items():
            if str(value).strip().lower() not in value_counts:
                scan_results.append(
                    ScanResult(
                        row=idx,
                        col=df.columns.get_loc(col_name),
                        message=f"Possible inconsistent category '{value}' in column '{col_name}'",
                        cleaner="category_standardization",
                        activate=True
                    )
                )

    return scan_results

def scan_dataframe(df: pd.DataFrame) -> List[ScanResult]:
    scan_results = []
    scan_results.extend(scan_df_for_duplicates(df))
    scan_results.extend(scan_df_for_missing(df))
    scan_results.extend(scan_df_for_outliers(df))
    scan_results.extend(scan_df_for_categorical(df))
    return scan_results

# sample
if __name__ == "__main__":
    data = {
        "A": [1, 2, 3, 4, 100, 6, 7, 8, 9, 100],  # 存在异常值
        "B": [10, 20, 30, 40, None, 60, 70, 80, 90, 100],  # 存在缺失值
        "C": ["X", "Y", "Z", "X", "Y", "Z", "X", "Y", "Z", "X"],
    }
    df = pd.DataFrame(data)
    df.loc[3] = df.loc[0]  # make a duplicate

    results = scan_dataframe(df)
    for res in results:
        print(res)