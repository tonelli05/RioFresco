import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- CONFIGURAÇÕES BÁSICAS ---
st.set_page_config(page_title="RioFresco Intelligence", page_icon="📈", layout="wide")

# --- CAMINHOS ---
BASE_DIR = Path(__file__).parent.resolve()
DADOS = BASE_DIR / "RioFresco-main" / "dados"
ARQUIVO_CLIMA = "clima_otimizado.csv"
ARQUIVO_JSON = "ranking_vulnerabilidade.json"

# --- ESTILO CSS PERSONALIZADO (DARK MODE CORPORATIVO) ---
st.markdown("""
    <style>
    /* Reset e Fundo */
    .stApp { 
        background-color: #0E1117; 
        color: #E0E6ED;
    }
    
    /* Tipografia e Cabeçalhos */
    h1, h2, h3 { 
        color: #1abc9c !important; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Métricas e Cartões */
    div[data-testid="metric-container"] {
        background-color: #1F2937;
        border: 1px solid #374151;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="metric-container"] label {
        color: #9CA3AF !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #10B981 !important;
        font-size: 1.8rem;
    }
    
    /* Tabelas e Dataframes */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    
    /* Esconder footer do Streamlit */
    footer { visibility: hidden; }
    
    /* Botões e Sliders */
    .stSlider > div > div > div > div { background-color: #1abc9c !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO DE DADOS COM CACHE ---
@st.cache_data
def carregar_dados_clima():
    csv_path = DADOS / ARQUIVO_CLIMA
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.DataFrame()

@st.cache_data
def carregar_dados_vulnerabilidade():
    json_path = DADOS / ARQUIVO_JSON
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return pd.DataFrame()

df_clima = carregar_dados_clima()
df_vuln = carregar_dados_vulnerabilidade()

# --- SIDEBAR: ARQUITETURA TÉCNICA ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Bras%C3%A3o_da_cidade_do_Rio_de_Janeiro.svg/1200px-Bras%C3%A3o_da_cidade_do_Rio_de_Janeiro.svg.png", width=100)
    st.title("RioFresco Eng.")
    st.caption("Arquitetura e Pipeline de Dados")
    
    with st.expander("1. Coleta (Bronze)", expanded=False):
        st.write("Extração via Open-Meteo Archive. Sistema resiliente com Exponential Backoff (429) e suporte a >160 bairros.")
    with st.expander("2. Processamento (Silver)", expanded=False):
        st.write("EDA robusta: Normalização de clima, tratamento DataSUS (Latin1) e cálculo de área via SIRGAS 2000.")
    with st.expander("3. Machine Learning (Gold)", expanded=False):
        st.write("Clusterização K-Means (Geração do IVT) e PCA para redução de dimensionalidade.")
        
    st.divider()
    st.markdown("**Versão:** 2.0.0")
    st.markdown("**Status:** Produção")

# --- CONTEÚDO PRINCIPAL ---

st.title("RioFresco: Inteligência Climática Urbana")
st.markdown("Painel executivo para tomada de decisão e análise de resiliência térmica nos bairros do Rio de Janeiro.")

# --- 1. KPIs DE IMPACTO ---
st.subheader("Métricas Globais da Cidade")
if not df_vuln.empty and not df_clima.empty:
    media_verde = df_vuln['percentual_verde'].mean()
    max_temp = df_clima['temp_max_abs'].max()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Média de Cobertura Vegetal", value=f"{media_verde:.1f}%", delta="- Risco Urbano")
    with col2:
        st.metric(label="Pico Histórico de Calor", value=f"{max_temp:.1f} °C", delta="Alerta", delta_color="inverse")
    with col3:
        st.metric(
            label="Correlação: Calor x Intern.", 
            value="R² = 5%", 
            delta="Impacto Multivariado",
            help="**O que isso significa?**\nApenas 5% das internações são explicadas diretamente pelo aumento bruto da temperatura. O modelo de Inteligência Artificial revelou que **a altitude, a proximidade com o mar e a ausência de áreas verdes** são fatores que agravam ou mitigam o problema de saúde de forma muito mais drástica."
        )
    with col4:
        bairros_alerta = df_vuln[df_vuln['categoria_climatica'] == 'Emergência Térmica']['bairro'].tolist()
        lista_bairros = "\n".join([f"- {b}" for b in sorted(bairros_alerta)])
        st.metric(
            label="Bairros em Emergência", 
            value=len(bairros_alerta), 
            delta="Atenção Prioritária", 
            delta_color="inverse",
            help=f"**Lista de Bairros em Nível Crítico:**\n\n{lista_bairros}"
        )
else:
    st.warning("Bancos de dados não encontrados ou vazios.")

st.divider()

# --- 2. MAPA INTERATIVO E PCA ---
st.subheader("Distribuição do Índice de Vulnerabilidade Térmica (IVT)")

if not df_vuln.empty:
    tab1, tab2 = st.tabs(["🌎 Mapa de Calor e Vulnerabilidade", "📊 Análise de Componentes Principais (PCA)"])
    
    color_discrete_map = {
        "Emergência Térmica": "#EF4444",  # Vermelho
        "Vulnerabilidade Urbana": "#F59E0B",  # Amarelo/Laranja
        "Zonas de Resiliência": "#10B981"  # Verde
    }
    
    with tab1:
        st.markdown("**Tamanho da Bolha:** % de Área Verde | **Cor:** Perfil de Risco")
        
        # --- FIX: Evita KeyError no groupby do Plotly x Pandas ---
        # Remove linhas com valores nulos nas colunas utilizadas e garante o tipo string
        df_clean = df_vuln.dropna(subset=["lat", "lon", "categoria_climatica", "percentual_verde", "IVT", "temp_max_media"]).copy()
        df_clean["categoria_climatica"] = df_clean["categoria_climatica"].astype(str)

        fig_map = px.scatter_mapbox(
            df_clean, lat="lat", lon="lon", color="categoria_climatica", 
            size="percentual_verde", hover_name="bairro", hover_data=["IVT", "temp_max_media"],
            color_discrete_map=color_discrete_map,
            zoom=10, mapbox_style="carto-darkmatter", height=500
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map, use_container_width=True)

    with tab2:
        st.markdown("**Gráfico de Dispersão dos Clusters (K-Means)**")
        fig_pca = px.scatter(
            df_vuln, x="PC1", y="PC2", color="categoria_climatica",
            hover_name="bairro", size="percentual_verde",
            color_discrete_map=color_discrete_map,
            title="Separação de Clusters (Redução de Dimensionalidade)",
            height=500
        )
        fig_pca.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E0E6ED'))
        st.plotly_chart(fig_pca, use_container_width=True)

st.divider()

# --- 3. SIMULADOR DE CENÁRIOS ---
st.subheader("🌱 Simulador de Resiliência Térmica")
st.markdown("Utilize o controle deslizante abaixo para simular políticas públicas de arborização urbana e observar o impacto teórico nas temperaturas médias locais.")

# Assumindo um coeficiente didático de redução (-0.08°C para cada 1% de aumento na vegetação)
COEFICIENTE_REDUCAO = -0.08 

aumento_verde = st.slider("Simular Aumento Percentual de Cobertura Vegetal (%)", min_value=0, max_value=25, value=0, step=1)

if aumento_verde > 0 and not df_vuln.empty:
    reducao_estimada = aumento_verde * COEFICIENTE_REDUCAO
    
    colA, colB = st.columns([1, 2])
    with colA:
        st.info(f"**Impacto Estimado:**\n\nRedução de **{abs(reducao_estimada):.2f} °C** nas máximas locais.")
    
    with colB:
        df_simulacao = df_vuln[['bairro', 'percentual_verde', 'temp_max_media', 'categoria_climatica']].copy()
        df_simulacao['Nova Temp. Max'] = df_simulacao['temp_max_media'] + reducao_estimada
        
        # Filtrar o Top 5 Bairros mais quentes para mostrar o impacto
        st.write("Top 5 Bairros Críticos (Projeção)")
        st.dataframe(df_simulacao.sort_values(by='temp_max_media', ascending=False).head(5), use_container_width=True)

st.divider()

# --- 4. DATASET CLIMÁTICO CONSOLIDADO ---
st.subheader("📚 Base de Dados Climática (Silver Tier)")
if not df_clima.empty:
    st.markdown("Explore os dados históricos consolidados. Clique nos cabeçalhos para ordenar (ex: identifique meses com maior `temp_max_abs`).")
    
    # Criar filtros interativos simples
    anos_disponiveis = df_clima['ano'].unique()
    ano_selecionado = st.selectbox("Filtrar por Ano", options=["Todos"] + list(anos_disponiveis))
    
    df_exibicao = df_clima if ano_selecionado == "Todos" else df_clima[df_clima['ano'] == ano_selecionado]
    
    st.dataframe(
        df_exibicao,
        use_container_width=True, height=300
    )

# --- 5. RODAPÉ ---
st.markdown("""
<div style='background-color: #1F2937; padding: 15px; border-radius: 8px; border: 1px solid #374151; text-align: center; margin-top: 30px;'>
    <h5 style='color: #1abc9c; margin-bottom: 8px; font-family: sans-serif; letter-spacing: 0.5px;'>Equipe Técnica</h5>
    <p style='color: #9CA3AF; font-size: 14px; margin: 0;'>
        <span style='color: #E0E6ED;'>Lucas de Moraes Brandão</span> &nbsp;|&nbsp; 
        <span style='color: #E0E6ED;'>Pedro Tonelli da Cunha</span> &nbsp;|&nbsp; 
        <span style='color: #E0E6ED;'>Isac Freire</span> &nbsp;|&nbsp; 
        <span style='color: #E0E6ED;'>Nargylla Fernanda Cloviel Lima</span>
    </p>
</div>
""", unsafe_allow_html=True)