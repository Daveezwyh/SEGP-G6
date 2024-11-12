from celery import shared_task
import time, logging, os
import pandas as pd

from .models import TaskProgress, Import, ImportData, ImportScanResult
from autoclean.utils import auto_read_csv_file_to_df, df_from_import_model
from autoclean.scanners.manager import ScannerManager

logger = logging.getLogger('django')

@shared_task(bind=True)
def add(self, x, y):
    time.sleep(3)
    return x + y

@shared_task(bind=True)
def read_file_to_import_data(self, args):
    try:
        task_progress_id = args["task_progress_id"]
        import_id = args["import_id"]

        import_instance = Import.objects.get(id=import_id)
        task_progress = TaskProgress.objects.get(id=task_progress_id)

        try:
            task_progress.status = TaskProgress.Status.PROCESSING.value
            task_progress.save()

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

                return args
            else:
                raise Exception("File not found in Import instance.")
            
        except Exception as e:
            task_progress.status = TaskProgress.Status.ERROR.value
            task_progress.error = str(e)
            task_progress.save()
            raise

    except Import.DoesNotExist:
        logger.error(f"Import with ID {import_id} does not exist.", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error in task {self.name}: {str(e)}", exc_info=True)
        raise

@shared_task(bind=True)
def scan_import(self, args):
    try:
        task_progress_id = args["task_progress_id"]
        import_id = args["import_id"]

        import_instance = Import.objects.get(id=import_id)
        task_progress = TaskProgress.objects.get(id=task_progress_id)

        try:
            df = df_from_import_model(import_instance.id)

            scanner_manager = ScannerManager()
            scanners = scanner_manager.get_scanners()

            scan_results = []

            for scanner in scanners:
                scan_results += scanner(df)
            
            for scan_result in scan_results:
                ImportScanResult.objects.create(
                    row=scan_result.row,
                    col=scan_result.col,
                    message=scan_result.message,
                    cleaner=scan_result.cleaner,
                    activate=scan_result.activate,
                    import_model=import_instance
                )

            task_progress.status = TaskProgress.Status.COMPLETED.value
            task_progress.percentage = 100
            task_progress.message = "Scanning of import data completed."
            task_progress.save()
            
        except Exception as e:
            task_progress.status = TaskProgress.Status.ERROR.value
            task_progress.error = str(e)
            task_progress.save()
            raise

    except Exception as e:
        logger.error(f"Error in task {self.name}: {str(e)}", exc_info=True)