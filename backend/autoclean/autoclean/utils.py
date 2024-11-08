import pandas as pd
import csv

from api.models import Import, ImportData

def auto_read_csv_file_to_df(file_path) -> pd.DataFrame:
    with open(file_path, 'r') as f:
        first_line = f.readline()
    
    sniffer = csv.Sniffer()
    try:
        delimiter = sniffer.sniff(first_line).delimiter
        return pd.read_csv(file_path, delimiter=delimiter)
    except (csv.Error, pd.errors.ParserError):
        pass
    
    common_delimiters = [',', '\t', ';', '|']
    
    for delimiter in common_delimiters:
        try:
            df = pd.read_csv(file_path, delimiter=delimiter)
            return df
        except pd.errors.ParserError:
            continue
    
    raise ValueError("Could not determine the delimiter for the CSV file.")

def df_from_import_model(import_id: int) -> pd.DataFrame:
    try:
        import_instance = Import.objects.get(id=import_id)
        import_datas = ImportData.objects.filter(import_model=import_instance)

        headers = import_instance.data.get('headers', [])
        df_data = []

        for import_data in import_datas:
            row_data = import_data.data

            if isinstance(row_data, dict):
                row = [row_data.get(header, None) for header in headers]
                df_data.append(row)
            else:
                df_data.append(row_data)

        return pd.DataFrame(df_data, columns=headers)
    
    except Exception as e:
        raise Exception(f"Error occurred while generating dataframe: {str(e)}")