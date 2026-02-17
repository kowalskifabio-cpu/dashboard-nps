import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px

# 1. Configurações e Estilo Escrita Contabilidade
st.set_page_config(page_title="Dashboard NPS - Escrita", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F4F6F8; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #DEE2E6; }
    .metric-card {
        background-color: #FFF3E0; /* Tom pastel suave para os cards */
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #FFE0B2;
    }
</style>
""", unsafe_allow_html=True)

# 2. Conexão com Dados
def load_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(st.secrets["SHEET_ID"])
        worksheet = sh.worksheet("respostas")
        df = pd.DataFrame(worksheet.get_all_records())
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# 3. Barra Lateral (Filtros Estratégicos conforme imagem)
with st.sidebar:
    st.image("Logo Escrita.png", width=180)
    st.markdown("### Filtros Estratégicos")
    
    if not df.empty:
        # Filtro de Empresa/Cliente
        clientes = ["Todas"] + sorted(df['cliente'].unique().tolist())
        filtro_cliente = st.selectbox("Empresa", clientes)
        
        # Filtro de Setor
        setores = ["Todos"] + sorted(df['setor'].unique().tolist())
        filtro_setor = st.selectbox("Setor", setores)
        
        # Lógica de Filtro
        if filtro_cliente != "Todas":
            df = df[df['cliente'] == filtro_cliente]
        if filtro_setor != "Todos":
            df = df[df['setor'] == filtro_setor]

    st.markdown("---")
    st.button("🔄 Atualizar Dados")

# 4. Conteúdo Principal
if df.empty:
    st.info("Aguardando os primeiros dados da pesquisa para gerar o Dashboard.")
else:
    st.title("📊 Indicadores Escrita Contabilidade")
    
    # Cards de Resumo (Topo da Imagem)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>Respostas</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    with c2:
        nps_medio = df['nps_score'].mean()
        st.markdown(f'<div class="metric-card"><h3>NPS Médio</h3><h2>{nps_medio:.1f}</h2></div>', unsafe_allow_html=True)
    with c3:
        # Cálculo Simples de Média Geral dos Indicadores
        media_total = df[['clareza', 'prazos', 'comunicacao', 'atendimento', 'custo']].mean().mean()
        st.markdown(f'<div class="metric-card"><h3>Média Geral</h3><h2>{media_total:.1f}</h2></div>', unsafe_allow_html=True)

    st.divider()

    # Gráfico de Tendência (NPS ao longo do tempo)
    st.subheader("📈 Tendência: Nota Geral (NPS)")
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
    df_tendencia = df.groupby(df['timestamp'].dt.date)['nps_score'].mean().reset_index()
    
    fig_tendencia = px.line(df_tendencia, x='timestamp', y='nps_score', 
                            markers=True, color_discrete_sequence=['#B79A5B'])
    fig_tendencia.update_layout(yaxis_range=[0,11], height=300)
    st.plotly_chart(fig_tendencia, use_container_width=True)

    st.divider()

    # Detalhes por Indicador (Gráficos de Rosca conforme imagem)
    st.subheader("🎯 Detalhes por Indicador")
    cols = st.columns(5)
    indicadores = ['clareza', 'prazos', 'comunicacao', 'atendimento', 'custo']
    nomes_bonitos = ['Clareza', 'Prazos', 'Comunicação', 'Atendimento', 'Custo']

    for i, ind in enumerate(indicadores):
        with cols[i]:
            media = df[ind].mean()
            # Criando um gráfico de rosca simples
            fig = px.pie(values=[media, 10-media], names=['Nota', 'Restante'],
                         hole=0.7, 
                         color_discrete_sequence=['#0E3A5D', '#E9ECEF'],
                         title=nomes_bonitos[i])
            fig.update_traces(textinfo='none')
            fig.update_layout(showlegend=False, height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"<center><b>{media:.1f}</b></center>", unsafe_allow_html=True)

    st.divider()
    
    # Lista de Comentários
    st.subheader("💬 Comentários Recentes")
    st.dataframe(df[['timestamp', 'cliente', 'nps_comment']].sort_values(by='timestamp', ascending=False), 
                 use_container_width=True)
