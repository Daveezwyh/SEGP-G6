import pandas as pd
import re
from pycaret.classification import setup, get_config
from typing import Optional

def auto_ML_cleaning(df: pd.DataFrame, target: Optional[str] = None) -> pd.DataFrame:
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates()
    
    # Define maximum allowed categories (less than 1% of rows)
    max_categories_threshold = int(len(df) * 0.01)
    # Identify categorical columns (object or category dtypes) that meet the threshold
    eligible_cat_features = [
        col for col in df.select_dtypes(include=['object', 'category', 'bool']).columns
        if df[col].nunique() <= max_categories_threshold]


    # Encode each eligible categorical column using pd.factorize
    for col in eligible_cat_features:
        df[col], _ = pd.factorize(df[col])
    if target is None or target not in df.columns:
        def detect_target_column(df):
            possible_target = None
            for col in df.columns:
                unique_values = df[col].nunique()
                # Check if the column has no missing values and is suitable for classification
                if unique_values == 2 and df[col].isnull().sum() == 0:  # Binary classification without missing values
                    possible_target = col
                elif 2 < unique_values < len(df) * 0.01 and df[col].isnull().sum() == 0:  # Multi-class classification without missing values
                    possible_target = col
            return possible_target # Target column is more possible on the right side
        target = detect_target_column(df)
    if target in eligible_cat_features:
        eligible_cat_features.remove(target)
    

    def detect_ignore_features(df, keywords=None):
        if keywords is None:
            # Only ignore columns that are very likely identifiers or irrelevant
            keywords = ['row', 'id', 'name']
        ignore_features = []
        for col in df.columns:
            # Check if column name contains any of the keywords
            if any(re.search(keyword, col, flags=re.IGNORECASE) for keyword in keywords):
                ignore_features.append(col)
        return ignore_features

    # Usage with your DataFrame
    ignore_features = detect_ignore_features(df)
    
    setup(
        data=df,
        target=target,
        
        # Data cleaning configuration
        numeric_imputation="mean",  # Fill missing numerical values with the median
        categorical_imputation='mode',  # Fill missing categorical values with the mode
        remove_multicollinearity=True,  # Remove multicollinearity features
        multicollinearity_threshold=1.0, 
        remove_outliers=True,  # Automatically handle outliers using the IQR method
        outliers_threshold=0.05,  # Outlier detection threshold
        fold_strategy='stratifiedkfold',  # Use stratified K-fold cross-validation
        categorical_features=eligible_cat_features,
        normalize=True,

        # Categorical feature handling
        ignore_features=ignore_features,  # Ignore irrelevant features
        
        # Other automation settings
        fix_imbalance=True,  # Automatically handle class imbalance
        session_id=42  # Random seed
        )
    
    df = get_config('X').join(get_config('y'))
    return df