import pandas as pd
import re
from pycaret.classification import *

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Remove duplicate rows
    df = df.drop_duplicates()
    
    # Remove Leading/Trailing Spaces from column names
    df.columns = df.columns.str.strip()
    
    # Define maximum allowed categories (less than 1% of rows)
    max_categories_threshold = int(len(df) * 0.01)
    
    # Identify categorical columns that meet the threshold
    eligible_cat_features = [
        col for col in df.select_dtypes(include=['object', 'category', 'bool']).columns
        if df[col].nunique() <= max_categories_threshold
    ]
    
    # Encode each eligible categorical column using pd.factorize
    for col in eligible_cat_features:
        df[col], _ = pd.factorize(df[col])
    
    # Detect target column if not provided
    def detect_target_column(df):
        possible_target = None
        for col in df.columns:
            unique_values = df[col].nunique()
            if unique_values == 2 and df[col].isnull().sum() == 0:
                possible_target = col
            elif 2 < unique_values < len(df) * 0.01 and df[col].isnull().sum() == 0:
                possible_target = col
        return possible_target
    
    target = detect_target_column(df)
    
    if target:
        print(f"Detected target column: {target}")
    else:
        print("No suitable target column detected. Please specify it manually.")
    
    if target in eligible_cat_features:
        eligible_cat_features.remove(target)
    
    def detect_ignore_features(df, keywords=None):
        if keywords is None:
            keywords = ['row', 'id', 'name']
        ignore_features = [col for col in df.columns if any(re.search(keyword, col, flags=re.IGNORECASE) for keyword in keywords)]
        return ignore_features
    
    ignore_features = detect_ignore_features(df)
    print("Automatically detected ignore features:", ignore_features)
    
    clf = setup(
        data=df,
        target=target,
        numeric_imputation="mean",
        categorical_imputation='mode',
        remove_multicollinearity=True,
        multicollinearity_threshold=1.0,
        remove_outliers=True,
        outliers_threshold=0.05,
        fold_strategy='stratifiedkfold',
        categorical_features=eligible_cat_features,
        normalize=True,
        ignore_features=ignore_features,
        fix_imbalance=True,
        session_id=42
    )
    
    return get_config("X")  # Return transformed DataFrame
