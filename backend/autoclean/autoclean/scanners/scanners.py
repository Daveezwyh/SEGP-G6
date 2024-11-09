from autoclean.scanners.result import ScanResult
import pandas as pd

def scan_df_for_something(df: pd.DataFrame) -> list:
    find_str = 'grants'
    scan_results = []

    for row_index, row in df.iterrows():
        for col_index, col in enumerate(df.columns):
            if str(find_str).lower() in str(row[col]).lower():
                scan_results.append(
                    ScanResult(
                        row=row_index,
                        col=col_index,
                        message=f"Found '{find_str}' in row {row_index+1}, col {col_index+1}",
                        cleaner="?",
                        activate=True
                    )
                )

    return scan_results