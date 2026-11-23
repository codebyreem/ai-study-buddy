# 🎀 AI Study Buddy

A pastel pink-themed AI study assistant built with **Python**, **Streamlit**, and the **Google Gemini API**. Paste your lecture notes to generate quick summaries, active-recall flashcards, and customizable multiple-choice practice quizzes.

## ✨ Features

- **📝 Note Analyzer:** Calculates word count and extracts a customizable sentence-level summary from lecture notes.
- **🃏 AI Flashcards:** Uses Google Gemini with structured Pydantic schemas to turn notes into interactive front/back study cards.
- **🎯 Customizable AI Quiz:** Generates multiple-choice questions (2–8 questions) with instant answer checking, explanations, final percentage scoring, and a one-click **Clear Quiz** reset.
- **🛡️ Resilient API Handling:** Built-in automatic retry logic handles temporary `503 UNAVAILABLE` model demand spikes gracefully.
- **🌸 Custom Pink UI:** Clean tabbed workspace styled with `.streamlit/config.toml` and soft pastel card containers.

## 🛠️ Tech Stack

- **Frontend / UI:** Streamlit
- **AI Model & SDK:** Google Gemini (`google-genai`)
- **Data Validation:** Pydantic
- **Language:** Python 3.10+

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone [https://github.com/YOUR-USERNAME/ai-study-buddy.git](https://github.com/YOUR-USERNAME/ai-study-buddy.git)
cd ai-study-buddy