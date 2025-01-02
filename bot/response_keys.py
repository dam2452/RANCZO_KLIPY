from enum import Enum

class ResponseKey(str, Enum):
    INVALID_ARGS_COUNT = "invalid_args_count"
    CLIP_NOT_EXIST = "clip_not_exist"
    CLIP_DELETED = "clip_deleted"
