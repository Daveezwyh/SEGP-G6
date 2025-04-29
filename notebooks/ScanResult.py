from enum import Enum

class SRActionType(Enum):
    """
    Enumeration for action selection types for cleaning operations.

    Purpose:
    --------
    Defines how many actions the user can or must select for a detected issue:
    - ONE_OPTIONAL: User may optionally choose one action.
    - ONE_MANDATORY: User must choose exactly one action.
    - MANY_OPTIONAL: User may choose multiple actions or none.
    - MANY_MANDATORY: User must choose multiple actions.

    Usage:
    ------
    Used inside ScanResult to enforce action selection logic.
    """
    ONE_OPTIONAL = 1
    ONE_MANDATORY = 2
    MANY_OPTIONAL = 3
    MANY_MANDATORY = 4

class ScanResult:
    """
    Representation of a detected data issue within a DataFrame.

    Purpose:
    --------
    Encapsulates information about a problem found during scanning, including:
    - The location of the issue (row, column)
    - A descriptive message
    - The type of user interaction required (via SRActionType)
    - A list of possible cleaning actions

    Constructor Inputs:
    -------------------
    row : int
        The index of the row where the issue is located.
    col : int or str
        The index or name of the column where the issue is located.
    message : str
        A description of the issue.
    action_type : SRActionType
        Specifies how the user should respond (mandatory or optional actions).
    priority : int
        Optional priority indicator for ordering issues (default=1000).
    actions : List[ScanResultAction]
        List of available cleaning actions for this issue.

    Methods:
    --------
    add_action(action)
        Add an action (must be a ScanResultAction) to the issue.
    __repr__()
        String representation of the ScanResult.
    """
    def __init__(self, row=0, col=0, message="", action_type=SRActionType.ONE_OPTIONAL, priority=1000, actions=None):
        self.row = row
        self.col = col
        self.message = message
        self.action_type = action_type
        self.priority = priority
        self.actions = actions if actions is not None else []

    def add_action(self, action):
        """
        Add a cleaning action to the ScanResult.

        Raises:
        -------
        TypeError if the provided action is not a ScanResultAction.
        """
        if isinstance(action, ScanResultAction):
            self.actions.append(action)
        else:
            raise TypeError("Only ScanResultAction instances can be added to actions.")
    
    def __repr__(self):
        return f"ScanResult(row={self.row}, col={self.col}, message='{self.message}', action_type={self.action_type}, priority={self.priority}, actions={self.actions})"

class ScanResultAction:
    """
    Representation of an available cleaning action for a detected issue.

    Purpose:
    --------
    Encapsulates an action that can be applied to fix a detected data issue.

    Constructor Inputs:
    -------------------
    title : str
        Short title of the action.
    description : str
        Detailed description of what the action does.
    cleaner : str
        The function name (as a string) that performs the cleaning.
    cleaner_id : Any
        Optional ID for the cleaner function (can be None).
    activate : bool
        Whether this action is activated by default.
    data : Any
        Optional additional data needed by the cleaner.

    Methods:
    --------
    __repr__()
        String representation of the ScanResultAction.
    """
    def __init__(self, title="Title", description="Description", cleaner="", cleaner_id=None, activate=False, data=None):
        self.title = title
        self.description = description
        self.cleaner = cleaner
        self.cleaner_id = cleaner_id
        self.activate = activate
        self.data = data
    
    def __repr__(self):
        return f"ScanResultAction(title='{self.title}', description='{self.description}', cleaner='{self.cleaner}', cleaner_id={self.cleaner_id}, activate={self.activate}, data={self.data})"
