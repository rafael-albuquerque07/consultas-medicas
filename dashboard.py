import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO
from datetime import datetime, timedelta
import numpy as np

# Configuração padrão do Plotly para evitar kwargs depreciados
PLOTLY_CONFIG = {
    "displaylogo": False,
        "scrollZoom": False,
    "modeBarButtonsToRemove": [
        "select2d", "lasso2d", "autoScale2d", "toggleSpikelines",
        "hoverClosestCartesian", "hoverCompareCartesian"
    ],
}

# ============== CONFIGURAÇÃO ==============
st.set_page_config(
    page_title="Dashboard de Consultas Médicas",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== CSS ==============
st.markdown("""
    <style>
    /* Importar fontes melhores */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Body e fundo */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    html, body {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
        color: #e4e6eb;
    }

    /* Escopo do app principal para evitar efeitos colaterais */
    .stApp, .main, [data-testid="stMainBlockContainer"], [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        box-sizing: border-box;
    }
    
    /* Main container */
    .main {
        background: transparent;
        padding: 0;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 2rem 3rem;
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
        border-right: 2px solid rgba(0, 212, 255, 0.1);
    }
    
    /* Header/Title Container - Fundo Escuro */
    [data-testid="stHeader"] {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%) !important;
    }
    
    [data-testid="stToolbar"] {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%) !important;
    }
    
    /* Garantir que h1 nunca tenha fundo branco */
    h1 {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Títulos - GRANDES E LEGÍVEIS */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #00d4ff !important;
        text-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
    }
    
    h2 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #00d4ff !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: #e4e6eb !important;
        margin-top: 1rem !important;
    }
    
    /* Parágrafos e texto */
    p, span, label {
        font-size: 1rem !important;
        color: #e4e6eb !important;
        line-height: 1.5;
    }
    
    /* Subtítulo */
    .subtitle {
        font-size: 1.1rem;
        color: #00d4ff;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, rgba(0,212,255,0) 0%, rgba(0,212,255,0.5) 50%, rgba(0,212,255,0) 100%);
        margin: 2rem 0;
    }
    
    /* Cards de Métrica - MUITO MAIOR */
    .metric-card {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.6) 0%, rgba(22, 33, 62, 0.4) 100%);
        border: 2px solid rgba(0, 212, 255, 0.2);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border: 2px solid rgba(0, 212, 255, 0.5);
        box-shadow: 0 12px 48px rgba(0, 212, 255, 0.15),
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #00d4ff !important;
        margin: 1rem 0;
    }
    
    .metric-label {
        font-size: 0.95rem !important;
        color: #a0a6af !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-change {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        margin-top: 0.8rem;
    }
    
    .metric-up {
        color: #00ff88 !important;
    }
    
    .metric-down {
        color: #ff6b6b !important;
    }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid rgba(0, 212, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #a0a6af !important;
        padding: 1rem 1.5rem !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #00d4ff !important;
        border-bottom: 3px solid #00d4ff !important;
    }
    
    /* Buttons */
    .stButton > button {
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
        color: white !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00e6ff 0%, #00aadd 100%) !important;
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.4);
        transform: translateY(-2px);
    }
    
    /* Input fields */
    .stDateInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div {
        background-color: rgba(15, 52, 96, 0.5) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        color: #e4e6eb !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stDateInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border: 2px solid rgba(0, 212, 255, 0.5) !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2) !important;
    }
    
    /* Mensagens */
    .stSuccess {
        background-color: rgba(0, 255, 136, 0.1) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        border-radius: 8px !important;
        color: #00ff88 !important;
    }
    
    .stError {
        background-color: rgba(255, 107, 107, 0.1) !important;
        border: 1px solid rgba(255, 107, 107, 0.3) !important;
        border-radius: 8px !important;
        color: #ff6b6b !important;
    }
    
    .stInfo {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 8px !important;
        color: #00d4ff !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        font-size: 1rem !important;
    }
    
    .stDataFrame table {
        background-color: rgba(15, 52, 96, 0.3) !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============== CARREGAR DADOS ==============
@st.cache_data(ttl=300)
def carregar_dados_github():
    """Carrega CSV do GitHub com jsDelivr"""
    url = "https://cdn.jsdelivr.net/gh/rafael-albuquerque07/consultas-medicas@main/consultas.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df['dataconsulta'] = pd.to_datetime(df['dataconsulta'])
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.info("💡 Certifique-se de que a URL do GitHub está correta")
        return None

def calcular_variacao(atual, anterior):
    # Tratamento robusto para evitar NaN e divisão por zero
    try:
        if pd.isna(atual) or pd.isna(anterior):
            return 0.0
        if anterior == 0:
            return 100.0 if atual > 0 else 0.0
        return ((atual - anterior) / anterior) * 100.0
    except Exception:
        return 0.0

def formatar_variacao(variacao):
    if variacao > 0:
        return f"↑ +{variacao:.1f}%"
    elif variacao < 0:
        return f"↓ {variacao:.1f}%"
    else:
        return f"→ {variacao:.1f}%"

# ============== CARREGAR DADOS ==============
df = carregar_dados_github()

if df is None:
    st.stop()

# ============== HEADER ==============
col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
with col_header2:
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>🏥 Dashboard de Consultas Médicas</h1>
            <p class='subtitle'>Análise Avançada com 4 Melhorias & Comparação de Períodos</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ============== ABAS PRINCIPAIS ==============
tab1, tab2, tab3 = st.tabs(["📊 Análise Simples", "🔄 Comparação Períodos", "📋 Dados Completos"])

# ================================================================
# TAB 1: ANÁLISE SIMPLES
# ================================================================
with tab1:
    # SIDEBAR FILTROS
    st.sidebar.markdown("<h2 style='font-size: 1.4rem; margin-top: 2rem;'>🎯 Filtros Avançados</h2>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<h3 style='font-size: 1.1rem; margin-top: 1.5rem;'>📅 Período</h3>", unsafe_allow_html=True)
    # Garantir objetos date para st.date_input
    data_min = df['dataconsulta'].min()
    data_max = df['dataconsulta'].max()
    data_min_date = data_min.date()
    data_max_date = data_max.date()
    
    col_data1, col_data2 = st.sidebar.columns(2)
    with col_data1:
        data_inicio = st.date_input("De:", value=data_min_date, min_value=data_min_date, max_value=data_max_date, key="tab1_inicio")
    with col_data2:
        data_fim = st.date_input("Até:", value=data_max_date, min_value=data_min_date, max_value=data_max_date, key="tab1_fim")
    
    st.sidebar.markdown("<h3 style='font-size: 1.1rem; margin-top: 1.5rem;'>🏢 Unidades</h3>", unsafe_allow_html=True)
    unidades = sorted(df['unidade'].unique())
    opcao_unidade = st.sidebar.multiselect("Selecione:", options=unidades, default=unidades, key="tab1_unidades")
    
    # APLICAR FILTROS
    df_filtrado = df[
        (df['dataconsulta'].dt.date >= data_inicio) &
        (df['dataconsulta'].dt.date <= data_fim)
    ]
    
    if opcao_unidade:
        df_filtrado = df_filtrado[df_filtrado['unidade'].isin(opcao_unidade)]
    
    # PERÍODO ANTERIOR
    dias_diferenca = (pd.to_datetime(data_fim) - pd.to_datetime(data_inicio)).days + 1
    data_inicio_anterior = pd.to_datetime(data_inicio) - timedelta(days=dias_diferenca)
    data_fim_anterior = pd.to_datetime(data_inicio) - timedelta(days=1)
    
    df_anterior = df[
        (df['dataconsulta'].dt.date >= data_inicio_anterior.date()) &
        (df['dataconsulta'].dt.date <= data_fim_anterior.date())
    ]
    
    if opcao_unidade:
        df_anterior = df_anterior[df_anterior['unidade'].isin(opcao_unidade)]
    
    # PERÍODO TEXTO
    periodo_texto = f"{data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"
    st.markdown(f"""
        <div style='text-align: center; background: rgba(0, 212, 255, 0.05); 
                    padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0, 212, 255, 0.2);
                    margin: 1.5rem 0;'>
            <p style='font-size: 1.1rem; color: #00d4ff; margin: 0;'>
                📊 <strong>Período Selecionado:</strong> {periodo_texto}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # ============== MÉTRICAS ==============
    st.markdown("<h2>📊 Indicadores Principais (com Variação %)</h2>", unsafe_allow_html=True)

    def _safe_mean(series):
        m = float(series.mean()) if len(series) > 0 else 0.0
        return 0.0 if pd.isna(m) else m

    def format_brl(v: float) -> str:
        try:
            return (f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        except Exception:
            return f"R$ {v}"
    
    total_consultas_atual = len(df_filtrado)
    unidades_ativas_atual = df_filtrado['unidade'].nunique()
    faturamento_atual = float(df_filtrado['valor'].sum())
    retorno_medio_atual = _safe_mean(df_filtrado['retornodaconsulta'])
    
    total_consultas_anterior = len(df_anterior)
    unidades_ativas_anterior = df_anterior['unidade'].nunique()
    faturamento_anterior = float(df_anterior['valor'].sum())
    retorno_medio_anterior = _safe_mean(df_anterior['retornodaconsulta'])
    
    var_consultas = calcular_variacao(total_consultas_atual, total_consultas_anterior)
    var_unidades = calcular_variacao(unidades_ativas_atual, unidades_ativas_anterior)
    var_faturamento = calcular_variacao(faturamento_atual, faturamento_anterior)
    var_retorno = calcular_variacao(retorno_medio_atual, retorno_medio_anterior)
    
    # CARDS METRICS
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total de Consultas</div>
                <div class='metric-value'>{total_consultas_atual}</div>
                <div class='metric-change metric-{"up" if var_consultas >= 0 else "down"}'>
                    {formatar_variacao(var_consultas)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Unidades Ativas</div>
                <div class='metric-value'>{unidades_ativas_atual}</div>
                <div class='metric-change metric-{"up" if var_unidades >= 0 else "down"}'>
                    {formatar_variacao(var_unidades)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Faturamento Total</div>
                <div class='metric-value'>{format_brl(faturamento_atual)}</div>
                <div class='metric-change metric-{"up" if var_faturamento >= 0 else "down"}'>
                    {formatar_variacao(var_faturamento)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Retorno Médio</div>
                <div class='metric-value'>{retorno_medio_atual:.1f}d</div>
                <div class='metric-change metric-{"up" if var_retorno >= 0 else "down"}'>
                    {formatar_variacao(var_retorno)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ============== GRÁFICOS 1 E 2 ==============
    st.markdown("<h2>📈 Distribuição por Categoria</h2>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2, gap="large")
    
    with col_g1:
        consultas_unidade = df_filtrado.groupby('unidade').size().reset_index(name='Total')
        consultas_unidade = consultas_unidade.sort_values('Total', ascending=False)
        
        fig1 = px.bar(
            consultas_unidade, x='unidade', y='Total',
            title='Consultas por Unidade',
            labels={'unidade': 'Unidade', 'Total': 'Consultas'},
            color='Total', color_continuous_scale='Viridis'
        )
        fig1.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            hovermode='x unified',
            title_font_size=16,
            title_font_color='#00d4ff',
            showlegend=False,
            margin=dict(l=50, r=20, t=60, b=50)
        )
        fig1.update_traces(marker_line_width=0)
        st.plotly_chart(fig1, config=PLOTLY_CONFIG)
    
    with col_g2:
        consultas_tipo = df_filtrado.groupby('tipoconsulta').size().reset_index(name='Total')
        
        fig2 = px.pie(
            consultas_tipo, values='Total', names='tipoconsulta',
            title='Consultas por Especialidade',
            hole=0.4,
            color_discrete_sequence=['#00d4ff', '#ff6b6b', '#00ff88', '#ffd700']
        )
        fig2.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            title_font_size=16,
            title_font_color='#00d4ff',
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig2, config=PLOTLY_CONFIG)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ============== SÉRIE TEMPORAL ==============
    st.markdown("<h2>📊 Série Temporal - Evolução Diária</h2>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2, gap="large")
    
    with col_t1:
        consultas_diarias = df_filtrado.groupby(df_filtrado['dataconsulta'].dt.date).size().reset_index()
        consultas_diarias.columns = ['Data', 'Total']
        consultas_diarias['Data'] = pd.to_datetime(consultas_diarias['Data'])
        
        fig3 = px.line(
            consultas_diarias, x='Data', y='Total',
            title='Consultas por Dia',
            markers=True, line_shape='spline'
        )
        fig3.update_traces(line_color='#00d4ff', marker_size=8, marker_color='#ffd700')
        fig3.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            hovermode='x unified',
            title_font_size=16,
            title_font_color='#00d4ff',
            margin=dict(l=50, r=20, t=60, b=50)
        )
        st.plotly_chart(fig3, config=PLOTLY_CONFIG)
    
    with col_t2:
        faturamento_diario = df_filtrado.groupby(df_filtrado['dataconsulta'].dt.date)['valor'].sum().reset_index()
        faturamento_diario.columns = ['Data', 'Faturamento']
        faturamento_diario['Data'] = pd.to_datetime(faturamento_diario['Data'])
        
        fig4 = px.line(
            faturamento_diario, x='Data', y='Faturamento',
            title='Faturamento por Dia',
            markers=True, line_shape='spline'
        )
        fig4.update_traces(line_color='#ff6b6b', marker_size=8, marker_color='#00ff88')
        fig4.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            hovermode='x unified',
            title_font_size=16,
            title_font_color='#00d4ff',
            margin=dict(l=50, r=20, t=60, b=50)
        )
        st.plotly_chart(fig4, config=PLOTLY_CONFIG)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ============== GRÁFICOS FINANCEIROS ==============
    st.markdown("<h2>💰 Análise Financeira</h2>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2, gap="large")
    
    with col_f1:
        faturamento_unidade = df_filtrado.groupby('unidade')['valor'].sum().reset_index()
        faturamento_unidade = faturamento_unidade.sort_values('valor', ascending=True)
        
        fig5 = px.bar(
            faturamento_unidade, x='valor', y='unidade',
            orientation='h',
            title='Faturamento Total por Unidade',
            labels={'valor': 'Faturamento (R$)', 'unidade': 'Unidade'},
            color='valor', color_continuous_scale='Reds'
        )
        fig5.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            hovermode='y unified',
            title_font_size=16,
            title_font_color='#00d4ff',
            showlegend=False,
            margin=dict(l=50, r=20, t=60, b=50)
        )
        st.plotly_chart(fig5, config=PLOTLY_CONFIG)
    
    with col_f2:
        faturamento_tipo = df_filtrado.groupby('tipoconsulta')['valor'].sum().reset_index()
        faturamento_tipo = faturamento_tipo.sort_values('valor', ascending=False)
        
        fig6 = px.bar(
            faturamento_tipo, x='tipoconsulta', y='valor',
            title='Faturamento por Especialidade',
            labels={'tipoconsulta': 'Especialidade', 'valor': 'Faturamento (R$)'},
            color='valor', color_continuous_scale='Greens'
        )
        fig6.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            hovermode='x unified',
            title_font_size=16,
            title_font_color='#00d4ff',
            showlegend=False,
            margin=dict(l=50, r=20, t=60, b=50)
        )
        fig6.update_traces(marker_line_width=0)
        st.plotly_chart(fig6, config=PLOTLY_CONFIG)

# ================================================================
# TAB 2: COMPARAÇÃO PERÍODOS
# ================================================================
with tab2:
    st.markdown("<h2>🔄 Comparação Entre Dois Períodos</h2>", unsafe_allow_html=True)
    st.info("💡 Selecione dois períodos diferentes para compará-los lado a lado")
    
    st.sidebar.markdown("<h2 style='font-size: 1.4rem; margin-top: 2rem;'>🎯 Filtros Comparação</h2>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<h3 style='font-size: 1.1rem;'>📅 Período A (Esquerda)</h3>", unsafe_allow_html=True)
    col_a1, col_a2 = st.sidebar.columns(2)
    with col_a1:
        data_a_inicio = st.date_input("De:", value=data_min_date, min_value=data_min_date, max_value=data_max_date, key="comp_a_inicio")
    with col_a2:
        data_a_fim = st.date_input("Até:", value=(data_min_date + timedelta(days=2)), min_value=data_min_date, max_value=data_max_date, key="comp_a_fim")
    
    st.sidebar.markdown("<h3 style='font-size: 1.1rem;'>📅 Período B (Direita)</h3>", unsafe_allow_html=True)
    col_b1, col_b2 = st.sidebar.columns(2)
    with col_b1:
        data_b_inicio = st.date_input("De:", value=(data_min_date + timedelta(days=3)), min_value=data_min_date, max_value=data_max_date, key="comp_b_inicio")
    with col_b2:
        data_b_fim = st.date_input("Até:", value=data_max_date, min_value=data_min_date, max_value=data_max_date, key="comp_b_fim")
    
    st.sidebar.markdown("<h3 style='font-size: 1.1rem;'>🏢 Unidades</h3>", unsafe_allow_html=True)
    opcao_unidade_comp = st.sidebar.multiselect("Selecione:", options=unidades, default=unidades, key="comp_unidades")
    
    # APLICAR FILTROS
    df_periodo_a = df[
        (df['dataconsulta'].dt.date >= data_a_inicio) &
        (df['dataconsulta'].dt.date <= data_a_fim)
    ]
    
    df_periodo_b = df[
        (df['dataconsulta'].dt.date >= data_b_inicio) &
        (df['dataconsulta'].dt.date <= data_b_fim)
    ]
    
    if opcao_unidade_comp:
        df_periodo_a = df_periodo_a[df_periodo_a['unidade'].isin(opcao_unidade_comp)]
        df_periodo_b = df_periodo_b[df_periodo_b['unidade'].isin(opcao_unidade_comp)]
    
    periodo_a_txt = f"{data_a_inicio.strftime('%d/%m/%Y')} até {data_a_fim.strftime('%d/%m/%Y')}"
    periodo_b_txt = f"{data_b_inicio.strftime('%d/%m/%Y')} até {data_b_fim.strftime('%d/%m/%Y')}"
    
    col_info_a, col_info_b = st.columns(2, gap="medium")
    with col_info_a:
        st.markdown(f"""
            <div style='background: rgba(0, 212, 255, 0.1); padding: 1.2rem; border-radius: 12px; 
                        border: 2px solid rgba(0, 212, 255, 0.3); text-align: center;'>
                <p style='font-size: 1.1rem; color: #00d4ff; margin: 0;'><strong>Período A:</strong></p>
                <p style='font-size: 0.95rem; color: #e4e6eb; margin: 0.5rem 0 0 0;'>{periodo_a_txt}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_info_b:
        st.markdown(f"""
            <div style='background: rgba(255, 107, 107, 0.1); padding: 1.2rem; border-radius: 12px; 
                        border: 2px solid rgba(255, 107, 107, 0.3); text-align: center;'>
                <p style='font-size: 1.1rem; color: #ff6b6b; margin: 0;'><strong>Período B:</strong></p>
                <p style='font-size: 0.95rem; color: #e4e6eb; margin: 0.5rem 0 0 0;'>{periodo_b_txt}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # CALCULAR MÉTRICAS
    total_a = len(df_periodo_a)
    unidades_a = df_periodo_a['unidade'].nunique()
    faturamento_a = df_periodo_a['valor'].sum()
    retorno_a = _safe_mean(df_periodo_a['retornodaconsulta'])
    
    total_b = len(df_periodo_b)
    unidades_b = df_periodo_b['unidade'].nunique()
    faturamento_b = df_periodo_b['valor'].sum()
    retorno_b = _safe_mean(df_periodo_b['retornodaconsulta'])
    
    dif_consultas = calcular_variacao(total_b, total_a)
    dif_unidades = calcular_variacao(unidades_b, unidades_a)
    dif_faturamento = calcular_variacao(faturamento_b, faturamento_a)
    dif_retorno = calcular_variacao(retorno_b, retorno_a)
    
    st.markdown("<h2>📊 Comparação de Métricas</h2>", unsafe_allow_html=True)
    
    col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4, gap="medium")
    
    with col_comp1:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total de Consultas</div>
                <div style='display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;'>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.8rem; font-weight: 700; color: #00d4ff;'>{total_a}</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período A</div>
                    </div>
                    <div style='color: #666; font-size: 1.5rem;'>→</div>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.8rem; font-weight: 700; color: #ff6b6b;'>{total_b}</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período B</div>
                    </div>
                </div>
                <div class='metric-change metric-{"up" if dif_consultas >= 0 else "down"}'
                     style='text-align: center;'>
                    {formatar_variacao(dif_consultas)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_comp2:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Unidades Ativas</div>
                <div style='display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;'>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.8rem; font-weight: 700; color: #00d4ff;'>{unidades_a}</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período A</div>
                    </div>
                    <div style='color: #666; font-size: 1.5rem;'>→</div>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.8rem; font-weight: 700; color: #ff6b6b;'>{unidades_b}</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período B</div>
                    </div>
                </div>
                <div class='metric-change metric-{"up" if dif_unidades >= 0 else "down"}'
                     style='text-align: center;'>
                    {formatar_variacao(dif_unidades)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_comp3:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Faturamento Total</div>
                <div style='display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;'>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: 700; color: #00d4ff;'>{format_brl(faturamento_a)}</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período A</div>
                    </div>
                    <div style='color: #666; font-size: 1.5rem;'>→</div>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.5rem; font-weight: 700; color: #ff6b6b;'>{format_brl(faturamento_b)}</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período B</div>
                    </div>
                </div>
                <div class='metric-change metric-{"up" if dif_faturamento >= 0 else "down"}'
                     style='text-align: center;'>
                    {formatar_variacao(dif_faturamento)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_comp4:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Retorno Médio</div>
                <div style='display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;'>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.8rem; font-weight: 700; color: #00d4ff;'>{retorno_a:.1f}d</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período A</div>
                    </div>
                    <div style='color: #666; font-size: 1.5rem;'>→</div>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.8rem; font-weight: 700; color: #ff6b6b;'>{retorno_b:.1f}d</div>
                        <div style='font-size: 0.8rem; color: #a0a6af;'>Período B</div>
                    </div>
                </div>
                <div class='metric-change metric-{"up" if dif_retorno >= 0 else "down"}'
                     style='text-align: center;'>
                    {formatar_variacao(dif_retorno)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2>📊 Visualizações Comparativas</h2>", unsafe_allow_html=True)
    
    col_cg1, col_cg2 = st.columns(2, gap="large")
    
    with col_cg1:
        comp_a_unidade = df_periodo_a.groupby('unidade').size().reset_index(name='Período A')
        comp_b_unidade = df_periodo_b.groupby('unidade').size().reset_index(name='Período B')
        comp_unidade = comp_a_unidade.merge(comp_b_unidade, on='unidade', how='outer').fillna(0)
        
        fig_comp1 = px.bar(
            comp_unidade, x='unidade', y=['Período A', 'Período B'],
            title='Consultas por Unidade (Comparação)',
            barmode='group',
            color_discrete_map={'Período A': '#00d4ff', 'Período B': '#ff6b6b'}
        )
        fig_comp1.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            title_font_size=16,
            title_font_color='#00d4ff',
            hovermode='x unified',
            margin=dict(l=50, r=20, t=60, b=50)
        )
        st.plotly_chart(fig_comp1, config=PLOTLY_CONFIG)
    
    with col_cg2:
        comp_a_esp = df_periodo_a.groupby('tipoconsulta')['valor'].sum().reset_index(name='Período A')
        comp_b_esp = df_periodo_b.groupby('tipoconsulta')['valor'].sum().reset_index(name='Período B')
        comp_esp = comp_a_esp.merge(comp_b_esp, on='tipoconsulta', how='outer').fillna(0)
        
        fig_comp2 = px.bar(
            comp_esp, x='tipoconsulta', y=['Período A', 'Período B'],
            title='Faturamento por Especialidade (Comparação)',
            barmode='group',
            color_discrete_map={'Período A': '#00d4ff', 'Período B': '#ff6b6b'}
        )
        fig_comp2.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 52, 96, 0.3)',
            font=dict(size=12, color='#e4e6eb', family='Inter'),
            height=450,
            title_font_size=16,
            title_font_color='#00d4ff',
            hovermode='x unified',
            margin=dict(l=50, r=20, t=60, b=50)
        )
        st.plotly_chart(fig_comp2, config=PLOTLY_CONFIG)


# ================================================================
# TAB 3: DADOS COMPLETOS
# ================================================================
with tab3:
    st.markdown("<h2>📋 Dados Completos</h2>", unsafe_allow_html=True)
    
    df_tabela = df.copy()
    df_tabela['dataconsulta'] = df_tabela['dataconsulta'].dt.strftime("%d/%m/%Y")
    df_tabela.columns = ['Data', 'Unidade', 'Especialidade', 'Valor (R$)', 'Retorno']
    df_tabela = df_tabela.sort_values('Data', ascending=False)
    
    st.dataframe(
        df_tabela,
        hide_index=True,
        height=600
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2>📊 Estatísticas Gerais</h2>", unsafe_allow_html=True)
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4, gap="medium")
    
    with col_stat1:
        st.metric("Total de Registros", len(df), delta=None)
    with col_stat2:
        st.metric("Período", f"{df['dataconsulta'].min().date()} a {df['dataconsulta'].max().date()}", delta=None)
    with col_stat3:
        st.metric("Faturamento Total", format_brl(float(df['valor'].sum())), delta=None)
    with col_stat4:
        st.metric("Valor Médio", format_brl(float(df['valor'].mean() if not pd.isna(df['valor'].mean()) else 0.0)), delta=None)


# ═══════════════════════════════════════════════════════════════
# 🏥 RODAPÉ DO DASHBOARD
# ═══════════════════════════════════════════════════════════════

st.markdown("<hr style='margin: 3rem 0;'>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"""
    <div style='text-align: center; padding: 3rem 0; color: #a0a6af;
                border-top: 2px solid rgba(0, 212, 255, 0.2);
                border-radius: 10px;'>
        <p style='font-size: 0.95rem; font-weight: 600;'>
            🏥 Dashboard de Consultas Médicas
        </p>
        <p style='font-size: 0.95rem; font-weight: 600;'>
            AUTOR: Rafael Albuquerque
        </p>
        <p style='font-size: 0.85rem; margin-top: 0.5rem;'>
            Última atualização: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </p>
        <p style='font-size: 0.85rem; color: #00d4ff; margin-top: 1rem;'>
            Com 4 Melhorias: Date Range + Série Temporal + Variação % + Comparação Períodos
        </p>
        <p style='font-size: 0.8rem; color: #7a7f88; margin-top: 0.5rem;'>
            Streamlit + Plotly + Pandas • Design Premium
        </p>
    </div>
""", unsafe_allow_html=True)
