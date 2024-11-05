from celery import shared_task
import time, logging, os
import pandas as pd

from .models import Import, ImportData
from autoclean.utils import auto_read_csv_file_to_df

logger = logging.getLogger('django')

@shared_task(bind=True)
def add(self, x, y):
    time.sleep(3)
    return x + y

@shared_task(bind=True)
def read_file_to_import_data(self, import_id):
    try:
        import_instance = Import.objects.get(id=import_id)

        if import_instance.file:
            file_path = import_instance.file.path
            _, file_extension = os.path.splitext(file_path)

            try:
                if file_extension.lower() == '.csv':
                    df = auto_read_csv_file_to_df(file_path)
                elif file_extension.lower() in ['.xls', '.xlsx']:
                    df = pd.read_excel(file_path)
                else:
                    logger.error(f"Unsupported file format: {file_extension}")
                    raise ValueError("Unsupported file format")
            except FileNotFoundError:
                logger.error(f"File not found at path: {file_path}", exc_info=True)
                raise
            except pd.errors.EmptyDataError:
                logger.error(f"The file at {file_path} is empty.", exc_info=True)
                raise ValueError("File is empty.")
            except pd.errors.ParserError:
                logger.error(f"Failed to parse the file at {file_path}.", exc_info=True)
                raise ValueError("File format is invalid or corrupt.")
            except Exception as e:
                logger.error(f"Unexpected error reading the file at {file_path}: {str(e)}", exc_info=True)
                raise ValueError("An unexpected error occurred while reading the file.")
            
            headers = df.columns.tolist()

            current_data = import_instance.data or {}

            current_data.update({
                'headers': headers,
                'total_rows': len(df)
            })
            
            import_instance.data = current_data
            import_instance.save()

            for row in df.itertuples(index=False, name=None):
                row_data = {header: value for header, value in zip(headers, row)}
                
                try:
                    ImportData.objects.create(
                        import_model=import_instance,
                        data=row_data
                    )
                except Exception as e:
                    logger.error(f"Error creating ImportData: {row_data}, error: {str(e)}", exc_info=True)
                    raise

            return True
        else:
            logger.error("File not found in Import instance.")
            return False

    except Import.DoesNotExist:
        logger.error(f"Import with ID {import_id} does not exist.", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error in task {self.name}: {str(e)}", exc_info=True)
        raise