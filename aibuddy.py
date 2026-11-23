from google import genai
from pydantic import BaseModel
import streamlit as st
import os
import time

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎀",
    layout="centered",
)

st.markdown(
    """
    <style>
        .study-hero {
            background: linear-gradient(135deg, #fff0f6 0%, #ffe3ec 100%);
            border: 1px solid #f8bbd0;
            border-radius: 18px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
        }
        .study-badge {
            display: inline-block;
            background-color: #fce4ec;
            color: #ad1457;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            margin-bottom: 0.45rem;
        }
        .study-title {
            color: #880e4f;
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0 0 0.25rem 0;
        }
        .study-subtitle {
            color: #5c2b41;
            font-size: 0.98rem;
            margin: 0;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #f48fb1 !important;
            border-radius: 16px !important;
            background-color: #fffafd;
        }
        .stButton > button[kind="primary"] {
            background-color: #ec407a;
            border-color: #ec407a;
            color: #ffffff;
            border-radius: 10px;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #d81b60;
            border-color: #d81b60;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class MCQ(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str


class QuizResult(BaseModel):
    questions: list[MCQ]


class Flashcard(BaseModel):
    front: str
    back: str


class FlashcardDeck(BaseModel):
    cards: list[Flashcard]


def _call_gemini_with_retry(
    prompt: str,
    schema: type[BaseModel],
    error_label: str,
    max_retries: int = 2,
    retry_delay: float = 1.5,
):
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                },
            )
            return response.parsed
        except Exception as e:
            error_text = str(e)
            is_503 = "503" in error_text or "UNAVAILABLE" in error_text.upper()
            if is_503 and attempt < max_retries:
                time.sleep(retry_delay)
                continue
            st.error(f"Couldn't {error_label} right now: {e}")
            return None
    return None


def generate_mcqs_with_gemini(notes: str, num_questions: int = 4) -> list[MCQ]:
    prompt = f"""
    Create {num_questions} clear, meaningful multiple-choice questions based ONLY on these study notes:
    {notes}

    Rules:
    - Provide exactly 4 answer options per question.
    - Make 'answer' match one of the 4 options word-for-word.
    - Keep 'explanation' concise and clear for a student.
    """
    parsed = _call_gemini_with_retry(prompt, QuizResult, "generate questions")
    if parsed and parsed.questions:
        return parsed.questions
    return []


def generate_flashcards_with_gemini(notes: str, num_cards: int = 5) -> list[Flashcard]:
    prompt = f"""
    Create {num_cards} study flashcards based ONLY on these lecture notes:
    {notes}

    Rules:
    - Make 'front' a concise term, concept, or question.
    - Make 'back' a clear, accurate student-friendly answer or explanation.
    - Stay strictly faithful to the provided notes.
    """
    parsed = _call_gemini_with_retry(prompt, FlashcardDeck, "create flashcards")
    if parsed and parsed.cards:
        return parsed.cards
    return []


def clear_quiz_state() -> None:
    st.session_state.quiz_questions = []
    for key in list(st.session_state.keys()):
        if key.startswith("mcq_"):
            del st.session_state[key]


if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

st.markdown(
    """
    <div class="study-hero">
        <div class="study-badge">🎀 Study Workspace</div>
        <h1 class="study-title">AI Study Buddy</h1>
        <p class="study-subtitle">Your personal AI study assistant for summaries, active-recall flashcards, and practice quizzes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.subheader("Paste Your Lecture Notes")
    notes = st.text_area(
        "Paste your lecture notes here:",
        height=170,
        placeholder="Paste lecture notes, textbook paragraphs, or study summaries...",
    )

tab_analyze, tab_flashcards, tab_quiz = st.tabs(
    ["📝 Analyze Notes", "🃏 AI Flashcards", "🎯 AI Quiz"]
)

# --- Tab 1: Analyze Notes ---
with tab_analyze:
    with st.container(border=True):
        st.subheader("Quick Note Summary")
        summary_length = st.slider(
            "How many sentences should your summary contain?",
            min_value=1,
            max_value=5,
            value=3,
        )
        if st.button("Analyze Notes", type="primary"):
            if notes.strip() == "":
                st.warning("Please enter your lecture notes first!")
            else:
                word_count = len(notes.split())
                sentences = notes.split(".")
                summary = sentences[:summary_length]
                st.success("Summary generated!")
                st.metric("Word Count", word_count)
                st.markdown("#### Your Summary")
                for sentence in summary:
                    if sentence.strip() != "":
                        st.write("- " + sentence.strip() + ".")

# --- Tab 2: AI Flashcards ---
with tab_flashcards:
    with st.container(border=True):
        st.subheader("Active Recall Flashcards")
        num_cards = st.slider(
            "How many flashcards would you like?",
            min_value=2,
            max_value=8,
            value=5,
        )
        if st.button("Create Flashcards", type="primary"):
            if notes.strip() == "":
                st.warning("Please enter your lecture notes first!")
            elif len(notes.split()) < 10:
                st.warning("Please paste at least 10 words of notes so Gemini can create helpful flashcards.")
            else:
                with st.spinner("Generating study flashcards with Gemini..."):
                    new_cards = generate_flashcards_with_gemini(notes, num_cards=num_cards)
                    if new_cards:
                        st.session_state.flashcards = new_cards

        if st.session_state.flashcards:
            st.markdown("#### Your AI Flashcards")
            for i, card in enumerate(st.session_state.flashcards):
                with st.expander(f"Card {i + 1}: {card.front}"):
                    st.write(card.back)

# --- Tab 3: Gemini Multiple-Choice Quiz ---
with tab_quiz:
    with st.container(border=True):
        st.subheader("Multiple-Choice Practice Quiz")
        num_questions = st.slider(
            "How many multiple-choice questions would you like?",
            min_value=2,
            max_value=8,
            value=4,
        )

        col_gen, col_clear = st.columns([2, 1])

        with col_gen:
            if st.button("Generate Quiz", type="primary"):
                if notes.strip() == "":
                    st.warning("Please enter your lecture notes first!")
                elif len(notes.split()) < 10:
                    st.warning("Please paste at least 10 words of notes so Gemini can create good questions.")
                else:
                    clear_quiz_state()
                    with st.spinner("Generating multiple-choice questions with Gemini..."):
                        new_questions = generate_mcqs_with_gemini(notes, num_questions=num_questions)
                        if new_questions:
                            st.session_state.quiz_questions = new_questions

        with col_clear:
            if st.session_state.quiz_questions and st.button("Clear Quiz"):
                clear_quiz_state()
                st.rerun()

        if st.session_state.quiz_questions:
            st.markdown("#### Your AI Quiz")
            user_selections = []
            for i, q in enumerate(st.session_state.quiz_questions):
                st.write(f"**Question {i + 1}:** {q.question}")
                choice = st.radio(
                    f"Select an option for Question {i + 1}:",
                    q.options,
                    key=f"mcq_{i}",
                )
                user_selections.append(choice)

            if st.button("Check Answers & Score"):
                score = 0
                total = len(st.session_state.quiz_questions)
                for i, q in enumerate(st.session_state.quiz_questions):
                    chosen = user_selections[i]
                    if chosen == q.answer:
                        score += 1
                        st.success(f"Question {i + 1}: Correct! — {q.explanation}")
                    else:
                        st.error(f"Question {i + 1}: Not quite. Correct answer: **{q.answer}** — {q.explanation}")

                percentage = (score / total) * 100
                st.info(f"**Final Score:** {score} / {total} ({percentage:.1f}%)")