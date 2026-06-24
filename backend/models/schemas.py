from pydantic import BaseModel
from typing import List, Optional

class RoleSelection(BaseModel):
    role: str  # "SDE" | "AI Engineer" | "Data Analyst"
    difficulty: Optional[str] = "medium"  # easy | medium | hard

class TranscribedAnswer(BaseModel):
    session_id: str
    question: str
    answer_text: str
    role: str
    question_number: int

class ScoreResult(BaseModel):
    relevance: float        # 0-10
    clarity: float          # 0-10
    technical_accuracy: float  # 0-10
    confidence: float       # 0-10
    overall: float
    feedback: str
    keywords_matched: List[str]
    improvement_tips: List[str]

class SessionSummary(BaseModel):
    session_id: str
    role: str
    candidate_name: Optional[str] = "Candidate"
    scores: List[ScoreResult]
    questions: List[str]
    answers: List[str]
    total_questions: int
    average_score: float
