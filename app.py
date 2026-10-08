import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Configuración de Credenciales
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def fetch_notion_data():
    """Conecta a la API de Notion y extrae las métricas virales"""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    data = response.json()
    
    records = []
    for page in data.get("results", []):
        props = page["properties"]
        
        try:
            # Extraer Título del video
            title_list = props.get("Name", {}).get("title", [])
            name = title_list[0]["plain_text"] if title_list else "Sin Título"
            
            # Extraer Métricas Puras (fallback a 0 si la celda está vacía)
            views = props.get("Views", {}).get("number") or 0
            likes = props.get("Likes", {}).get("number") or 0
            saved = props.get("Saved", {}).get("number") or 0
            
            # Extraer Fórmula de Engagement
            formula_data = props.get("Fuego 🔥 (Engagement)", {}).get("formula", {})
            engagement = formula_data.get("number") or 0
            
            records.append({
                "Video": name,
                "Vistas": views,
                "Likes": likes,
                "Guardados": saved,
                "Engagement (%)": engagement * 100 # Escalar porcentaje
            })
        except Exception as e:
            continue
            
    return pd.DataFrame(records)

# 2. Configuración Visual del Dashboard
st.set_page_config(page_title="Dannie Moons Analytics", layout="wide")
st.title("📈 Laboratorio de Ingeniería Viral")

df = fetch_notion_data()

# 3. Generación del Gráfico
if not df.empty:
    # Gráfico de Dispersión: Compara Vistas vs Engagement.
    # El tamaño del círculo representa los Likes y el color los Guardados.
    fig = px.scatter(
        df, 
        x="Vistas", 
        y="Engagement (%)", 
        size="Likes",
        color="Guardados",
        hover_name="Video",
        template="plotly_dark",
        title="Impacto del Algoritmo: Vistas vs Retención"
    )
    
    # Ocultar fondo transparente para que encaje estéticamente con Notion Modo Oscuro
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No se encontraron datos. Verifica que tu Autopsia Viral tenga filas con números y que el bot tenga acceso.")
