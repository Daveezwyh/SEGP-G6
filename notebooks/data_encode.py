import pandas as pd

def encode_categorical_features(df):
    """
    Convert categorical features with up to 10 unique values into numeric labels.
    Features with more than 10 unique values are retained in their original form.
    
    :param df: Input dataframe
    :return: Dataframe with encoded features
    """
    df_encoded = df.copy()  # Copy the original dataframe to avoid modifying it directly
    
    for column in df_encoded.select_dtypes(include=['object', 'category']).columns:
        unique_values = df_encoded[column].nunique()
        
        # Check if the column has up to 10 unique values
        if unique_values <= 10:
            # Convert categorical values to numeric labels starting from 1
            df_encoded[column] = pd.factorize(df_encoded[column])[0] + 1
        else:
            print(f"Column '{column}' has {unique_values} unique values, keeping original.")
    
    return df_encoded

# # Test case with a column containing more than 10 unique values
# df_test = pd.DataFrame({
#     'Animal': ['dog', 'cat', 'fish', 'dog', 'cat', 'bird', 'lion', 'tiger', 
#                'bear', 'shark', 'whale', 'penguin'],  # 12 unique values
#     'Size': ['small', 'medium', 'large', 'small', 'medium', 'large', 
#              'small', 'medium', 'large', 'small', 'medium', 'large'],
#     'Color': ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 
#               'black', 'white', 'gray', 'pink', 'brown', 'cyan']  # 12 unique values
# })

# df_encoded_test = encode_categorical_features(df_test)
# print(df_encoded_test)
