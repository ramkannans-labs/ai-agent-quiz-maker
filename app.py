"""Local Streamlit interface for the PydanticAI quiz maker."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from quiz_agent import Quiz, generate_quiz  # noqa: E402


st.set_page_config(page_title="AI Quiz Maker", page_icon="🧠", layout="centered")
st.title("🧠 AI Quiz Maker")
st.caption("Create a quick practice quiz, answer it, and review what you learned.")


def clear_quiz() -> None:
    """Clear quiz state and rerun the app for a fresh quiz."""
    for key in ("quiz", "submitted", "last_error"):
        st.session_state.pop(key, None)
    for key in list(st.session_state):
        if key.startswith("answer_"):
            st.session_state.pop(key, None)
    st.rerun()


def configuration_is_ready() -> bool:
    """Show setup guidance when the user has not configured Anthropic yet."""
    missing = []
    if not os.getenv("ANTHROPIC_API_KEY", "").strip():
        missing.append("ANTHROPIC_API_KEY")
    if not os.getenv("ANTHROPIC_MODEL", "").strip():
        missing.append("ANTHROPIC_MODEL")
    if missing:
        st.info(
            "Before generating a quiz, copy `.env.example` to `.env` and fill in: "
            + ", ".join(f"`{item}`" for item in missing)
            + ". Then restart Streamlit. Your API key stays in your local `.env` file."
        )
        return False
    return True


if "quiz" not in st.session_state:
    with st.form("quiz_setup"):
        topic = st.text_input("What do you want to practise?", placeholder="e.g. Photosynthesis")
        difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
        question_count = st.slider("Number of questions", min_value=3, max_value=10, value=5)
        create_quiz = st.form_submit_button("Create my quiz", type="primary")

    if create_quiz:
        if not topic.strip():
            st.warning("Enter a topic to create your quiz.")
        elif not configuration_is_ready():
            pass
        else:
            with st.spinner("Creating your quiz…"):
                try:
                    st.session_state.quiz = generate_quiz(
                        topic=topic.strip(),
                        difficulty=difficulty,
                        question_count=question_count,
                    )
                    st.session_state.submitted = False
                    st.rerun()
                except Exception as exc:  # show a helpful UI message, not a traceback
                    st.error(
                        f"The quiz could not be generated ({type(exc).__name__}). "
                        "Check that your model name and API key in `.env` are correct, "
                        "then try again. No API key is displayed here."
                    )
                    if isinstance(exc, ValueError):
                        st.caption(str(exc))
else:
    quiz: Quiz = st.session_state.quiz
    st.subheader(quiz.title)
    st.write("Choose one answer for each question, then submit to see your results.")

    with st.form("quiz_answers"):
        answers: list[int] = []
        for index, question in enumerate(quiz.questions):
            st.markdown(f"**{index + 1}. {question.question}**")
            answer = st.radio(
                "Select an answer",
                options=range(len(question.options)),
                format_func=lambda option_index, options=question.options: options[option_index],
                key=f"answer_{index}",
                label_visibility="collapsed",
            )
            answers.append(answer)
        submitted = st.form_submit_button("Submit answers", type="primary")

    if submitted:
        st.session_state.submitted = True
        st.session_state.answers = answers
        st.rerun()

    if st.session_state.get("submitted"):
        chosen_answers: list[int] = st.session_state.answers
        correct = sum(
            chosen == question.correct_option
            for chosen, question in zip(chosen_answers, quiz.questions)
        )
        total = len(quiz.questions)
        st.divider()
        st.subheader("Your results")
        st.metric("Score", f"{correct} / {total}")
        if correct == total:
            st.success("Perfect score! Excellent work.")
        elif correct == 0:
            st.info("Good practice! Review the explanations and give it another try.")
        else:
            st.success(f"You got {correct} of {total} correct. Keep it up!")

        for index, (question, chosen) in enumerate(zip(quiz.questions, chosen_answers)):
            is_correct = chosen == question.correct_option
            st.markdown(f"**{index + 1}. {'✅ Correct' if is_correct else '❌ Not quite'}**")
            if not is_correct:
                st.write(f"Your answer: {question.options[chosen]}")
            st.write(f"Correct answer: {question.options[question.correct_option]}")
            st.caption(question.explanation)

    st.divider()
    if st.button("Start a new quiz"):
        clear_quiz()
