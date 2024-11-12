import pandas as pd

def scan_duplicates(df):
    duplicate_message = []
    duplicated_rows = df[df.duplicated()]
    
    for index in duplicated_rows.index:
        duplicate_message.append(f"row {index} is duplicated")

    return duplicate_message

def remove_duplicates(df):
    df = df.drop_duplicates().reset_index(drop=True)
    return df