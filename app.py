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
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #B79A5B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    h2 { color: #0E3A5D; }
    h3 { color: #1F5E8C; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# 2. Função de Carga Segura
def load_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Usa os segredos configurados no Streamlit Cloud
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(st.secrets["SHEET_ID"])
        worksheet = sh.worksheet("respostas")
        
        # Lê todos os valores
        data = worksheet.get_all_values()
        if len(data) <= 1: # Se só tiver o cabeçalho ou estiver vazio
            return pd.DataFrame()
            
        # Cria o DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Limpa colunas sem nome para evitar o erro de duplicatas
        df = df.loc[:, df.columns != '']
        
        # Converte colunas de texto para números para os gráficos funcionarem
        colunas_notas = ['clareza', 'prazos', 'comunicacao', 'atendimento', 'custo', 'nps_score']
        for col in colunas_notas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Erro ao conectar na Planilha: {e}")
        return pd.DataFrame()

# Inicializa o DF para evitar o NameError
df = load_data()

# 3. Barra Lateral
with st.sidebar:
    try:
        st.image("Logo Escrita.png", width=180)
    except:
        st.write("### Escrita Contabilidade")
    
    st.markdown("---")
    st.markdown("### Filtros")
    
    # Só mostra filtros se houver dados
    if not df.empty:
        filtro_setor = st.selectbox("Setor", ["Todos"] + sorted(df['setor'].unique().tolist()))
        if filtro_setor != "Todos":
            df = df[df['setor'] == filtro_setor]
            
    if st.button("🔄 Atualizar"):
        st.rerun()

# 4. Layout Principal
st.title("📊 Dashboard de Performance")

if df.empty:
    st.warning("⚠️ Nenhuma resposta encontrada na aba 'respostas' da planilha.")
    st.info("Certifique-se de que o App de Pesquisa já enviou pelo menos uma resposta.")
else:
    # Métricas de Topo
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>Total de Respostas</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    with c2:
        media_nps = df['nps_score'].mean()
        st.markdown(f'<div class="metric-card"><h3>NPS Médio</h3><h2>{media_nps:.1f}</h2></div>', unsafe_allow_html=True)
    with c3:
        # Média dos indicadores específicos
        ind_cols = ['clareza', 'prazos', 'comunicacao', 'atendimento', 'custo']
        media_ind = df[ind_cols].mean().mean()
        st.markdown(f'<div class="metric-card"><h3>Média Operacional</h3><h2>{media_ind:.1f}</h2></div>', unsafe_allow_html=True)

    st.write("---")

    # Gráficos de Rosca (Indicadores)
    st.subheader("🎯 Desempenho por Indicador")
    cols = st.columns(5)
    labels = ["Clareza", "Prazos", "Comunicação", "Atendimento", "Custo"]
    keys = ['clareza', 'prazos', 'comunicacao', 'atendimento', 'custo']

    for i, col_name in enumerate(keys):
        with cols[i]:
            nota = df[col_name].mean()
            fig = px.pie(values=[nota, 10-nota], names=['Nota', ''],
                         hole=0.7, color_discrete_sequence=['#0E3A5D', '#E9ECEF'])
            fig.update_traces(textinfo='none')
            fig.update_layout(showlegend=False, height=180, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"<center><b>{labels[i]}</b><br><span style='font-size:20px'>{nota:.1f}</span></center>", unsafe_allow_html=True)

    st.write("---")
    
    # Tabela de Comentários
    st.subheader("💬 Feedbacks dos Clientes")
    st.dataframe(df[['timestamp', 'cliente', 'setor', 'nps_score', 'nps_comment']].sort_values(by='timestamp', ascending=False), 
                 use_container_width=True)
