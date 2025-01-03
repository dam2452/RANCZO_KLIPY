from enum import Enum


class ResponseKey(str, Enum):
    INVALID_ARGS_COUNT = "invalid_args_count"
    CLIP_NOT_EXIST = "clip_not_exist"
    CLIP_DELETED = "clip_deleted"
    CLIP_NAME_EXISTS = "clip_name_exists"
    NO_SEGMENT_SELECTED = "no_segment_selected"
    FAILED_TO_VERIFY_CLIP_LENGTH = "failed_to_verify_clip_length"
    CLIP_SAVED_SUCCESSFULLY = "clip_saved_successfully"
    CLIP_NAME_NOT_PROVIDED = "clip_name_not_provided"
    CLIP_NAME_LENGTH_EXCEEDED = "clip_name_length_exceeded"
    CLIP_LIMIT_EXCEEDED = "clip_limit_exceeded"
    NO_EPISODES_FOUND = "no_episodes_found"
    NO_SAVED_CLIPS = "no_saved_clips"
    NO_PREVIOUS_SEARCH_RESULTS = "no_previous_search_results"
