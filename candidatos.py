import streamlit as st
import json
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Documentos", layout="wide")

# Constantes
TIPO_DOC = ['BO', 'DJ', 'D1', 'D2', 'D3']
MAX_DOCS = 5
COLUMNAS_ELIMINAR = ['codigo_hojavida', 'porcentaje_avance', 'porcentaje_avance_ddjj', 'numero', 'Fecha', 'Hora', 'estado']
COLUMNAS_PRIMERAS = ["DNI", "nombre_completo", "circunscripcion", "tipo_eleccion", "cargo_eleccion", "foto", "hv"]

# Barra de búsqueda
search = st.text_input(
    "Buscar por nombre o DNI o circunscripcion",
    placeholder="Escriba un nombre o DNI o circunscripcion"
)

@st.cache_data
def cargar_datos():
    with open('data_final.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def crear_tabla_con_documentos(data):
    filas = []
    for item in data:
        fila = {key: value for key, value in item.items() if key != 'docs'}
        docs = item.get('docs', [])
        for i in range(MAX_DOCS):
            fila[TIPO_DOC[i]] = docs[i].get('rutaArchivo', '') if i < len(docs) else ''
        filas.append(fila)
    return pd.DataFrame(filas)

def procesar_usuario(valor):
    if isinstance(valor, str) and valor:
        palabras = valor.split()
        if 'ana' in valor.lower():
            return palabras[1] if len(palabras) > 1 else valor
        return palabras[0] if palabras else valor
    return valor

# Main
data = cargar_datos()
df = crear_tabla_con_documentos(data)

# Renombrar y limpiar
df = df.rename(columns={
    'documento_identidad': 'DNI',
    'fecha_confirmacion': 'Fecha',
    'hora_confirmacion': 'Hora',
    'url_foto': 'foto',
    'url_hv': 'hv'
})

df["fecha_hora"] = df["Fecha"].astype(str) + " " + df["Hora"].astype(str)
df = df.drop(columns=COLUMNAS_ELIMINAR)

# Procesar usuario
if 'usuario_confirma' in df.columns:
    df['usuario_confirma'] = df['usuario_confirma'].apply(procesar_usuario)

# Configurar columnas
column_config = {
    'usuario_confirma': st.column_config.TextColumn('Confirmo', width=50),
    'DNI': st.column_config.TextColumn('DNI', width=65),
    'foto': st.column_config.ImageColumn("img", width=30),
    'hv': st.column_config.LinkColumn('hv', width=30, display_text="📄"),
    'fecha_hora': st.column_config.DatetimeColumn('Fecha hora', format="DD/MM/YY HH:mm:ss"),
}

# Configurar documentos
for col in df.columns:
    if col in TIPO_DOC:
        column_config[col] = st.column_config.LinkColumn(col, width=28, display_text="📄")

# Reordenar columnas
df = df[COLUMNAS_PRIMERAS + [c for c in df.columns if c not in COLUMNAS_PRIMERAS]]

# Filtrar
df_filtrado = df
if search:
    texto = search.strip().lower()
    mask = (
        df["nombre_completo"].astype(str).str.lower().str.contains(texto, na=False) |
        df["DNI"].astype(str).str.contains(texto, na=False) |
        df["circunscripcion"].astype(str).str.lower().str.contains(texto, na=False)
    )
    df_filtrado = df[mask]

# Mostrar tabla
st.dataframe(
    df_filtrado,
    column_config=column_config,
    hide_index=True,
    row_height=24,
    width="content",
    height=min(len(df) * 35 + 40, 800),
    selection_mode="multi-cell",
    on_select="ignore",
)

# JavaScript para focus en input
st.iframe(
    """
    <script>
    const focusInput = () => {
        const inputs = parent.document.querySelectorAll('.stTextInput input');
        if (inputs.length > 0) {
            inputs[0].focus();
            inputs[0].select();
        } else {
            setTimeout(focusInput, 100);
        }
    };
    focusInput();
    </script>
    """,
    height=1
)