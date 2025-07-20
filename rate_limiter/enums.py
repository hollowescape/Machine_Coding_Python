from enum import Enum

class AlgorithmType(Enum):
    SLIDING_WINDOW_LOG = "SLIDING_WINDOW_LOG"
    TOKEN_BUCKET = "TOKEN_BUCKET"
    FIXED_WINDOW = "FIXED_WINDOW"

