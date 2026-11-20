"""Quiz generation powered by PydanticAI and Anthropic."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field, model_validator
from pydantic_ai import Agent


class QuizQuestion(BaseModel):
    """One multiple-choice quiz question."""

    question: str = Field(min_length=5, description="The question shown to the learner")
    options: list[str] = Field(min_length=2, max_length=6)
    correct_option: int = Field(ge=0, description="Zero-based index into options")
    explanation: str = Field(min_length=5, description="A short explanation of the correct answer")

    @model_validator(mode="after")
    def validate_answer_and_options(self) -> "QuizQuestion":
        if len(self.options) < 2:
            raise ValueError("A question must have at least two options")
        if any(not option.strip() for option in self.options):
            raise ValueError("Answer options cannot be blank")
        if len({option.strip().casefold() for option in self.options}) != len(self.options):
            raise ValueError("Answer options must be unique")
        if self.correct_option >= len(self.options):
            raise ValueError("correct_option must refer to an available option")
        return self


class Quiz(BaseModel):
    """Structured quiz returned by the model."""

    title: str = Field(min_length=1)
    questions: list[QuizQuestion] = Field(min_length=1, max_length=10)


def generate_quiz(topic: str, difficulty: str, question_count: int) -> Quiz:
    """Generate a quiz for the requested topic and learner level."""
    model = os.getenv("ANTHROPIC_MODEL", "").strip()
    if not model:
        raise ValueError(
            "Set ANTHROPIC_MODEL in your .env file (for example: anthropic:<model-id>)."
        )

    agent: Agent[None, Quiz] = Agent(
        model,
        output_type=Quiz,
        system_prompt=(
            "You are a careful educational quiz author. Write clear, accurate questions. "
            "Each question must have plausible, distinct answer choices and exactly one "
            "correct answer. Use a zero-based index for correct_option. Keep explanations "
            "brief and helpful. If the learner supplies a topic, focus only on that topic."
        ),
    )
    prompt = (
        f"Create exactly {question_count} multiple-choice questions about: {topic}.\n"
        f"Difficulty: {difficulty}.\n"
        "Use 4 options per question where practical, and make the quiz suitable for learning."
    )
    result = agent.run_sync(prompt)
    quiz = result.output

    if len(quiz.questions) != question_count:
        raise ValueError(
            f"The model returned {len(quiz.questions)} questions instead of {question_count}. "
            "Please try generating the quiz again."
        )
    return quiz
