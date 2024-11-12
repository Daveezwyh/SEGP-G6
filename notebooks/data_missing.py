import pandas as pd
from fancyimpute import KNN

def scan_missing(df):
    missing_messages = []
    for row_index, row in df.iterrows():
        for col_name in df.columns:
            if pd.isna(row[col_name]):
                missing_messages.append(f"row {row_index} column {col_name} has missing value")
    return missing_messages

def fill_missing_values_knn(df, k=6):
    df_filled = df.copy()
    numeric_df = df_filled.select_dtypes(include=[float, int])
    non_numeric_df = df_filled.select_dtypes(exclude=[float, int])
    
    if not numeric_df.empty:
        filled_numeric_data = KNN(k=k).fit_transform(numeric_df)
        numeric_df_filled = pd.DataFrame(filled_numeric_data, columns=numeric_df.columns, index=df.index)
        df_filled.update(numeric_df_filled)
        
    for column in non_numeric_df.columns:
        if not non_numeric_df[column].mode().empty:
            most_frequent_value = non_numeric_df[column].mode().iloc[0]
            df_filled[column].fillna(most_frequent_value, inplace=True)
            
    return df_filled

# # Example usage
# file_path = 'Churn_Modelling.csv'  # Replace with your file path
# df = pd.read_csv(file_path)
# missing_messages = scan_miising(df)
# df_withou_missing = fill_missing_values_knn(df)
