import pandas as pd

def display_data(df, display_option, num_rows):
    """
    Display data content based on the user's selected display option.
    
    Parameters:
    - df: DataFrame.
    - display_option: Display option, default is to show the first few rows. Options include:
        - "head": Show the first few rows
        - "tail": Show the last few rows
        - "summary": Show descriptive statistics
        - "columns": Show column names
    - num_rows: Number of rows to display when using "head" or "tail", default is 5 rows.
    """
    if display_option == "head":
        return df.head(num_rows)
    elif display_option == "tail":
        return df.tail(num_rows)
    elif display_option == "sample":
        return df.sample(num_rows)
    elif display_option == "summary":
        return df.describe()
    elif display_option == "columns":
        return df.columns
    elif display_option == "shape":
        return df.shape
    elif display_option == "info":
        return df.info()
    elif display_option == "all":
        return df
    else:
        raise ValueError("Invalid display option. Choose from 'head', 'tail', 'summary', or 'columns'.")

# df.shape
# df.info()

# # Choose display option
# display_option = "summary"  # User can set this to "head", "tail", "summary", or "columns"
# output = display_data(df, display_option, display_numbenum_rows)
# print(output)