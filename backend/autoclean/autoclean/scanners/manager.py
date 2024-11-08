from .scanners import *

class ScannerManager:
    def __init__(self):
        self.scanners = [
            scan_df_for_something
        ]
    
    def get_scanners(self):
        return self.scanners