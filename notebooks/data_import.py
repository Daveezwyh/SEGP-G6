import mimetypes
import pandas as pd
from pathlib import Path

def load_data(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    file_extension = Path(file_path).suffix.lower()

    if file_extension == '.csv' or mime_type == 'text/csv':
        return pd.read_csv(file_path)
    elif file_extension in ['.xls', '.xlsx'] or \
         mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                       'application/vnd.ms-excel']:
        return pd.read_excel(file_path, engine='openpyxl')
    elif file_extension == '.sqlite' or mime_type == 'application/x-sqlite3':
        from sqlalchemy import create_engine
        engine = create_engine(f'sqlite:///{file_path}')
        return pd.read_sql('SELECT * FROM table_name', engine)
    else:
        raise ValueError(f"Unrecognized file type: {mime_type}")