import pandas as pd
import csv
import datetime
from rest_framework.pagination import PageNumberPagination
from typing import Callable
import ast
import types
from api.models import Import, ImportData
from autoclean.scanners.result import ScanResult, ScanResultAction
from django.core.exceptions import ObjectDoesNotExist

def auto_read_csv_file_to_df(file_path) -> pd.DataFrame:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
        
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(first_line).delimiter
        except csv.Error:
            delimiter = None

        common_delimiters = [',', '\t', ';', '|']
        delimiters_to_try = [delimiter] + common_delimiters if delimiter else common_delimiters

        for delim in delimiters_to_try:
            try:
                df = pd.read_csv(file_path, delimiter=delim, encoding='utf-8', parse_dates=True)

                for col in df.select_dtypes(include=['datetime64[ns]', 'timedelta64[ns]']):
                    df[col] = df[col].apply(lambda x: x.to_pydatetime() if not pd.isna(x) else None)

                return df
            except (pd.errors.ParserError, pd.errors.EmptyDataError):
                continue

        raise ValueError("Could not determine the delimiter for the CSV file.")

    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except pd.errors.EmptyDataError:
        raise ValueError("The file is empty.")

def save_import_data_from_df(import_instance: Import, df: pd.DataFrame) -> None:
    if not isinstance(import_instance, Import):
        raise TypeError(f"Expected 'import_instance' to be an instance of Import, got {type(import_instance)}")

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected 'df' to be a pandas DataFrame, got {type(df)}")

    if df.empty:
        raise Exception("The provided DataFrame is empty and cannot be processed.")
    
    for col in df.select_dtypes(include=['datetime64[ns]', 'timedelta64[ns]']):
        df[col] = df[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)

    headers = df.columns.tolist()
    total_rows = len(df)

    current_data = import_instance.data or {}
    current_data.update({'headers': headers, 'total_rows': total_rows})
    import_instance.data = current_data
    import_instance.save()

    ImportData.objects.filter(import_model=import_instance).delete()

    import_data_objects = [
        ImportData(import_model=import_instance, data={
            header: (
                value.isoformat() if isinstance(value, (pd.Timestamp, datetime.datetime)) else 
                (None if pd.isna(value) else value)
            )
            for header, value in zip(headers, row)
        })
        for row in df.itertuples(index=False, name=None)
    ]

    if import_data_objects:
        ImportData.objects.bulk_create(import_data_objects)

def df_from_import_model(import_id: int) -> pd.DataFrame:
    try:
        import_instance = Import.objects.get(id=import_id)
        import_datas = ImportData.objects.filter(import_model=import_instance)

        headers = import_instance.data.get('headers', [])
        if not headers:
            raise ValueError("No headers found in the import instance.")
        
        df_data = [
            [import_data.data.get(header, None) if isinstance(import_data.data, dict) else None for header in headers]
            for import_data in import_datas
        ]

        df = pd.DataFrame(df_data, columns=headers)

        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass

        return df

    except ObjectDoesNotExist:
        print(f"Import with ID {import_id} does not exist.")
        return pd.DataFrame()

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return pd.DataFrame()

    except Exception as e:
        print(f"Unexpected error: {e}")
        return pd.DataFrame()

class AutocleanAPIPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def cleaner_fn_activate(func_string: str) -> Callable:
    """
    Parses, validates, and activates a function from a string, ensuring necessary imports exist.
    
    Args:
        func_string (str): The function definition as a string.

    Returns:
        Callable: The extracted function if valid, else raises an error.
    """
    try:
        # Parse the string into an AST (Abstract Syntax Tree)
        parsed_code = ast.parse(func_string)

        # Find all function definitions
        func_defs = [node for node in parsed_code.body if isinstance(node, ast.FunctionDef)]

        # Ensure there's exactly one function
        if len(func_defs) != 1:
            raise ValueError("The input must contain exactly one function definition.")

        # Extract function name
        func_name = func_defs[0].name

        # Execution Namespace (Inject necessary imports)
        execution_namespace = {
            "ScanResult": ScanResult,  # Inject ScanResult
            "ScanResultAction": ScanResultAction,  # Inject ScanResult.Action
            "pandas": pd,              # Inject pandas (allows `pandas.DataFrame`)
            "pd": pd,                   # Allow both `pandas` and `pd`
        }

        # Execute in the caller's namespace, including ScanResult and pandas
        exec(func_string, execution_namespace)

        # Retrieve the function
        func = execution_namespace.get(func_name)

        # Ensure it's actually a function
        if not isinstance(func, types.FunctionType):
            raise ValueError("Extracted object is not a function.")

        return func

    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {e}")