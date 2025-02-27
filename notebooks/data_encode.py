import pandas as pd

def encode_categorical_features(df):
    df_encoded = df.copy()
    
    for column in df_encoded.select_dtypes(include=['object', 'category']).columns:
        unique_values = df_encoded[column].nunique()

        if unique_values <= 10:
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
