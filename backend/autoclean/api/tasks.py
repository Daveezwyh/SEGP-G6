from celery import shared_task
import time, logging, os
import pandas as pd

from .models import TaskProgress, Import, ImportData, ImportDataOriginal, ImportScanResult, ImportScanResultAction, Cleaner
from autoclean.utils import auto_read_csv_file_to_df, df_from_import_model, cleaner_fn_activate, save_import_data_from_df
from autoclean.scanners.manager import ScannerManager
from autoclean.scanners.result import ScanResult
from autoclean.autocleaner.autocleaner import clean_data

logger = logging.getLogger('django')

@shared_task(bind=True)
def test_task(self, args):
    try:
        task_progress_id = args["task_progress_id"]
        task_progress = TaskProgress.objects.get(id=task_progress_id)

        task_progress.status = TaskProgress.Status.PENDING.value
        task_progress.message = "Task retrieved from queue. Processing task..."
        task_progress.save()

        for i in range(30):
            task_progress.message = f"Processing task, step {i + 1} of 30"
            task_progress.percentage = ((i + 1) / 30) * 100
            task_progress.save()
            time.sleep(1)
        
        task_progress.status = TaskProgress.Status.COMPLETED.value
        task_progress.message = "Task completed successfully."
        task_progress.save()
        
        return args
    except Exception as e:
        logger.error(f"Error in task {self.name}: {str(e)}", exc_info=True)
        raise

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
                
                try:
                    save_import_data_from_df(import_instance, df)
                except Exception as e:
                    logger.error(f"Error saving import data from DataFrame: {str(e)}", exc_info=True)
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
def copy_import_data_original(self, args):
    try:
        task_progress_id = args["task_progress_id"]
        import_id = args["import_id"]

        import_instance = Import.objects.get(id=import_id)
        task_progress = TaskProgress.objects.get(id=task_progress_id)

        task_progress.message = "Saving original copy of import data records..."
        task_progress.save()

        import_data_records = ImportData.objects.filter(import_model=import_instance)

        original_records = [
            ImportDataOriginal(
                import_model=import_instance,
                data=import_data.data,
                created_at=import_data.created_at
            )
            for import_data in import_data_records
        ]

        ImportDataOriginal.objects.bulk_create(original_records)

        task_progress.message = "Original copy of import data records saved successfully."
        task_progress.save()

        return args
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
                import_scan_result = ImportScanResult.objects.create(
                    row=scan_result.row,
                    col=scan_result.col,
                    message=scan_result.message,
                    action_type=scan_result.action_type.value,
                    import_model=import_instance
                )

                for action in scan_result.actions:
                    ImportScanResultAction.objects.create(
                        title=action.title,
                        description=action.description,
                        cleaner=action.cleaner,
                        cleaner_id=action.cleaner_id,
                        activate=action.activate,
                        data=action.data,
                        import_scan_result=import_scan_result
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

@shared_task(bind=True)
def clean_import(self, args):
    try:
        task_progress_id = args["task_progress_id"]
        import_id = args["import_id"]

        import_instance = Import.objects.get(id=import_id)
        task_progress = TaskProgress.objects.get(id=task_progress_id)

        try:
            import_instance.status = Import.Status.PROCESSING.value
            import_instance.save()

            task_progress.status = TaskProgress.Status.PROCESSING.value
            task_progress.save()

            df:pd.DataFrame = df_from_import_model(import_instance.id)

            if df.empty:
                raise ValueError("The DataFrame is empty and cannot be cleaned.")

            imp_scan_results = import_instance.scan_results.all().order_by('priority', 'id')

            for imp_scan_result in imp_scan_results:
                scan_result: ScanResult = imp_scan_result.transform()

                imp_actions = imp_scan_result.actions.all()

                for imp_action in imp_actions:
                    if imp_action.activate and imp_action.cleaner:
                        cleaner = Cleaner.objects.filter(fn_name=imp_action.cleaner, status=1).first()

                        if cleaner:
                            #logger.info(f"{cleaner.definition}")
                            cleaner_fn = cleaner_fn_activate(cleaner.definition)
                            df:pd.DataFrame = cleaner_fn(scan_result, df)

                        else:
                            continue
            
            save_import_data_from_df(import_instance, df)
            
            import_instance.status = Import.Status.COMPLETED.value
            import_instance.save()

            task_progress.status = TaskProgress.Status.COMPLETED.value
            task_progress.percentage = 100
            task_progress.message = "Cleaning process of import data completed."
            task_progress.save()

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
def full_auto_clean_import(self, args):
    try:
        task_progress_id = args["task_progress_id"]
        import_id = args["import_id"]

        import_instance = Import.objects.get(id=import_id)
        task_progress = TaskProgress.objects.get(id=task_progress_id)

        try:
            import_instance.status = Import.Status.PROCESSING.value
            import_instance.save()

            task_progress.status = TaskProgress.Status.PROCESSING.value
            task_progress.save()

            df:pd.DataFrame = df_from_import_model(import_instance.id)

            if df.empty:
                raise ValueError("The DataFrame is empty and cannot be cleaned.")
            
            df = clean_data(df, task_progress)
            save_import_data_from_df(import_instance, df)
            
            import_instance.status = Import.Status.COMPLETED.value
            import_instance.save()

            task_progress.status = TaskProgress.Status.COMPLETED.value
            task_progress.percentage = 100
            task_progress.message = "Cleaning process of import data completed."
            task_progress.save()

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