import numpy as np
import pandas as pd
from typing import List
from sklearn.preprocessing import LabelEncoder
from ScanResult import *

def apply_scan_results(df: pd.DataFrame, scan_results: List[ScanResult]) -> pd.DataFrame:

    # Group scan results by (row, col) and keep the chosen (active) action for each
    grouped = {}
    for scan in scan_results:
        # For each scan, find the action that the user selected (i.e. with activate=True)
        active_actions = [action for action in scan.actions if action.activate]
        if not active_actions:
            continue  # skip if no action was selected
        # Assume only one action per scan result is active.
        action = active_actions[0]
        key = (scan.row, scan.col)
        grouped[key] = (scan, action)  # If multiple for same key, last one wins

    # Process each grouped scan result
    for (row, col), (scan, action) in grouped.items():
        # For deletion actions: if the active action indicates removal,
        # then drop the row. For duplicate rows, col is set to -1.
        if action.cleaner in ["remove", "delete"]:
            if col == -1:
                # Entire row removal (e.g. for duplicate row handling)
                if row in df.index:
                    df.drop(index=row, inplace=True)
            else:
                # For missing or outlier cases, dropping the row
                if row in df.index:
                    df.drop(index=row, inplace=True)
        
        # For missing values: fill the cell with a computed statistic.
        elif action.cleaner in ["mean", "median", "mode"]:
            if col not in df.columns or row not in df.index:
                continue
            if action.cleaner == "mean":
                val = df[col].mean()
            elif action.cleaner == "median":
                val = df[col].median()
            elif action.cleaner == "mode":
                modes = df[col].mode()
                val = modes.iloc[0] if not modes.empty else np.nan
            df.at[row, col] = val
        
        # For forward/backward fill on missing values.
        elif action.cleaner in ["ffill", "bfill"]:
            if col not in df.columns or row not in df.index:
                continue

            if action.cleaner == "ffill":
                # Try forward fill: use the last valid value before (or at) the current row.
                series_before = df[col].iloc[:row + 1]
                val = series_before.ffill().iloc[-1]
                # If ffill doesn't yield a valid value (e.g., at the very first row), fallback to bfill.
                if pd.isna(val):
                    series_after = df[col].iloc[row:]
                    val = series_after.bfill().iloc[0]
            else:  # action.cleaner == "bfill"
                # Try backward fill: use the first valid value at (or after) the current row.
                series_after = df[col].iloc[row:]
                val = series_after.bfill().iloc[0]
                # If bfill doesn't yield a valid value (e.g., at the last row), fallback to ffill.
                if pd.isna(val):
                    series_before = df[col].iloc[:row + 1]
                    val = series_before.ffill().iloc[-1]

            df.at[row, col] = val

        
        # For categorical features: apply encoding or drop the column.
        elif action.cleaner in ["one_hot", "label_encoding", "drop"]:
            if col not in df.columns:
                continue
            if action.cleaner == "one_hot":
                df = pd.get_dummies(df, columns=[col], prefix=[col])
            elif action.cleaner == "label_encoding":
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
            elif action.cleaner == "drop":
                df.drop(columns=[col], inplace=True, errors='ignore')
        
        # For target handling. Here you might use action.data if provided.
        elif action.cleaner == "handle_target":
            if col not in df.columns or row not in df.index:
                continue
            if action.data is not None:
                df.at[row, col] = action.data
            # Otherwise, no default action is taken.
        
        # For any "keep" action, or unknown actions, no operation is performed.
        elif action.cleaner == "keep":
            pass

    # Reset index if any rows were dropped
    df.reset_index(drop=True, inplace=True)
    return df
