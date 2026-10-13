import streamlit as st
import requests
import pandas as pd
import plotly.express as px

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

st.set_page_config(page_title="Modo Diagnóstico", layout="wide")
st.title("🛠️ Diagnóstico de Conexión a Notion")

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
response = requests.post(url, headers=headers)

if response.status_code != 200:
    st.error(f"🚨 Error de conexión (Código HTTP: {response.status_code})")
    st.write("El servidor de Notion respondió esto (Revisa tus Tokens y Database ID):")
    st.json(response.json())
else:
    data = response.json()
    if not data.get("results"):
        st.warning("⚠️ Conexión exitosa, pero Notion dice que la tabla está vacía.")
        st.info("Causa más probable: El bot 'Dannie Moons Analytics' no está conectado a esta base de datos específica a través de las Conexiones de la página.")
    else:
        st.success(f"✅ ¡Se encontraron {len(data['results'])} filas! Procesando datos...")
        
        records = []
        for i, page in enumerate(data.get("results", [])):
            props = page["properties"]
            try:
                title_list = props.get("Name", {}).get("title", [])
                name = title_list[0]["plain_text"] if title_list else f"Sin título {i}"
                
                views = props.get("Views", {}).get("number") or 0
                likes = props.get("Likes", {}).get("number") or 0
                saved = props.get("Saved", {}).get("number") or 0
                
                formula_data = props.get("Engagement", {}).get("formula", {})
                engagement = formula_data.get("number") or 0
                
                records.append({
                    "Video": name,
                    "Vistas": views,
                    "Likes": likes,
                    "Guardados": saved,
                    "Engagement (%)": engagement * 100
                })
            except Exception as e:
                st.error(f"❌ Error al procesar la propiedad en una fila: {e}")
                st.write("Estructura de los datos que causaron el error:")
                st.json(props)
        
        df = pd.DataFrame(records)
        
        if not df.empty:
            fig = px.scatter(df, x="Vistas", y="Engagement (%)", size="Likes", color="Guardados", hover_name="Video", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)
