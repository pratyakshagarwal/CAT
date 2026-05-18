from pydantic import BaseModel, Field
from typing import TypedDict, Optional, List, Dict

_difficulty_label = lambda d: (
    "recall / definition"        if d <= 0.3 else
    "conceptual / single-step"   if d <= 0.6 else
    "multi-step reasoning"       if d <= 0.8 else
    "edge case / deep trap"
)


class Options(BaseModel): A: str; B: str; C: str; D: str
class Tags(BaseModel): subject: str; topic: str; sub_topic: str

class Question(BaseModel):
    q: str
    opt: dict
    solution: str
    explanation: str 
    difficulty: float = Field(ge=0.1, le=1)
    tags: dict

class Question_Schema(BaseModel):
    "Schema for generated question"
    q: str = Field(description="The actual answer text")
    difficulty: float = Field(description="Difficulty level from 0.1 (easy) to 1.0 (hard)")
    tags: Dict[str, str] = Field(
        description="The specific topics or categories the question is derived from (e.g., {'subject': 'Physics', 'topic': 'Kinematics'})"
    )

class Option_Schema(BaseModel):
    opt: Dict[str, str] = Field(
        description="A dictionary of options where keys are labels (e.g., 'A', 'B') and values are the option text"
    )
    solution: str = Field(description="The correct option key (e.g., 'A')")

class Explain_Schema(BaseModel):
    explanation: str = Field(description="Why the correct answer is right and why each wrong option is wrong")

class Eval_Schema(BaseModel):
    q_score:      float = Field(description="Score for question quality (0.0 to 1.0)")
    opt_score:    float = Field(description="Score for options/distractors quality (0.0 to 1.0)")
    exp_score:    float = Field(description="Score for explanation quality (0.0 to 1.0)")
    q_feedback:   str   = Field(description="Specific feedback for question improvement")
    opt_feedback: str   = Field(description="Specific feedback for options improvement")
    exp_feedback: str   = Field(description="Specific feedback for explanation improvement")

class UserSession(TypedDict, total=False):
    # ── Exam context ──────────────────────────────────────────────────────────
    Exam:         Optional[str]       # Exam user is preparing for
    Subjects:     List[str]           # User preferred subjects
    Topics:       List[str]           # Topics to ask questions on

    # ── CAT state ─────────────────────────────────────────────────────────────
    Difficulty:   float               # Current difficulty (0.1 → 1.0)
    RetryCount:   int                 # How many retries have happened

    # ── Current question pipeline ─────────────────────────────────────────────
    Q:            Question_Schema     # Generated question
    Options:      Option_Schema       # Generated options
    Explanation:  Explain_Schema      # Generated explanation

    # ── Evaluator ─────────────────────────────────────────────────────────────
    Eval:         Eval_Schema         # Eval scores + feedback
    RetryQ:       bool                # Question failed threshold
    RetryOpt:     bool                # Options failed threshold
    RetryExp:     bool                # Explanation failed threshold
    EvalFeedback: Optional[str]       # Feedback passed back to failing node

    # ── History ───────────────────────────────────────────────────────────────
    History:      List[Question_Schema]   # All questions asked this session

# -------------------------
# Schemas
# -------------------------
class SessionCreate(BaseModel):
    subjects: List[str] = Field(min_length=1)
    topics: List[str] = Field(min_length=1)
    exam: Optional[str] = None


class GenerateQuestionRequest(BaseModel): session_id: str
class GenerateInsightRequest(BaseModel): session_id: str


class QuestionResponse(BaseModel):
    id: str
    q_text: str
    options: Dict[str, str]
    solution: str
    explanation: str
    difficulty: float
    subject: Optional[str]
    topic: Optional[str]
    sub_topic: Optional[str]

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    user_answer: str