import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
import folium
from streamlit_folium import st_folium
from sklearn.cluster import KMeans

st.set_page_config(page_title="Roteiro Otimizado", layout="wide")

# 🔐 Tela de login
def login():
    st.title("🔐 Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if username == "Se@RJ" and password == "Se@RJ1":
            st.session_state["autenticado"] = True
        else:
            st.error("Usuário ou senha incorretos.")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    login()
    st.stop()

# ✅ A partir daqui, o app original é carregado
# CSS personalizado para responsividade
st.markdown("""
    <style>
        div[data-testid="stHeadingWithActionElements"] {
            font-size: 1em;
        }      
        @media (max-width: 600px) {
            div[data-testid="stHeadingWithActionElements"] {
                font-size: 1.1em;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 📄 Carregar os dados
uploaded_file = st.file_uploader("📁 Envie a base de dados (.xlsx)", type=["xlsx"])
if uploaded_file is None:
    st.warning("Por favor, envie o arquivo 'base_joinvile_tratada.xlsx' para continuar.")
    st.stop()

df = pd.read_excel(uploaded_file)
df = df.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
df = df.dropna(subset=['latitude', 'longitude']).copy()
df['latitude'] = df['latitude'].astype(str).str.replace(",", ".", regex=False).astype(float)
df['longitude'] = df['longitude'].astype(str).str.replace(",", ".", regex=False).astype(float)

endereco_col = [col for col in df.columns if 'Endereco' in col][0]

# 🧭 Sidebar: seleção dinâmica por endereço
st.sidebar.markdown("### Endereços no mapa")

if "enderecos_selecionados" not in st.session_state:
    st.session_state.enderecos_selecionados = df[endereco_col].tolist()

col1, col2 = st.sidebar.columns(2)
if col1.button("Selecionar todos os endereços"):
    st.session_state.enderecos_selecionados = df[endereco_col].tolist()
if col2.button("Limpar endereços"):
    st.session_state.enderecos_selecionados = []

enderecos_selecionados = st.sidebar.multiselect(
    "Selecione os endereços:",
    options=df[endereco_col].tolist(),
    default=st.session_state.enderecos_selecionados
)
st.session_state.enderecos_selecionados = enderecos_selecionados

# 🎨 Filtro por cor
st.sidebar.markdown("### Filtrar por cor")
cores_disponiveis = ["green", "blue", "orange", "red"]

if "cores_selecionadas" not in st.session_state:
    st.session_state.cores_selecionadas = cores_disponiveis

col3, col4 = st.sidebar.columns(2)
if col3.button("Selecionar todas as cores"):
    st.session_state.cores_selecionadas = cores_disponiveis
if col4.button("Limpar cores"):
    st.session_state.cores_selecionadas = []

cores_selecionadas = st.sidebar.multiselect(
    "Selecione as cores:",
    options=cores_disponiveis,
    default=st.session_state.cores_selecionadas
)
st.session_state.cores_selecionadas = cores_selecionadas

# 🔍 Filtrar pontos selecionados
df_selecionado = df[df[endereco_col].isin(enderecos_selecionados)].copy()
df_selecionado.reset_index(drop=True, inplace=True)

# 📐 Criar matriz de distâncias
def create_distance_matrix(df):
    df = df.reset_index(drop=True)
    num_points = len(df)
    matrix = np.zeros((num_points, num_points))
    for i in range(num_points):
        for j in range(num_points):
            if i != j:
                coord_i = (df.loc[i, 'latitude'], df.loc[i, 'longitude'])
                coord_j = (df.loc[j, 'latitude'], df.loc[j, 'longitude'])
                matrix[i][j] = geodesic(coord_i, coord_j).meters
    return matrix

# 🔄 Resolver TSP com OR-Tools
if not df_selecionado.empty:
    distance_matrix = create_distance_matrix(df_selecionado)
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    rota_otimizada = []
    if solution:
        index = routing.Start(0)
        while not routing.IsEnd(index):
            rota_otimizada.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))

        df_final = df_selecionado.loc[rota_otimizada].reset_index(drop=True)
        df_final['ordem_visita'] = df_final.index + 1
    else:
        st.error("Não foi possível resolver o problema de roteamento.")
        df_final = df_selecionado.copy()
        df_final['ordem_visita'] = None
else:
    df_final = df_selecionado.copy()
    df_final['ordem_visita'] = None

# 📍 Centralizar no ponto de ordem 10, se existir
if not df_final.empty and 10 in df_final['ordem_visita'].values:
    ponto_10 = df_final[df_final['ordem_visita'] == 10].iloc[0]
    centro_lat, centro_lon = ponto_10['latitude'], ponto_10['longitude']
elif not df_final.empty:
    centro_lat = df_final['latitude'].mean()
    centro_lon = df_final['longitude'].mean()
else:
    centro_lat, centro_lon = -26.3044, -48.8456  # fallback

# 🟢 Função para definir cor
def definir_cor(valor):
    if valor >= 15000:
        return 'green'
    elif 5000 <= valor < 15000:
        return 'blue'
    elif 0 < valor < 5000:
        return 'orange'
    else:
        return 'red'

# 🗺️ Mapa interativo
st.subheader("🗺️ Mapa interativo da seleção:")
m = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)

for idx, row in df_final.iterrows():
    cor = definir_cor(row['Maior Compra'])
    if cor in cores_selecionadas:
        popup_text = f"""
        <b>Ordem:</b> {row['ordem_visita']}<br>
        <b>Endereço:</b> {row[endereco_col]}<br>
        <b>Índice:</b> {idx}<br>
        <b>Maior Compra:</b> R$ {row['Maior Compra']:,.2f}
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            tooltip=f"{row['ordem_visita']} - {row[endereco_col]}",
            icon=folium.Icon(color=cor)
        ).add_to(m)

st_folium(m, width="100%", height=600)

# 📊 Tabela
st.subheader("📌 Ordem de visitação otimizada:")
st.dataframe(df_final[[endereco_col, 'N Fantasia  ', 'Maior Compra']])
