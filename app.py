import streamlit as st
from pypdf import PdfReader
import json

st.set_page_config(layout = "wide", page_title = "Exam Classifier")
st.title("Exam Classifier")

with open("topics.json", mode = "r", encoding = "utf-8") as file:
    topics_dict = json.load(file)

file = st.file_uploader(label="Selecciona un archivo...", type = ["pdf"])

def parse_text(text):
    text = text.split("\n")
    for index, line in enumerate(text):
        if "tema" in line.lower():
            text = text[index:]
            break
    
    text = [line for line in text if line != "\n"]
    exercises = []

    topic = None
    for line in text:
        if "tema" in line.lower():
            topic = line.split(":")[1].strip().lower()
            topic = topics_dict[topic]
        elif "Ju" in line or "Reserva" in line:
            exercises.append(line[2:])  # remove " · "
        else:
            pass
    if topic and exercises:
        return topic, exercises

if file:
    reader = PdfReader(file)
    first_page = reader.pages[0]
    text = first_page.extract_text()
    topic, exercises = parse_text(text)

    # load exercise types for selected topic
    exercise_types = None
    try:
        with open("exercise_types.json", "r", encoding="utf-8") as file:
            exercise_types = json.load(file)
    except FileNotFoundError:
        print(f"El archivo {topic}.json, con clasificaciones de ejercicios, no existe.")

    st.subheader(f"Tema: {topic.title()}")

    col1, col2 = st.columns(2)
    
    with col1:
        
        selected_exercise = st.selectbox(
            label = "Examen:",
            options= exercises,
        )

        if selected_exercise:
            exam, exercise = selected_exercise.split(", ")

    with col2:
        if exercise_types:
            ex_type = st.selectbox(
                label = "Tipo de ejercicio",
                options = exercise_types[topic]
            )

    st.text(f"Convocatoria: {exam} \t|\t Ejercicio: {exercise} \t|\t Tipo ejercicio: {ex_type}")