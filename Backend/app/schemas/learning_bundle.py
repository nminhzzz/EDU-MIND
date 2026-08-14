"""Structured output for one ready-to-study lesson bundle."""

from pydantic import BaseModel, Field, model_validator

from app.agents.quiz_generator.schemas import QuizQuestionItem


class LearningBundle(BaseModel):
    lesson_markdown: str = Field(min_length=500)
    lesson_summary: str = Field(min_length=100, max_length=6000)
    quiz_title: str = Field(min_length=3, max_length=255)
    questions: list[QuizQuestionItem] = Field(min_length=10, max_length=10)

    @model_validator(mode="before")
    @classmethod
    def normalize_question_mix(cls, data):
        if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
            return data
        data = dict(data)
        questions = [
            dict(question) if isinstance(question, dict) else question
            for question in data["questions"]
        ]
        data["questions"] = questions
        for question in questions:
            raw_type = str(question.get("question_type", "mcq")).lower()
            is_essay = "essay" in raw_type or "tự luận" in raw_type or "tu luan" in raw_type
            question["question_type"] = "essay" if is_essay else "mcq"
            if is_essay:
                question["options"] = None
            raw_difficulty = str(question.get("difficulty", "medium")).lower()
            question["difficulty"] = (
                "easy" if "easy" in raw_difficulty or "dễ" in raw_difficulty
                else "hard" if "hard" in raw_difficulty or "khó" in raw_difficulty
                else "medium"
            )

        essays = [question for question in questions if question.get("question_type") == "essay"]
        if len(essays) < 3:
            for question in reversed(questions):
                if question.get("question_type") == "mcq":
                    question["question_type"] = "essay"
                    question["options"] = None
                    essays.append(question)
                    if len(essays) == 3:
                        break
        return data

    @model_validator(mode="after")
    def enforce_seven_three_mix(self):
        essay_count = sum(q.question_type == "essay" for q in self.questions)
        mcq_count = sum(q.question_type == "mcq" for q in self.questions)
        if (mcq_count, essay_count) != (7, 3):
            raise ValueError("Learning bundle must contain exactly 7 MCQ and 3 essay questions")
        return self
