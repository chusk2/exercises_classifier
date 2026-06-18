import streamlit as st
from pypdf import PdfReader
import json
import pandas as pd

st.set_page_config(layout = "centered", page_title = "Exam Classifier")
st.title("Exam Classifier")

with open("topics.json", mode = "r", encoding = "utf-8") as file:
    topics_dict = json.load(file)

file = st.file_uploader(label="Selecciona un archivo...", type = ["pdf"])

def extract_info_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = reader.pages[0].extract_text()
    text_lines = [line.strip() for line in text.split("\n") if line.strip()][3:]
    
    return text_lines

def parse_lines(text_lines):
    
    year = int(text_lines[0])
    subject = text_lines[1].lower()
    topic = text_lines[2].split(":")[1].strip().lower()
    topic = topics_dict[topic]

    # define the data dictionary
    data = {
           "year" : year,
           "subject" : subject,
           "topic" : topic,
           "exercises" : []
    }

    for line in text_lines[3:]:
        line = line[2:]  # remove "• "
        components = line.split(', ')
        data["exercises"].append((components[0], ', '.join(components[1:]) ) )
    
    return data


if file:
    
    text_lines = extract_info_from_pdf(file)
    data = parse_lines(text_lines)

    # load exercise types for selected topic
    exercise_types = None
    try:
        with open("exercise_types.json", "r", encoding="utf-8") as file:
            exercise_types = json.load(file)
    except FileNotFoundError:
        print(f"El archivo {data["topic"]}.json, con clasificaciones de ejercicios, no existe.")

    st.subheader(f"Tema: {data["topic"].title()}")

    col1, col2 = st.columns(2)
    
    with col1:
        
        selected_exercise = st.selectbox(
            label = "Examen:",
            options= [ex[0] + " - " + ex[1] for ex in data["exercises"] ]
        )

        if selected_exercise:
            exam, exercise = selected_exercise.split(" - ")

    with col2:
        if exercise_types:
            ex_type = st.selectbox(
                label = "Tipo de ejercicio",
                options = exercise_types[data["topic"]]
            )
    
    current_exercise = {
        "asignatura" : data["subject"],
        "tema" : data["topic"],
        "año" :data["year"],
        "convocatoria" : exam,
        "ejercicio" : exercise,
        "tipo_ejercicio" : ex_type
        }
    df = pd.DataFrame([current_exercise])
    
    st.dataframe(df.T, use_container_width=True)
    