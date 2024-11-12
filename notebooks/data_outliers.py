import pandas as pd
from sklearn.ensemble import IsolationForest

def scan_outliers(df):
    X = df.select_dtypes(include=[float, int])

    # Set up the IsolationForest model
    iforest = IsolationForest(
        n_estimators=100, 
        max_samples='auto',
        contamination=0.05, 
        max_features=X.shape[1],
        bootstrap=False, 
        n_jobs=-1, 
        random_state=1
    )
    
    # Predict outliers and label them in the DataFrame
    df['label'] = iforest.fit_predict(X)

    # Collect outlier messages
    outlier_message = []
    for idx, row in df.iterrows():
        if row['label'] == -1:
            outlier_message.append(f"Row {idx} has outlier")

    return outlier_message

def remove_outliers(df):
    # Filter out rows labeled as outliers
    clean_df = df[df['label'] == 1].copy()
    clean_df.drop(columns=['label'], inplace=True)
    
    return clean_df