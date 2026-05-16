from enum import StrEnum


class SourceType(StrEnum):
    YOUTUBE = "youtube"
    REDDIT = "reddit"
    NEWS = "news"


class MentionContentType(StrEnum):
    VIDEO = "video"
    REDDIT_SUBMISSION = "reddit_submission"
    REDDIT_COMMENT = "reddit_comment"
    ARTICLE = "article"


class IngestionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
