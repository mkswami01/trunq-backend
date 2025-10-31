
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class FormatText(BaseModel):
    title: str
    formattedText: str

class ExtractedItem(BaseModel):
    content: str  # What they said
    intent: Literal [
        "tasks",
        "schedules",
        "reminder",
        "ideas",
        "note",
        "metric",
        "reflection",
        "curiosity",
        "decisions",
        "people"
    ]
    isQuestion: bool
    tags: list[str]  # General topics mentioned
    title: str
    formattedText: str

    scheduled_for:Optional[datetime] = None
    has_deadline: bool = Field(default=False, description="Deadline for the querydo")

class NoteMetadata(BaseModel):
    items: list[ExtractedItem]  # Everything we found


class QueryAnalysis(BaseModel):
    relevant_intents: list[Literal[
        "tasks",
        "schedules",
        "reminder",
        "ideas",
        "note",
        "metric",
        "reflection",
        "curiosity",
        "decisions",
        "people"
    ]] = Field(description="Which intent categories are relevant to this query")

    temporal_range_start: Optional[datetime] = Field(default=None,description="Time context of the query for start of the date and time")
    temporal_range_end: Optional[datetime] = Field(default=None,description="Time context of the query for end of the date and time")

    semantic_query: str = Field(
        description="Refined Query for semantic search in Supermemory"
    )

    requires_synthesis: bool = Field(
        default=True,
        description="Whether results need LLM synthesis or can return raw results"
    )

class QueryResult(BaseModel):
      text: str
      intent: Optional[str] = None
      date: Optional[datetime] = None
      has_deadline: bool = False