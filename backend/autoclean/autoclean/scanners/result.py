class ScanResult:
    def __init__(self, row=0, col=0, message=""):
        self.row = row
        self.col = col
        self.message = message

    def __repr__(self):
        return f"ScanResult(row={self.row}, col={self.col}, message='{self.message}')"

class ScannerAttribute:
    def __init__(self, name="Scanner Name", description="Scanner Description"):
        self.name = name
        self.description = description