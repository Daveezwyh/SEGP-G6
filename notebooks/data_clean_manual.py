import pandas as pd
from ScanResult import ScanResult

def clean_df_for_duplicates(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.cleaner == clean_df_for_duplicates.__name__:
            if action.activate:
                df = df.drop_duplicates(keep='first')
    return df

#############################################
# decide which way to choose
import pandas as pd

def fill_with_mean(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.cleaner == "fill_with_mean" and action.activate:
            col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
            if col_name:
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                df[col_name].fillna(df[col_name].mean(), inplace=True)
    return df

def fill_with_median(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.cleaner == "fill_with_median" and action.activate:
            col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
            if col_name:
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                df[col_name].fillna(df[col_name].median(), inplace=True)
    return df

def fill_with_mode(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.cleaner == "fill_with_mode" and action.activate:
            col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
            if col_name:
                mode_values = df[col_name].mode()
                if not mode_values.empty:
                    df[col_name].fillna(mode_values[0], inplace=True)
    return df

def fill_with_ffill(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.cleaner == "fill_with_ffill" and action.activate:
            col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
            if col_name:
                df[col_name].fillna(method='ffill', inplace=True)
    return df

def fill_with_bfill(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.cleaner == "fill_with_bfill" and action.activate:
            col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
            if col_name:
                df[col_name].fillna(method='bfill', inplace=True)
    return df

def delete_missing_rows(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.cleaner == "delete_missing_rows" and action.activate:
            col_name = df.columns[scan_result.col] if 0 <= scan_result.col < len(df.columns) else None
            if col_name:
                df.dropna(subset=[col_name], inplace=True)
    return df

def clean_df_for_missing(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "fill_with_mean":
                df[scan_result.col].fillna(df[scan_result.col].mean(), inplace=True)
            elif action.cleaner == "fill_with_median":
                df[scan_result.col].fillna(df[scan_result.col].median(), inplace=True)
            elif action.cleaner == "fill_with_mode":
                df[scan_result.col].fillna(df[scan_result.col].mode()[0], inplace=True)
            elif action.cleaner == "fill_with_ffill":
                df[scan_result.col].fillna(method='ffill', inplace=True)
            elif action.cleaner == "fill_with_bfill":
                df[scan_result.col].fillna(method='bfill', inplace=True)
            elif action.cleaner == "delete_missing_rows":
                df.dropna(subset=[scan_result.col], inplace=True)
    return df
#######################################################


def clean_df_for_outlier(scan_result, df):
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "clean_df_for_outlier":
                if scan_result.row in df.index:
                    df.drop(index=scan_result.row, inplace=True)
                else:
                    print(f"Row {scan_result.row} not found in DataFrame.")
    return df

def clean_df_cat_one_hot(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "clean_df_cat_one_hot":
                col = scan_result.col
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
    return df

def clean_df_cat_label_encoding(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "clean_df_cat_label_encoding":
                col = scan_result.col
                df[col] = df[col].astype('category').cat.codes
    return df

def clean_df_cat_drop(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "clean_df_cat_drop":
                df = df.drop(scan_result.col, axis=1)
    return df

#######################################################
# Deprecated
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
#######################################################

def apply_target_cleaning(scan_result: ScanResult, df: pd.DataFrame) -> pd.DataFrame:
    for action in scan_result.actions:
        if action.activate:
            if action.cleaner == "delete_target_row":
                df.drop(index=scan_result.row, inplace=True)
            elif action.cleaner == "delete_target_column":
                df.drop(columns=[scan_result.col], inplace=True)
    return df
