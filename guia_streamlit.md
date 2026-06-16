# 🧩 Guía de sintaxis Streamlit

Referencia rápida para los componentes más usados en una app Streamlit: dropdown, file upload, dataframe, radio buttons y conexión a SQLite3.

---

## 📦 Instalación y estructura básica

```bash
pip install streamlit
streamlit run app.py
```

```python
import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Mi App", layout="wide")
st.title("Mi aplicación Streamlit")
```

---

## 1. Dropdown (Selectbox)

```python
# Dropdown simple
opcion = st.selectbox(
    label="Elige una opción:",
    options=["Opción A", "Opción B", "Opción C"]
)

st.write(f"Seleccionaste: **{opcion}**")
```

```python
# Dropdown con índice por defecto y opciones desde lista/variable
categorias = ["Química", "Física", "Matemáticas"]

categoria = st.selectbox(
    label="Asignatura:",
    options=categorias,
    index=0,            # índice de la opción por defecto
    help="Elige la asignatura del ejercicio"
)
```

```python
# Multiselect (selección múltiple)
seleccion = st.multiselect(
    label="Elige varios temas:",
    options=["Termodinámica", "Cinética", "Equilibrio", "Ácido-base"],
    default=["Termodinámica"]
)
```

---

## 2. File Upload

```python
# Subir un único archivo
archivo = st.file_uploader(
    label="Sube un archivo CSV:",
    type=["csv"]            # lista de extensiones permitidas
)

if archivo is not None:
    df = pd.read_csv(archivo)
    st.success(f"Archivo cargado: {archivo.name}")
```

```python
# Subir múltiples archivos
archivos = st.file_uploader(
    label="Sube uno o varios archivos:",
    type=["csv", "xlsx", "pdf"],
    accept_multiple_files=True
)

for archivo in archivos:
    st.write(f"📄 {archivo.name} — {archivo.size} bytes")
```

```python
# Leer Excel subido
archivo_excel = st.file_uploader("Sube un Excel:", type=["xlsx"])

if archivo_excel:
    df = pd.read_excel(archivo_excel, sheet_name=0)
```

---

## 3. Mostrar un DataFrame

```python
# Tabla interactiva (recomendada — permite ordenar y filtrar)
st.dataframe(df)

# Con opciones de tamaño
st.dataframe(df, height=300, use_container_width=True)
```

```python
# Tabla estática (sin interactividad)
st.table(df)
```

```python
# Mostrar solo algunas columnas
st.dataframe(df[["columna1", "columna2"]])
```

```python
# Con métricas rápidas encima
col1, col2, col3 = st.columns(3)
col1.metric("Filas", df.shape[0])
col2.metric("Columnas", df.shape[1])
col3.metric("Nulos", df.isnull().sum().sum())

st.dataframe(df, use_container_width=True)
```

```python
# Estilo condicional (resaltar valores)
st.dataframe(
    df.style.highlight_max(axis=0, color="lightgreen")
)
```

---

## 4. Radio Button

```python
# Radio básico
modo = st.radio(
    label="Elige el modo:",
    options=["Ver datos", "Editar", "Exportar"]
)

st.write(f"Modo activo: {modo}")
```

```python
# Radio horizontal
orientacion = st.radio(
    label="Disposición:",
    options=["Vertical", "Horizontal"],
    horizontal=True         # disponible desde Streamlit 1.18+
)
```

```python
# Usar el radio para controlar qué se muestra
accion = st.radio("¿Qué quieres hacer?", ["Ver tabla", "Ver gráfico"])

if accion == "Ver tabla":
    st.dataframe(df)
elif accion == "Ver gráfico":
    st.line_chart(df)
```

---

## 5. Enviar datos a SQLite3

### Conexión básica

```python
import sqlite3

def get_connection():
    conn = sqlite3.connect("datos.db")   # crea el archivo si no existe
    return conn
```

### Crear tabla si no existe

```python
def crear_tabla():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT,
            categoria TEXT,
            valor     REAL,
            fecha     TEXT
        )
    """)
    conn.commit()
    conn.close()

crear_tabla()
```

### Insertar una fila desde el formulario

```python
nombre    = st.text_input("Nombre:")
categoria = st.selectbox("Categoría:", ["A", "B", "C"])
valor     = st.number_input("Valor:", min_value=0.0)

if st.button("💾 Guardar en base de datos"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO registros (nombre, categoria, valor, fecha) VALUES (?, ?, ?, DATE('now'))",
        (nombre, categoria, valor)
    )
    conn.commit()
    conn.close()
    st.success("✅ Registro guardado correctamente.")
```

> **Usa siempre `?` como placeholder** — nunca f-strings en SQL, para evitar inyección.

### Insertar un DataFrame entero

```python
if st.button("📤 Subir CSV a la base de datos"):
    if archivo is not None:
        df = pd.read_csv(archivo)
        conn = get_connection()
        df.to_sql(
            name="registros",
            con=conn,
            if_exists="append",    # "replace" para sobreescribir
            index=False
        )
        conn.close()
        st.success(f"✅ {len(df)} filas insertadas.")
```

### Leer datos de vuelta y mostrarlos

```python
def cargar_datos():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM registros", conn)
    conn.close()
    return df

if st.button("🔄 Recargar datos"):
    df_bd = cargar_datos()
    st.dataframe(df_bd, use_container_width=True)
```

---

## 6. Ejemplo completo integrado

```python
import streamlit as st
import pandas as pd
import sqlite3

# ---------- Config ----------
st.set_page_config(page_title="Demo Streamlit + SQLite", layout="wide")
st.title("📊 Demo: Streamlit + SQLite3")

DB = "demo.db"

def get_conn():
    return sqlite3.connect(DB)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                fuente    TEXT,
                categoria TEXT,
                filas     INTEGER
            )
        """)

init_db()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Configuración")
    categoria = st.selectbox("Categoría:", ["Ventas", "RRHH", "Operaciones"])
    modo      = st.radio("Vista:", ["Tabla", "Resumen"], horizontal=True)

# ---------- Upload ----------
archivo = st.file_uploader("Sube un CSV:", type=["csv"])

if archivo:
    df = pd.read_csv(archivo)

    if modo == "Tabla":
        st.dataframe(df, use_container_width=True)
    else:
        st.write(df.describe())

    if st.button("💾 Guardar metadatos en SQLite"):
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO datos (fuente, categoria, filas) VALUES (?, ?, ?)",
                (archivo.name, categoria, len(df))
            )
        st.success("Metadatos guardados.")

# ---------- Ver BD ----------
st.divider()
st.subheader("📁 Registros en la base de datos")

with get_conn() as conn:
    df_bd = pd.read_sql("SELECT * FROM datos", conn)

st.dataframe(df_bd, use_container_width=True)
```

---

## 📝 Referencia rápida de widgets

| Widget | Función | Retorna |
|---|---|---|
| Dropdown | `st.selectbox()` | valor seleccionado |
| Multi-select | `st.multiselect()` | lista de valores |
| Radio | `st.radio()` | valor seleccionado |
| File upload | `st.file_uploader()` | objeto archivo / lista |
| Tabla interactiva | `st.dataframe()` | — |
| Tabla estática | `st.table()` | — |
| Botón | `st.button()` | `True` / `False` |
| Input texto | `st.text_input()` | string |
| Input número | `st.number_input()` | int / float |

---

*Streamlit docs: https://docs.streamlit.io*
