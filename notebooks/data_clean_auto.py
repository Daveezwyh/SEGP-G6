import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import IsolationForest
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.feature_selection import VarianceThreshold
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor
#from backend.autoclean.api.models import TaskProgress

def clean_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Main function to automatically clean and preprocess the DataFrame.

    Purpose:
    --------
    This function applies a sequence of data cleaning steps:
    - Remove duplicated rows
    - Handle missing values appropriately
    - Detect and remove outliers using Isolation Forest
    - Detect and process datetime features
    - Standardize and clean text features
    - Encode categorical features with one-hot or frequency encoding
    - Remove sparse binary features

    This function provides an automated pipeline for preparing tabular data
    for machine learning or data analysis tasks.

    Inputs:
    -------
    df : pd.DataFrame
        Raw input DataFrame to be cleaned.

    Output:
    -------
    pd.DataFrame
        A cleaned and processed DataFrame ready for modeling.

    Parameters (Internal Defaults):
    --------------------------------
    numeric_threshold : float
        If the ratio of unique values exceeds this threshold, drop the categorical column (default=0.99).
    contamination : float
        Assumed proportion of outliers for Isolation Forest (default=0.05).
    max_onehot_features : int
        Maximum unique values allowed for one-hot encoding (default=20).
    handle_dates : bool
        Whether to detect and process datetime columns (default=True).
    text_cleaning : bool
        Whether to clean text fields (default=True).
    extract_dates : bool
        Whether to extract year, month, day, weekday from datetime columns (default=True).
    remove_sparse : bool
        Whether to remove low-variance binary features (default=True).

    Error Handling:
    ---------------
    Each internal step is wrapped in a try-except block to ensure that
    failure in one step does not stop the entire cleaning process.
    """
    
    # Set internal parameter values
    numeric_threshold: float = 0.99
    contamination: float = 0.05
    max_onehot_features: int = 20
    handle_dates: bool = True
    text_cleaning: bool = True
    extract_dates: bool = True
    remove_sparse: bool = True
    # remove_collinear: bool = True

    df = df.copy()  # Work on a copy to avoid modifying the original DataFrame

    def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicated rows from the DataFrame.

        Purpose:
        --------
        This function drops duplicate rows from the input DataFrame, keeping only
        the first occurrence of each unique row.

        Input:
        ------
        df : pd.DataFrame
            The input DataFrame to clean.

        Output:
        -------
        pd.DataFrame
            A new DataFrame with duplicated rows removed.

        Error Handling:
        ---------------
        No internal try-except; assumes correct DataFrame input.
        """
        return df.drop_duplicates(keep="first").copy()

    def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values for different feature types in the DataFrame.

        Purpose:
        --------
        This function handles missing values differently depending on the feature type:
        - Numeric features: Filled using multivariate imputation (IterativeImputer).
        - Categorical features ('object' and 'category'): Filled with the mode value or "missing" if all missing.
        - Datetime features: Filled with the most frequent date or a default date ('1900-01-01') if all missing.
        - Boolean features: Filled with the mode or False if all missing.
        Additionally, it drops any columns where all values are missing.

        Input:
        ------
        df : pd.DataFrame
            The DataFrame with missing values to process.

        Output:
        -------
        pd.DataFrame
            A new DataFrame with missing values filled appropriately.

        Error Handling:
        ---------------
        No internal try-except; assumes the input DataFrame is properly formatted.
        """
        # Identify and drop columns where all values are NaN
        all_null_cols = df.columns[df.isnull().all()]
        df.drop(columns=all_null_cols, inplace=True)

        # 1. Handle numeric features by applying Iterative Imputer
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            imputer = IterativeImputer(max_iter=10, random_state=42)
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

        # 2. Handle object-type categorical features
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            if df[col].isnull().all():
                df[col].fillna("missing", inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else "missing"
                df[col].fillna(mode_val, inplace=True)

        # 3. Handle category-type categorical features
        cat_dtype_cols = df.select_dtypes(include=['category']).columns.tolist()
        for col in cat_dtype_cols:
            if df[col].isnull().all():
                df[col].fillna("missing", inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else "missing"
                df[col].fillna(mode_val, inplace=True)

        # 4. Handle datetime features
        datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        for col in datetime_cols:
            if df[col].isnull().all():
                df[col].fillna(pd.Timestamp('1900-01-01'), inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else pd.Timestamp('1900-01-01')
                df[col].fillna(mode_val, inplace=True)

        # 5. Handle boolean features
        bool_cols = df.select_dtypes(include=['bool']).columns.tolist()
        for col in bool_cols:
            if df[col].isnull().all():
                df[col].fillna(False, inplace=True)
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else False
                df[col].fillna(mode_val, inplace=True)

        return df

    def _detect_outliers(df: pd.DataFrame, contamination: float) -> pd.DataFrame:
        """
        Detect and remove outliers from numeric features using Isolation Forest.

        Purpose:
        --------
        This function applies the Isolation Forest algorithm to the numeric features 
        of the DataFrame to identify and remove outliers. 
        Outliers are detected based on the provided contamination rate.

        Inputs:
        -------
        df : pd.DataFrame
            The input DataFrame containing numeric features.
        contamination : float
            The proportion of outliers expected in the dataset (e.g., 0.05 means 5%).

        Output:
        -------
        pd.DataFrame
            A new DataFrame with detected outlier rows removed.

        Error Handling:
        ---------------
        No internal try-except; assumes numeric columns are suitable for modeling.
        """
        # Select only numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            # Initialize Isolation Forest
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            # Predict whether each sample is an outlier (-1) or not (1)
            preds = iso_forest.fit_predict(df[numeric_cols])
            # Keep only rows predicted as normal (preds != -1)
            df = df[preds != -1].reset_index(drop=True)
        return df

    def _process_dates(df: pd.DataFrame, handle_dates: bool, extract_dates: bool) -> pd.DataFrame:
        """
        Detect and process datetime columns in the DataFrame.

        Purpose:
        --------
        This function attempts to detect object-type columns that can be parsed as dates,
        converts them to datetime type, and optionally extracts features such as year,
        month, day, and weekday into separate columns. 
        Original datetime columns can be dropped after feature extraction.

        Inputs:
        -------
        df : pd.DataFrame
            The input DataFrame that may contain date-like columns.
        handle_dates : bool
            Whether to attempt to detect and process datetime columns.
        extract_dates : bool
            Whether to extract year, month, day, and weekday features from datetime columns.

        Output:
        -------
        pd.DataFrame
            A new DataFrame with processed date columns and optionally extracted features.

        Error Handling:
        ---------------
        Each column is individually attempted; failures to convert are silently ignored.
        """
        if not handle_dates:
            # If date handling is disabled, return the DataFrame unchanged
            return df

        date_cols = []  # Track successfully converted date columns

        # Attempt to parse each object-type column as datetime
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='raise')
                date_cols.append(col)
            except:
                continue

        # If extract_dates is enabled and some date columns are found
        if extract_dates and date_cols:
            for col in date_cols:
                # Create new features for each date part
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_weekday'] = df[col].dt.weekday
                # Drop the original datetime column after feature extraction
                df.drop(columns=[col], inplace=True)

        return df

    def _clean_text(df: pd.DataFrame, text_cleaning: bool) -> pd.DataFrame:
        """
        Standardize and clean text columns in the DataFrame.

        Purpose:
        --------
        This function standardizes object-type columns by:
        - Lowercasing all text
        - Removing special characters (keeping only alphanumeric and whitespace)
        - Reducing multiple spaces to a single space
        - Stripping leading and trailing whitespace

        Inputs:
        -------
        df : pd.DataFrame
            The input DataFrame containing text columns.
        text_cleaning : bool
            Whether to apply text cleaning or not.

        Output:
        -------
        pd.DataFrame
            A new DataFrame with cleaned text fields.

        Error Handling:
        ---------------
        Each column is processed independently; errors during cleaning are silently ignored.
        """
        if not text_cleaning:
            # If text cleaning is disabled, return the DataFrame unchanged
            return df

        # Iterate over all object-type columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = (
                df[col]
                .astype(str)  # Ensure the column is treated as string
                .str.lower()  # Convert all text to lowercase
                .str.replace(r'[^\w\s]', '', regex=True)  # Remove non-alphanumeric characters
                .str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with a single space
                .str.strip()  # Remove leading and trailing spaces
            )
        return df

    def _encode_categoricals(df: pd.DataFrame, numeric_threshold: float, max_onehot_features: int) -> pd.DataFrame:
        """
        Encode categorical features using one-hot encoding or frequency encoding.

        Purpose:
        --------
        This function handles object-type, category-type, and boolean-type columns.
        Depending on the number of unique values (cardinality):
        - If unique ratio > numeric_threshold, drop the column.
        - If number of unique values <= max_onehot_features, apply one-hot encoding.
        - Otherwise, apply frequency encoding.

        Inputs:
        -------
        df : pd.DataFrame
            The input DataFrame containing categorical features.
        numeric_threshold : float
            The maximum allowed unique ratio for keeping the column (above this threshold, the column is dropped).
        max_onehot_features : int
            The maximum number of unique values to allow one-hot encoding; beyond this, frequency encoding is used.

        Output:
        -------
        pd.DataFrame
            A new DataFrame with categorical features encoded appropriately.

        Error Handling:
        ---------------
        Each column is processed independently; columns exceeding thresholds are handled accordingly.
        """
        # Select all categorical columns (object, category, bool)
        cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns

        for col in cat_cols:
            unique_count = df[col].nunique()
            total_rows = len(df)
            unique_ratio = unique_count / total_rows

            # If unique ratio exceeds threshold, drop the column
            if unique_ratio > numeric_threshold:
                df.drop(columns=[col], inplace=True)
                continue

            # If number of unique values is small, apply one-hot encoding
            if unique_count <= max_onehot_features:
                df = pd.get_dummies(df, columns=[col], drop_first=True, dtype=int)
            else:
                # Otherwise, apply frequency encoding
                freq = (df[col].value_counts() / total_rows).to_dict()
                df[f"{col}_freq"] = df[col].map(freq).astype(np.float32)
                df.drop(columns=[col], inplace=True)
        return df

    def _remove_sparse_features(df: pd.DataFrame, remove_sparse: bool) -> pd.DataFrame:
        """
        Remove sparse binary features using variance threshold.

        Purpose:
        --------
        This function identifies binary columns (with only 0 and 1 values).
        If enabled, it removes binary features that have very low variance, 
        meaning the feature is nearly constant and not informative.

        Inputs:
        -------
        df : pd.DataFrame
            The input DataFrame containing binary features.
        remove_sparse : bool
            Whether to apply sparse feature removal or not.

        Output:
        -------
        pd.DataFrame
            A DataFrame with low-variance binary features removed.

        Error Handling:
        ---------------
        If variance threshold fitting fails (e.g., no binary columns or too small data), 
        the function catches the ValueError and returns the DataFrame unchanged.
        """
        if not remove_sparse:
            # If sparse removal is disabled, return the DataFrame unchanged
            return df

        # Identify binary columns (only 0 and 1 values)
        binary_cols = [
            col for col in df.columns 
            if set(df[col].dropna().unique()).issubset({0, 1})
        ]

        if binary_cols:
            selector = VarianceThreshold(threshold=0.05 * (1 - 0.05))  # 5% threshold
            try:
                binary_data = selector.fit_transform(df[binary_cols])
                selected_cols = np.array(binary_cols)[selector.get_support()].tolist()

                # Preserve non-binary columns + selected binary columns
                non_binary_cols = df.columns.difference(binary_cols).tolist()
                df = pd.concat([
                    df[non_binary_cols],
                    pd.DataFrame(binary_data, columns=selected_cols)
                ], axis=1)
            except ValueError:
                # Warn if variance threshold fitting fails but continue safely
                print("[Warning] Sparse feature removal failed.")
                return df

        return df

    def _remove_collinear_features(df: pd.DataFrame, remove_collinear: bool) -> pd.DataFrame:
        """
        Remove highly collinear features using Variance Inflation Factor (VIF) analysis.

        Purpose:
        --------
        This function detects multicollinearity among numeric features by calculating 
        the Variance Inflation Factor (VIF). It iteratively removes the feature 
        with the highest VIF until all features have VIF < 5.

        Inputs:
        -------
        df : pd.DataFrame
            The input DataFrame containing numeric features.
        remove_collinear : bool
            Whether to perform collinearity removal.

        Output:
        -------
        pd.DataFrame
            A DataFrame with highly collinear features removed.

        Error Handling:
        ---------------
        No explicit error handling; assumes numeric data is suitable for VIF calculation.
        """
        if not remove_collinear:
            # If collinearity removal is disabled, return the DataFrame unchanged
            return df

        # Select numeric columns only
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

        while numeric_cols:
            # Calculate VIF for each numeric column
            vif = [variance_inflation_factor(df[numeric_cols].values, i) 
                for i in range(len(numeric_cols))]
            max_vif = max(vif)

            if max_vif < 5:
                # Stop if all VIF values are below threshold
                break

            # Find the column with the highest VIF and remove it
            remove_idx = vif.index(max_vif)
            removed_col = numeric_cols.pop(remove_idx)

            if removed_col in all_cols:
                all_cols.remove(removed_col)

        # Return the DataFrame with reduced multicollinearity
        return df[all_cols]


    try:
        df = _remove_duplicates(df)
    except:
        pass

    try:
        df = _handle_missing_values(df)
    except:
        pass

    try:
        df = _detect_outliers(df, contamination)
    except:
        pass

    try:
        df = _process_dates(df, handle_dates, extract_dates)
    except:
        pass

    try:
        df = _clean_text(df, text_cleaning)
    except:
        pass

    try:
        df = _encode_categoricals(df, numeric_threshold, max_onehot_features)
    except:
        pass

    try:
        df = _remove_sparse_features(df, remove_sparse)
    except:
        pass

    return df