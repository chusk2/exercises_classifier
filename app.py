import streamlit as st
from pypdf import PdfReader
import json
import pandas as pd
import sqlite3
from pyuca import Collator


st.set_page_config(layout = "centered", page_title = "Exam Classifier")
st.title("Exam Classifier")

with open("topics.json", mode = "r", encoding = "utf-8") as file:
    topics_dict = json.load(file)

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


st.dataframe(exercises_df)