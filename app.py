import streamlit as st
import openai
import pyttsx3
import speech_recognition as sr
from datetime import datetime
from roleplays import roleplays

openai.api_key = "YOUR_OPENAI_API_KEY"

st.title("Roleplay Simulation Tool")

# Select roleplay
roleplay_name = st.selectbox("Select Roleplay", list(roleplays.keys()))
roleplay = roleplays[roleplay_name]

# Select language
language = st.radio("Language", roleplay["language"])

# Show student instructions
st.subheader("Instructions")
st.write(roleplay["student_instructions"])

# Preparation timer
prep_time = st.slider("Preparation time (minutes)", 1, 10, 5)
if st.button("Start Preparation"):
    st.write(f"Preparation started for {prep_time} minutes.")

# Audio input option
use_speech = st.checkbox("Use microphone input (speech-to-text)?")

if use_speech:
    st.write("Click 'Record' to capture your speech.")
    if st.button("Record"):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Recording...")
            audio = r.listen(source)
            try:
                student_input = r.recognize_google(audio, language="en-US" if language=="English" else "de-DE")
                st.write("You said:", student_input)
            except Exception as e:
                st.write("Error recognizing speech:", e)
else:
    student_input = st.text_input("Your message:")

if st.button("Send") and student_input:
    # Construct AI prompt
    prompt = f"""
You are {roleplay['name']} AI actor.
Instructions: {roleplay['ai_instructions'].format(language=language)}
Factual goal: {roleplay['factual_goal']}
Relationship goal: {roleplay['relationship_goal']}

Student: {student_input}
AI:
"""
    # Call OpenAI GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    ai_reply = response['choices'][0]['message']['content']
    st.write(f"AI: {ai_reply}")

    # TTS
    engine = pyttsx3.init()
    engine.say(ai_reply)
    engine.runAndWait()

    # Save transcript
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"transcripts/{roleplay_name}_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(f"Student: {student_input}\nAI: {ai_reply}\n")
    st.success("Transcript saved!")
