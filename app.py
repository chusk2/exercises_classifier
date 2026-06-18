import streamlit as st
from pypdf import PdfReader
import json
import pandas as pd
import sqlite3
from pyuca import Collator


st.set_page_config(layout = "wide", page_title = "Exam Classifier")
st.title("Exam Classifier")

with open("exercise_types.json", mode = "r", encoding = "utf-8") as file:
    exercise_types_dict = json.load(file)

# create connection to database
conn = sqlite3.connect("database.db")

# get the dataframe from all available data in db
df = pd.read_sql("select * from ejercicios ;", conn)


col1, col2 = st.columns(2)
    
with col1:
    
    # select subject
    collator = Collator()
    subjects = sorted( list(df.asignatura.unique()), key=collator.sort_key )

    selected_subject = st.selectbox(
        label = "Asignatura:",
        options= subjects
    )

    # select topic based on selected subject
    if selected_subject:
        topics = df.loc[df.asignatura == selected_subject, "tema"].unique()
        topics = sorted(list(topics), key=collator.sort_key)

    selected_topic = st.selectbox(
        label = "Tema:",
        options= topics
    )

    # select year based on selected subject and topic
    if selected_topic and selected_subject:
        mask = (df.asignatura == selected_subject) & (df.tema == selected_topic) 
        years = df.loc[mask, "año"].unique()
        years = sorted(list(years))

        selected_year = st.selectbox(
            label = "Año:",
            options= years
        )


mask = (df.asignatura == selected_subject) & \
(df.tema == selected_topic) & \
(df.año == selected_year)

exercises_df = df[mask].copy()
exercises_df["combined_ex"] = (exercises_df
                                .apply(lambda row: row.loc["convocatoria"] + " - " +
                                        row.loc["ejercicio"], axis=1)
)

selected_exercise = st.selectbox(
        label = "Ejercicio:",
        options= list(exercises_df.combined_ex)
    )

available_exercise_types = exercise_types_dict.get(selected_topic)
selected_exercise_type = None
exercise_type = None

if available_exercise_types:
    selected_exercise_type = st.selectbox(
            label = "Tipo de ejercicio:",
            options= available_exercise_types
        )

new_exercise_type = st.text_input(label = "Nuevo tipo de ejercicio",
                                  value="",
                                  max_chars=100,
                                  placeholder="Inserta nuevo tipo de ejercicio...",
                                  type="default"
)


if new_exercise_type:
    exercise_type = new_exercise_type
elif selected_exercise_type:
    exercise_type = selected_exercise_type

convocatoria, ejercicio = selected_exercise.split(" - ")

data = {
    "asignatura" : selected_subject,
    "tema" : selected_topic,
    "año" : selected_year,
    "convocatoria" : convocatoria,
    "ejercicio" : ejercicio,
    # if a new exercise type is provided
    "tipo_ejercicio" : exercise_type
}

if st.button("Guardar datos"):
    data_df = pd.DataFrame([data])
    data_df.to_sql("ejercicios", conn, if_exists="append", index = False)
    conn.commit()
    saved_data_string = ""
    for key, value in data.items():
        saved_data_string += f"**{key}**: *{value}*  \n" 

    st.success(f"### Datos guardados:  \n{saved_data_string}")


st.dataframe(exercises_df, hide_index = True, use_container_width=True)