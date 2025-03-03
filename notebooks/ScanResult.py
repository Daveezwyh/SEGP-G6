from enum import Enum

class SRActionType(Enum):
    DEFAULT = 0
    ONE_OPTIONAL = 1
    ONE_MANDATORY = 2
    MANY_OPTIONAL = 3
    MANY_MANDATORY = 4

class ScanResult:
    def __init__(self, row=0, col=0, message="", action_type=SRActionType.DEFAULT, actions=None):
        self.row = row
        self.col = col
        self.message = message
        self.action_type = action_type
        self.actions = actions if actions is not None else []

    def add_action(self, action):
        if isinstance(action, ScanResultAction):
            self.actions.append(action)
        else:
            raise TypeError("Only ScanResultAction instances can be added to actions.")
    
    def __repr__(self):
        return f"ScanResult(row={self.row}, col={self.col}, message='{self.message}', action_type={self.action_type}, actions={self.actions})"

class ScanResultAction:
    def __init__(self, title="Title", description="Description", cleaner="", cleaner_id=None, activate=False, data=None):
        self.title = title
        self.description = description
        self.cleaner = cleaner
        self.cleaner_id = cleaner_id
        self.activate = activate
        self.data = data
    
    def __repr__(self):
        return f"ScanResultAction(title='{self.title}', description='{self.description}', cleaner='{self.cleaner}', cleaner_id={self.cleaner_id}, activate={self.activate}, data={self.data})"