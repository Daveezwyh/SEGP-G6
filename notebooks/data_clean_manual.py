import pandas as pd
from ScanResult import ScanResult

def clean_df_for_duplicates(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "remove":
                df = df.drop_duplicates(keep='first')
            elif action.cleaner == "keep":
                pass
    return df

def clean_df_for_missing(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            col = scan_result.col
            row_idx = scan_result.row
            
            if row_idx not in df.index or col not in df.columns:
                continue

            if action.cleaner == "mean":
                df.at[row_idx, col] = df[col].mean()
            elif action.cleaner == "median":
                df.at[row_idx, col] = df[col].median()
            elif action.cleaner == "mode":
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df.at[row_idx, col] = mode_val.iloc[0]
            elif action.cleaner == "ffill":
                prev_valid = df.loc[:row_idx, col].dropna()
                if not prev_valid.empty:
                    df.at[row_idx, col] = prev_valid.iloc[-1]
            elif action.cleaner == "bfill":
                next_valid = df.loc[row_idx:, col].dropna()
                if not next_valid.empty:
                    df.at[row_idx, col] = next_valid.iloc[0]
            elif action.cleaner == "delete":
                df = df.drop(index=row_idx)
    return df

def clean_df_for_outliers(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "delete":
                df = df.drop(index=scan_result.row)
    return df

def clean_df_for_categorical(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
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
    return df