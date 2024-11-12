class ScanResult:
    def __init__(self, row=0, col=0, message="", cleaner="", activate=False):
        self.row = row
        self.col = col
        self.message = message
        self.cleaner = cleaner
        self.activate = activate

    def __repr__(self):
        return f"ScanResult(row={self.row}, col={self.col}, message='{self.message}', cleaner='{self.cleaner}', activate={self.activate})"