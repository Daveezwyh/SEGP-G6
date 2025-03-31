import pandas as pd
import re
from pycaret.classification import setup, get_config, pull, compare_models
from typing import Optional

def auto_ML_cleaning(df: pd.DataFrame, target: Optional[str] = None) -> pd.DataFrame:
    
    setup(
        data=df,
        target=target,
        
        # Data cleaning configuration
        numeric_imputation="median",  # Fill missing numerical values with the median
        categorical_imputation='mode',  # Fill missing categorical values with the mode
        remove_multicollinearity=True,  # Remove multicollinearity features
        multicollinearity_threshold=1.0, 
        remove_outliers=True,  # Automatically handle outliers using the IQR method
        outliers_threshold=0.05,  # Outlier detection threshold
        fold_strategy='stratifiedkfold',  # Use stratified K-fold cross-validation
        normalize=True,
        
        # Other automation settings
        fix_imbalance=True,  # Automatically handle class imbalance
        session_id=42  # Random seed
        )
    
    df = get_config('X').join(get_config('y'))

    compare_models(sort='AUC')
    model_comparison = pull()

    return model_comparison