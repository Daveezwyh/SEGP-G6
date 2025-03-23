import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import IsolationForest
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.feature_selection import VarianceThreshold
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor

from backend.autoclean.api.models import TaskProgress

def clean_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Automated data cleaning and preprocessing pipeline
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw input data to be processed
    numeric_threshold : float (default=0.1)
        Threshold ratio for high-cardinality numeric column detection
    max_unique_count : int (default=100)
        Maximum allowed unique values for categorical columns
    contamination : float (default=0.05)
        Outlier fraction assumption for Isolation Forest
    max_onehot_features : int (default=15)
        Cardinality threshold for One-Hot encoding
    handle_dates : bool (default=True)
        Automatically detect and process datetime columns
    text_cleaning : bool (default=True)
        Standardize text formatting and clean special characters
    extract_dates : bool (default=True)
        Create datetime features from detected date columns
    remove_sparse : bool (default=True)
        Remove sparse binary features using variance threshold
    remove_collinear : bool (default=True)
        Remove collinear features using VIF analysis
    generate_report : bool (default=False)
        Generate HTML summary report
    output_path : str (default="cleaning_report.html")
        Output path for generated report
    
    Returns:
    --------
    pd.DataFrame
        Processed and cleaned data
    """
    numeric_threshold: float = 0.1
    max_unique_count: int = 100
    contamination: float = 0.05
    max_onehot_features: int = 15
    handle_dates: bool = True
    text_cleaning: bool = True
    extract_dates: bool = True
    remove_sparse: bool = True
    remove_collinear: bool = True

    task_progress: TaskProgress = None

    def update_progress(step_message: str, progress_increment: float):
        if task_progress:
            task_progress.percentage += progress_increment
            task_progress.message = step_message
            task_progress.save()

    df = df.copy()

    def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        return df.drop_duplicates(keep="first").copy()

    def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values for different feature types:
    
        - Numeric features: Use IterativeImputer for multivariate imputation.
        - Categorical features (object and category types): Fill missing values with the mode;
          if all values are missing, fill with "missing".
        - Datetime features: Fill missing values with the mode date; if all missing, fill with a default date (e.g., '1900-01-01').
        - Boolean features: Fill missing values with the mode; if all missing, default to False.
        """
        all_null_cols = df.columns[df.isnull().all()]
        df.drop(columns=all_null_cols, inplace=True)
    
        # 1. Numeric features: Apply Iterative Imputation
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            imputer = IterativeImputer(max_iter=10, random_state=42)
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        # 2. Categorical features (object type): Fill with mode or "missing" if all are missing
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            if df[col].isnull().all():
                df[col].fillna("missing", inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else "missing"
                df[col].fillna(mode_val, inplace=True)
        
        # 3. Categorical features (category type): Same approach as object type
        cat_dtype_cols = df.select_dtypes(include=['category']).columns.tolist()
        for col in cat_dtype_cols:
            if df[col].isnull().all():
                df[col].fillna("missing", inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else "missing"
                df[col].fillna(mode_val, inplace=True)
        
        # 4. Datetime features: Fill with mode or default date if all are missing
        datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        for col in datetime_cols:
            if df[col].isnull().all():
                df[col].fillna(pd.Timestamp('1900-01-01'), inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else pd.Timestamp('1900-01-01')
                df[col].fillna(mode_val, inplace=True)
        
        # 5. Boolean features: Fill with mode or default to False if all are missing
        bool_cols = df.select_dtypes(include=['bool']).columns.tolist()
        for col in bool_cols:
            if df[col].isnull().all():
                df[col].fillna(False, inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else False
                df[col].fillna(mode_val, inplace=True)
        
        return df

    def _detect_outliers(df: pd.DataFrame, contamination: float) -> pd.DataFrame:
        """Outlier detection using Isolation Forest"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            preds = iso_forest.fit_predict(df[numeric_cols])
            df = df[preds != -1].reset_index(drop=True)
        return df

    def _process_dates(df: pd.DataFrame, handle_dates: bool, extract_dates: bool) -> pd.DataFrame:
        """Detect and process datetime columns"""
        if not handle_dates:
            return df
        
        date_cols = []
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='raise')
                date_cols.append(col)
            except:
                continue
        
        if extract_dates and date_cols:
            for col in date_cols:
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_weekday'] = df[col].dt.weekday
                df.drop(columns=[col], inplace=True)
        
        return df

    def _clean_text(df: pd.DataFrame, text_cleaning: bool) -> pd.DataFrame:
        """Standardize text formatting"""
        if not text_cleaning:
            return df
        
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.lower()
                .str.replace(r'[^\w\s]', '', regex=True)
                .str.replace(r'\s+', ' ', regex=True)
                .str.strip()
            )
        return df

    def _encode_categoricals(
        df: pd.DataFrame, 
        max_unique_count: int,
        numeric_threshold: float,
        max_onehot_features: int
    ) -> pd.DataFrame:
        """Encode categorical variables with frequency or One-Hot encoding"""
        # Select non-numeric columns
        cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns
        
        for col in cat_cols:
            unique_count = df[col].nunique()
            total_rows = len(df)
            
            # Drop high cardinality columns
            if unique_count > max_unique_count or unique_count / total_rows > 0.5:
                df.drop(columns=[col], inplace=True)
                continue
            
            # Encoding strategy
            if unique_count <= max_onehot_features:
                # One-Hot Encoding
                df = pd.get_dummies(df, columns=[col], drop_first=True, dtype=int)
            elif max_onehot_features <= unique_count <= numeric_threshold:
                # Frequency Encoding
                freq = (df[col].value_counts() / total_rows).to_dict()
                df[f"{col}_freq"] = df[col].map(freq).astype(np.float32)
                df.drop(columns=[col], inplace=True)
        
        return df

    def _remove_sparse_features(df: pd.DataFrame, remove_sparse: bool) -> pd.DataFrame:
        """Remove sparse binary features using variance threshold"""
        if not remove_sparse:
            return df
        
        binary_cols = [
            col for col in df.columns 
            if set(df[col].dropna().unique()).issubset({0, 1})
        ]
        
        if binary_cols:
            selector = VarianceThreshold(threshold=0.05*(1-0.05))
            binary_data = selector.fit_transform(df[binary_cols])
            selected_cols = np.array(binary_cols)[selector.get_support()].tolist()
            non_binary_cols = df.columns.difference(binary_cols).tolist()
            df = pd.concat([
                df[non_binary_cols],
                pd.DataFrame(binary_data, columns=selected_cols)
            ], axis=1)
        
        return df

    def _remove_collinear_features(df: pd.DataFrame, remove_collinear: bool) -> pd.DataFrame:
        """Remove collinear features using VIF"""
        if not remove_collinear:
            return df
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()
        
        while numeric_cols:
            vif = [variance_inflation_factor(df[numeric_cols].values, i) 
                   for i in range(len(numeric_cols))]
            max_vif = max(vif)
            
            if max_vif < 5:
                break
            
            remove_idx = vif.index(max_vif)
            removed_col = numeric_cols.pop(remove_idx)
            
            if removed_col in all_cols:
                all_cols.remove(removed_col)
        
        return df[all_cols]

    df = _remove_duplicates(df)
    update_progress("Removed duplicates", 14.3)
    
    df = _handle_missing_values(df)
    update_progress("Handled missing values", 14.3)
    
    df = _detect_outliers(df, contamination)
    update_progress("Detected and removed outliers", 14.3)
    
    df = _process_dates(df, handle_dates, extract_dates)
    update_progress("Processed dates", 14.3)
    
    df = _clean_text(df, text_cleaning)
    update_progress("Cleaned text", 14.3)
    
    df = _encode_categoricals(df, max_unique_count, numeric_threshold, max_onehot_features)
    update_progress("Encoded categorical features", 14.3)
    
    df = _remove_sparse_features(df, remove_sparse)
    update_progress("Removed sparse features", 14.3)
    
    df = _remove_collinear_features(df, remove_collinear)
    update_progress("Removed collinear features", 14.3)

    if task_progress:
        task_progress.status = TaskProgress.Status.COMPLETED.value
        task_progress.message = "Data cleaning completed"
        task_progress.percentage = 100.0
        task_progress.save()
    
    return df

generate_report: bool = False,
output_path: str = "cleaning_report.html"
def _generate_report(df: pd.DataFrame, generate_report: bool, output_path: str) -> None:
    """Generate HTML cleaning report with correlation matrix"""
    if not generate_report:
        return
    
    summary = pd.DataFrame({
        'Data Type': df.dtypes,
        'Missing Values': df.isnull().sum(),
        'Unique Values': df.nunique()
    })
    
    numeric_df = df.select_dtypes(include=['number'])
    plt.figure(figsize=(12, 8))
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.savefig('correlation_plot.png')
    
    with open(output_path, 'w') as f:
        f.write("<h1>Data Cleaning Report</h1>")
        f.write("<h2>Data Summary</h2>")
        f.write(summary.to_html())
        f.write("<h2>Correlation Matrix</h2>")
        f.write(f"<img src='correlation_plot.png' width='800'/>")
    
    logging.info(f"Report saved to: {output_path}")