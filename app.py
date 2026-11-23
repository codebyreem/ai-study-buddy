import streamlit as st
st.title("AI Study Buddy")
st.write("Your personal AI study assistant")
st.subheader("Let's Study")
notes = st.text_area("Paste your lecture notes here:")
summary_length = st.slider(
    "How many sentences should your summary contain?",
    min_value=1,
    max_value=5,
    value=3
)
if st.button("Analyze Notes"):
    if notes.strip() =="":
        st.warning("Please enter your lecture notes first!")
    else:
        word_count = len(notes.split())
        st.write("Number of words:",word_count)
        sentences = notes.split(".")
        summary= sentences[:summary_length]
        st.success("Summary generated!")
        st.subheader("Your Summary")
        for sentence in summary:
            if sentence.strip() !="":
                st.write("- "+ sentence.strip() +".")

if st.button("Create Flashcards"):
    if notes.strip() =="":
        st.warning("Please enter your lecture notes first!")
    else:
        sentences = notes.split(",")
        st.subheader("Your Flashcards")
        for i, sentence in enumerate(sentences):
            if sentence.strip() !="":
               with st.expander(f"Flashcard {i + 1}"):
                   st.write(sentence.strip())

if st.button("Generate Quiz"):
    if notes.strip() =="":
        st.warning("Please enter your lecture notes first!")
    else:
        sentences = notes.split(".")
        st.subheader("Your Quiz")
        for i, sentence in enumerate(sentences):
            if sentence.strip() !="":
                st.write(f"Question{i + 1}")
                st.write("Which statement appeared in your notes?")
                options = [
                    sentence.strip(),
                    "I don't know",
                    "None of the above"
                ]
                answer = st.radio(
                    f"Choose your answer for Question {i + 1}:",
                    options,
                    key=f"question_{i}"
                )