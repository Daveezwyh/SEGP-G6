import pandas as pd
from fancyimpute import KNN
from sklearn.ensemble import IsolationForest

def remove_duplicates(df):
    df = df.drop_duplicates().reset_index(drop=True)
    return df

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

def remove_outliers(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    X = df.select_dtypes(include=[float, int])

    X_no_missing = X.dropna()

    iforest = IsolationForest(
        n_estimators=100,
        max_samples='auto',
        contamination=contamination,
        max_features=X_no_missing.shape[1],
        bootstrap=False,
        n_jobs=-1,
        random_state=1
    )

    labels = iforest.fit_predict(X_no_missing)
      
    inlier_indices = X_no_missing.index[labels == 1]
    df_inliers = df.loc[inlier_indices]

    return df_inliers
