import pandas as pd
import mimetypes

def load_data(file_path):
    # get file type
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type == 'text/csv':
        return pd.read_csv(file_path)
    elif mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return pd.read_excel(file_path)
    elif mime_type == 'application/vnd.ms-excel':
        return pd.read_excel(file_path)
    elif mime_type == 'application/x-sqlite3':
        from sqlalchemy import create_engine
        engine = create_engine(f'sqlite:///{file_path}')
        return pd.read_sql('SELECT * FROM table_name', engine)
    else:
        raise ValueError(f"unrecogonized file type: {mime_type}")

# # example
# file_path = 'data.csv'  # replace by file path
# df = load_data(file_path)
# print(df.head())