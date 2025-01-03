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
    NO_QUOTE_PROVIDED = "no_quote_provided"
    NO_PREVIOUS_SEARCHES = "no_previous_searches"
    NO_QUOTES_SELECTED = "no_quotes_selected"
    INVALID_INTERVAL = "invalid_interval"
    INVALID_SEGMENT_INDEX = "invalid_segment_index"
    MAX_EXTENSION_LIMIT = "max_extension_limit"
    MAX_CLIP_DURATION = "max_clip_duration"
    EXTRACTION_FAILURE = "extraction_failure"
    NO_SEGMENTS_FOUND = "no_segments_found"
    MESSAGE_TOO_LONG = "message_too_long"
    LIMIT_EXCEEDED_CLIP_DURATION = "limit_exceeded_clip_duration"
    INVALID_RANGE = "invalid_range"
    INVALID_INDEX = "invalid_index"
    NO_MATCHING_SEGMENTS_FOUND = "no_matching_segments_found"
    MAX_CLIPS_EXCEEDED = "max_clips_exceeded"
    CLIP_TIME_EXCEEDED = "clip_time_exceeded"
    NO_MATCHING_CLIPS_FOUND = "no_matching_clips_found"
    CLIP_NOT_FOUND = "clip_not_found"





