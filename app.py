
import streamlit as st
import pandas as pd

st.set_page_config(page_title="AirBnB Madrid", layout="wide")

col_titulo = st.columns([1, 2, 1])
with col_titulo[1]:
    st.title("AirBnB")
    st.subheader("Alvaro Fraile")
# le he pedido ayuda a clude para meter el data set    
@st.cache_data
def load_data():
    df = pd.read_csv("airbnb (3).csv", sep=",", on_bad_lines="skip")
    df.columns = [c.strip().replace(";", "") for c in df.columns]
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["reviews_per_month"] = pd.to_numeric(df["reviews_per_month"], errors="coerce")
    df["number_of_reviews"] = pd.to_numeric(df["number_of_reviews"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["price"])
    df = df[df["price"] > 0]
    return df

df = load_data()

# Aqui lo que hacemos es que cojo y creo un filtro para las tres ventanas hago uno de los distritos y otro para el precio con un rango 
st.sidebar.header("Filtros_Global")
Barrio = ["Todos"] + sorted(df["neighbourhood_group"].dropna().unique().tolist())
Barrio_elegir = st.sidebar.selectbox("Elige tu barrio", Barrio)
min_p = int(df["price"].min())
max_p = int(df["price"].quantile(0.95))
precio_rango = st.sidebar.slider("Elige tu precio", min_p, max_p, (min_p, max_p))

df_filtrado = df.copy()
if Barrio_elegir != "Todos": 
    df_filtrado = df_filtrado[df_filtrado["neighbourhood_group"] == Barrio_elegir]
    
df_filtrado = df_filtrado[(df_filtrado["price"] >= precio_rango[0]) & (df_filtrado["price"] <= precio_rango[1])]
st.sidebar.markdown(f"Pisos disponibles : {len(df_filtrado):,}")

tab1, tab2, tab3 = st.tabs(["Por Vecindario", "Tipos de Alojamiento", "Reseñas"])

#-------------------------------------------------------------------- por vecindario ------------------------------------------------------------------------------------
with tab1:
    st.markdown("POR VECINDARIO")

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Precio medio", value=f"{df_filtrado['price'].mean():.0f} €")
    col2.metric(label="N_casas", value=f"{len(df_filtrado):,}")
    col3.metric(label="Media_reseñas", value=f"{df_filtrado['reviews_per_month'].mean():.2f}")

    st.markdown("Mapas_Casas")
    df_map = df_filtrado.dropna(subset=["latitude", "longitude"])[["latitude", "longitude"]]
    st.map(df_map, zoom=12, size=10)

# ------------------------------------------------------------------- Estilo de casa -----------------------------------------------------------------------------------------
with tab2:
    st.markdown("TIPOS DE CASA")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("Numero de opciones por tip")
        conteo = df_filtrado["room_type"].value_counts().reset_index()
        conteo.columns = ["Tipo", "Cantidad"]
        st.bar_chart(conteo.set_index("Tipo"))

    with col_b:
        st.markdown("Precio medio por tipo")
        precio_tipo = (df_filtrado.groupby("room_type")["price"].mean().reset_index().rename(columns={"room_type": "Tipo", "price": "Precio medio (€)"}))
        precio_tipo["Precio medio (€)"] = precio_tipo["Precio medio (€)"].round(2)
        st.bar_chart(precio_tipo.set_index("Tipo"))

# -------------------------------------------------------------------------- reseñas -----------------------------------------------------------------------------------------
with tab3:
    st.markdown("RESEÑAS")
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("Top 10 Barrios")
        top_barrios = (
            df_filtrado.groupby("neighbourhood")["reviews_per_month"].mean().dropna().sort_values(ascending=False).head(10).reset_index().rename(columns={"neighbourhood": "Barrio", "reviews_per_month": "Media reviews/mes"}))
        st.bar_chart(top_barrios.set_index("Barrio"))

    with col_d:
        st.markdown("Por tipo de casa")
        resena_tipo = (
            df_filtrado.groupby("room_type")["number_of_reviews"].sum().reset_index().rename(columns={"room_type": "Tipo", "number_of_reviews": "Total reviews"})
        )
        st.bar_chart(resena_tipo.set_index("Tipo"))
