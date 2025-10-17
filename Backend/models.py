from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class FileUploadResponse(BaseModel):
    message: str
    processed_files: int
    failed_files: int
    total_files: int

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str] = []
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"

class ProcessingStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class FileProcessingResult(BaseModel):
    filename: str
    status: ProcessingStatus
    error: Optional[str] = None
    chunks_created: int = 0