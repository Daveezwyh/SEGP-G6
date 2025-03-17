from .scanners import *

class ScannerManager:
    def __init__(self):
        self.scanners = [
            scan_df_for_duplicates,
            scan_df_for_missing,
            scan_df_for_outliers,
            scan_df_for_categorical,
        ]
    
    def get_scanners(self):
        return self.scanners