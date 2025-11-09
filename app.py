import streamlit as st
import json
import os
import sys
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import subprocess
import time
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="IA Leilão Imóveis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .info-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .risk-alert {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #856404;
        font-weight: 500;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #155724;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Funções auxiliares
@st.cache_data(ttl=60)  # Cache por 60 segundos apenas
def load_config():
    """Carrega configurações do config.json"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar config.json: {e}")
        return {}

def save_config(config):
    """Salva configurações no config.json"""
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

@st.cache_data
def load_available_properties():
    """Carrega lista de imóveis disponíveis"""
    properties = []
    data_dir = Path("data/detail")
    
    if data_dir.exists():
        for city_folder in data_dir.iterdir():
            if city_folder.is_dir():
                for html_file in city_folder.glob("*.html"):
                    imovel_id = html_file.stem
                    properties.append({
                        "id": imovel_id,
                        "cidade": city_folder.name,
                        "arquivo": str(html_file)
                    })
    
    return properties

def create_radar_chart(criterios):
    """Cria gráfico radar com os critérios de avaliação"""
    categories = [c["nome"] for c in criterios]
    values = [c["nota"] for c in criterios]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Avaliação',
        line=dict(color='#667eea', width=2),
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickmode='linear',
                tick0=0,
                dtick=2
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    return fig

def display_property_info(imovel_data):
    """Exibe informações do imóvel em formato organizado"""
    st.markdown("### 📋 Informações do Imóvel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**🏢 Identificação**")
        st.write(f"**Condomínio:** {imovel_data.get('condominio', 'N/A')}")
        st.write(f"**Apartamento:** {imovel_data.get('apartamento', 'N/A')}")
        st.write(f"**Bloco:** {imovel_data.get('bloco', 'N/A')}")
        st.write(f"**Matrícula:** {imovel_data.get('matricula', 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**📏 Características**")
        st.write(f"**Área Privativa:** {imovel_data.get('area_privativa_m2', 'N/A')} m²")
        st.write(f"**Área Total:** {imovel_data.get('area_total_m2', 'N/A')} m²")
        st.write(f"**Quartos:** {imovel_data.get('quartos', 'N/A')}")
        st.write(f"**Vagas:** {imovel_data.get('vaga_garagem', 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**💰 Valores**")
        st.write(f"**Avaliação:** {imovel_data.get('avaliacao', 'N/A')}")
        st.write(f"**Valor Mínimo:** {imovel_data.get('valor_minimo', 'N/A')}")
        st.write(f"**Desconto:** {imovel_data.get('desconto_percent', 'N/A')}")
        st.write(f"**Comarca:** {imovel_data.get('comarca', 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)

def display_analysis_results(analysis_data):
    """Exibe resultados da análise de forma visual"""
    
    # Nota Final em destaque
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        nota_final = analysis_data["nota_final"]["valor"]
        
        # Determina cor baseada na nota
        if nota_final >= 7:
            color = "#28a745"
            emoji = "🟢"
            status = "EXCELENTE"
        elif nota_final >= 5:
            color = "#ffc107"
            emoji = "🟡"
            status = "BOM"
        else:
            color = "#dc3545"
            emoji = "🔴"
            status = "ATENÇÃO"
        
        st.markdown(f"""
        <div style="background: {color}; padding: 2rem; border-radius: 15px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 4rem;">{emoji} {nota_final:.1f}</h1>
            <h3 style="margin: 0.5rem 0 0 0;">{status}</h3>
            <p style="margin: 0.5rem 0 0 0;">Nota Final do Imóvel</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informações do Imóvel
    display_property_info(analysis_data["imovel"])
    
    # Critérios de Avaliação
    st.markdown("### 📊 Análise por Critérios")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gráfico Radar
        st.plotly_chart(create_radar_chart(analysis_data["criterios"]), 
                       use_container_width=True)
    
    with col2:
        # Detalhes dos Critérios
        for criterio in analysis_data["criterios"]:
            with st.expander(f"**{criterio['nome']}** - Nota: {criterio['nota']}/10 (Peso: {criterio['peso']*100:.0f}%)"):
                st.write(f"**Justificativa:** {criterio['justificativa']}")
                if criterio.get('fontes'):
                    st.write("**Fontes:**")
                    for fonte in criterio['fontes']:
                        st.write(f"- {fonte}")
    
    # Riscos
    st.markdown("### ⚠️ Riscos Identificados")
    for i, risco in enumerate(analysis_data["riscos"], 1):
        if risco.get("descricao"):
            st.markdown(f"""
            <div class="risk-alert">
                <strong>Risco {i}:</strong> {risco['descricao']}<br>
                <small><strong>Fonte:</strong> {risco.get('fonte', 'N/A')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Próximos Passos
    st.markdown("### ✅ Próximos Passos Recomendados")
    for i, passo in enumerate(analysis_data["proximos_passos"], 1):
        if passo:
            st.markdown(f"""
            <div class="success-box">
                <strong>{i}.</strong> {passo}
            </div>
            """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/real-estate.png", width=80)
    st.markdown("# 🏠 Leilão IA")
    st.markdown("---")
    
    page = st.radio(
        "Navegação",
        ["🏠 Início", "🔍 Buscar Imóveis", "🤖 Analisar Imóvel", "📊 Ranking"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Configurações")
    
    config = load_config()
    
    estado = st.text_input("Estado (sigla)", value=config.get("estado", "PE"))
    cidade = st.text_input("Cidade", value=config.get("cidade", "RECIFE"))
    
    if st.button("💾 Salvar Configurações"):
        config["estado"] = estado
        config["cidade"] = cidade
        save_config(config)
        st.success("Configurações salvas!")
        st.cache_data.clear()
    
    st.markdown("---")
    st.markdown("**Desenvolvido por:**")
    st.markdown("🐸 Frog | 32 | Delay")

# Página: Início
if page == "🏠 Início":
    st.markdown('<p class="main-header">🏠 IA Analisadora de Leilões de Imóveis</p>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 Sobre o Projeto
    
    Este sistema utiliza **Inteligência Artificial** para analisar e ranquear imóveis de leilão da 
    Caixa Econômica Federal, auxiliando na tomada de decisão para investimentos em **revenda rápida (flip)**.
    
    ### 🚀 Funcionalidades
    
    - **🔍 Buscar Imóveis**: Realize web scraping do site da Caixa para obter lista de imóveis disponíveis
    - **🤖 Analisar com IA**: Análise automatizada usando GPT-4o para avaliar viabilidade de investimento
    - **📊 Ranking**: Compare múltiplos imóveis e identifique as melhores oportunidades
    
    ### 📋 Critérios de Avaliação
    
    O sistema avalia cada imóvel em 5 critérios principais:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        1. **Liquidez & Preço de Entrada** (30%)
           - Deságio vs. avaliação
           - Tipologia e localização
        
        2. **Situação Registral & Risco Jurídico** (25%)
           - Cadeia dominial
           - Pendências judiciais
        
        3. **Despesas Propter Rem** (20%)
           - IPTU e condomínio
           - Passivos
        """)
    
    with col2:
        st.markdown("""
        4. **Prazos de Contratação & Registro** (15%)
           - Compatibilidade com horizonte de 6 meses
        
        5. **Velocidade de Liquidez** (10%)
           - Potencial de revenda rápida
        
        &nbsp;
        """)
    
    st.markdown("---")
    
    # Estatísticas (se houver dados)
    properties = load_available_properties()
    
    if properties:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📁 Imóveis Coletados", len(properties))
        
        with col2:
            cidades = len(set([p["cidade"] for p in properties]))
            st.metric("🏙️ Cidades", cidades)
        
        with col3:
            st.metric("🤖 Status IA", "✅ Ativo")
        
        with col4:
            st.metric("📊 Análises Hoje", "-")
    
    st.markdown("---")
    st.info("👈 Use o menu lateral para navegar entre as funcionalidades")

# Página: Buscar Imóveis
elif page == "🔍 Buscar Imóveis":
    st.markdown('<p class="main-header">🔍 Buscar Imóveis no Site da Caixa</p>', 
                unsafe_allow_html=True)
    
    config = load_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📝 Configuração da Busca
        
        Esta ferramenta realiza **web scraping** do site oficial de leilões da Caixa Econômica Federal.
        
        **Passos:**
        1. Configure estado e cidade na barra lateral
        2. Execute a busca de lista de imóveis
        3. Baixe os detalhes de cada imóvel encontrado
        """)
    
    with col2:
        st.info(f"""
        **Configuração Atual:**
        - **Estado:** {config.get('estado', 'Não configurado')}
        - **Cidade:** {config.get('cidade', 'Não configurado')}
        
        Altere nas configurações da barra lateral se necessário.
        """)
    
    st.markdown("---")
    
    # Buscar lista de imóveis
    st.markdown("### 📋 Passo 1: Buscar Lista de Imóveis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("🔍 Executar Busca de Lista", type="primary", use_container_width=True):
            with st.spinner("🤖 Executando scraping... Isso pode levar alguns minutos..."):
                try:
                    # Usa o Python do ambiente virtual
                    python_exe = sys.executable
                    result = subprocess.run(
                        [python_exe, "scrape_property_list.py"],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Lista de imóveis obtida com sucesso!")
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ Erro: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("⏱️ Timeout: A busca demorou mais de 5 minutos")
                except Exception as e:
                    st.error(f"❌ Erro ao executar: {str(e)}")
    
    with col2:
        # Verificar se existe arquivo de lista
        list_file = Path(f"data/list/imoveis_{config.get('cidade', '').lower()}_{config.get('estado', '').lower()}.html")
        if list_file.exists():
            st.success(f"✅ Arquivo encontrado: {list_file.name}")
            st.caption(f"Modificado em: {datetime.fromtimestamp(list_file.stat().st_mtime).strftime('%d/%m/%Y %H:%M')}")
        else:
            st.warning("⚠️ Nenhuma lista encontrada ainda")
    
    st.markdown("---")
    
    # Baixar detalhes
    st.markdown("### 📥 Passo 2: Baixar Detalhes dos Imóveis")
    
    st.warning("⚠️ **Atenção:** Esta operação pode demorar vários minutos, pois baixa detalhes de cada imóvel individualmente.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("📥 Baixar Todos os Detalhes", type="primary", use_container_width=True):
            with st.spinner("🤖 Baixando detalhes... Aguarde..."):
                try:
                    # Usa o Python do ambiente virtual
                    python_exe = sys.executable
                    result = subprocess.run(
                        [python_exe, "scrape_detail.py"],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutos
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Detalhes baixados com sucesso!")
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ Erro: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("⏱️ Timeout: A operação demorou mais de 30 minutos")
                except Exception as e:
                    st.error(f"❌ Erro ao executar: {str(e)}")
    
    with col2:
        properties = load_available_properties()
        if properties:
            st.success(f"✅ {len(properties)} imóveis com detalhes disponíveis")
        else:
            st.info("ℹ️ Nenhum detalhe baixado ainda")
    
    st.markdown("---")
    
    # Lista de imóveis disponíveis
    if properties:
        st.markdown("### 📊 Imóveis Disponíveis")
        
        df = pd.DataFrame(properties)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Página: Analisar Imóvel
elif page == "🤖 Analisar Imóvel":
    st.markdown('<p class="main-header">🤖 Analisar Imóvel com IA</p>', 
                unsafe_allow_html=True)
    
    config = load_config()
    
    # Verificar se assistente está configurado
    if not config.get("assistant_id") or not config.get("edital_file_id"):
        st.error("""
        ❌ **Configuração Incompleta!**
        
        Você precisa primeiro:
        1. Fazer upload do edital: `python upload_edital.py`
        2. Criar o assistente: `python create_assistent.py`
        """)
        st.stop()
    
    properties = load_available_properties()
    
    if not properties:
        st.warning("⚠️ Nenhum imóvel disponível. Execute a busca primeiro!")
        st.stop()
    
    # Seleção de imóvel
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_property = st.selectbox(
            "Selecione um imóvel para análise:",
            options=properties,
            format_func=lambda x: f"{x['id']} - {x['cidade']}"
        )
    
    with col2:
        st.markdown("&nbsp;")
        analyze_button = st.button("🤖 Analisar com IA", type="primary", use_container_width=True)
    
    # Mostrar informações do imóvel selecionado
    if selected_property:
        st.info(f"""
        **Imóvel Selecionado:**
        - **ID:** {selected_property['id']}
        - **Localização:** {selected_property['cidade']}
        - **Arquivo:** {selected_property['arquivo']}
        """)
    
    # Executar análise
    if analyze_button:
        with st.spinner("🤖 Analisando imóvel com IA... Isso pode levar alguns minutos..."):
            try:
                # Recarregar config.json direto do arquivo (sem cache) e atualizar imóvel
                with open("config.json", "r") as f:
                    fresh_config = json.load(f)
                fresh_config["imovel"] = selected_property["id"]
                save_config(fresh_config)
                
                # Executar query.py com o Python do ambiente virtual
                python_exe = sys.executable
                result = subprocess.run(
                    [python_exe, "query.py"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    # Tentar extrair JSON da saída
                    output = result.stdout
                    
                    # Procurar pelo JSON na saída
                    try:
                        # Encontrar o início e fim do JSON
                        start_idx = output.find("{")
                        end_idx = output.rfind("}") + 1
                        
                        if start_idx != -1 and end_idx != 0:
                            json_str = output[start_idx:end_idx]
                            analysis_data = json.loads(json_str)
                            
                            # Salvar resultado
                            output_dir = Path("data/analysis")
                            output_dir.mkdir(parents=True, exist_ok=True)
                            
                            output_file = output_dir / f"{selected_property['id']}_analysis.json"
                            with open(output_file, "w", encoding="utf-8") as f:
                                json.dump(analysis_data, f, indent=4, ensure_ascii=False)
                            
                            st.success(f"✅ Análise concluída! Resultado salvo em: {output_file}")
                            
                            # Exibir resultados
                            st.markdown("---")
                            display_analysis_results(analysis_data)
                            
                            # Opção de download
                            st.markdown("---")
                            st.download_button(
                                label="📥 Baixar Análise (JSON)",
                                data=json.dumps(analysis_data, indent=4, ensure_ascii=False),
                                file_name=f"analise_{selected_property['id']}.json",
                                mime="application/json"
                            )
                        else:
                            st.error("❌ Não foi possível extrair o JSON da resposta")
                            with st.expander("Ver saída completa"):
                                st.code(output)
                    
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Erro ao decodificar JSON: {str(e)}")
                        with st.expander("Ver saída completa"):
                            st.code(output)
                else:
                    st.error(f"❌ Erro na análise: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                st.error("⏱️ Timeout: A análise demorou mais de 5 minutos")
            except Exception as e:
                st.error(f"❌ Erro ao executar análise: {str(e)}")
    
    # Mostrar análises anteriores
    st.markdown("---")
    st.markdown("### 📂 Análises Anteriores")
    
    analysis_dir = Path("data/analysis")
    if analysis_dir.exists():
        analysis_files = list(analysis_dir.glob("*_analysis.json"))
        
        if analysis_files:
            for analysis_file in sorted(analysis_files, key=lambda x: x.stat().st_mtime, reverse=True):
                with st.expander(f"📄 {analysis_file.stem}"):
                    try:
                        with open(analysis_file, "r", encoding="utf-8") as f:
                            past_analysis = json.load(f)
                        
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.metric("Nota Final", f"{past_analysis['nota_final']['valor']:.1f}/10")
                        with col2:
                            st.caption(f"Analisado em: {datetime.fromtimestamp(analysis_file.stat().st_mtime).strftime('%d/%m/%Y %H:%M')}")
                        
                        if st.button(f"Ver Detalhes", key=analysis_file.name):
                            display_analysis_results(past_analysis)
                    except Exception as e:
                        st.error(f"Erro ao carregar: {str(e)}")
        else:
            st.info("Nenhuma análise anterior encontrada")
    else:
        st.info("Nenhuma análise anterior encontrada")

# Página: Ranking
elif page == "📊 Ranking":
    st.markdown('<p class="main-header">📊 Ranking de Imóveis</p>', 
                unsafe_allow_html=True)
    
    # Carregar todas as análises
    analysis_dir = Path("data/analysis")
    
    if not analysis_dir.exists() or not list(analysis_dir.glob("*_analysis.json")):
        st.warning("⚠️ Nenhuma análise disponível ainda. Analise alguns imóveis primeiro!")
        st.stop()
    
    analysis_files = list(analysis_dir.glob("*_analysis.json"))
    
    # Carregar dados de todas as análises
    rankings = []
    
    for analysis_file in analysis_files:
        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            imovel_id = analysis_file.stem.replace("_analysis", "")
            
            rankings.append({
                "ID": imovel_id,
                "Nota Final": data["nota_final"]["valor"],
                "Condomínio": data["imovel"].get("condominio", "N/A"),
                "Quartos": data["imovel"].get("quartos", "N/A"),
                "Área (m²)": data["imovel"].get("area_privativa_m2", "N/A"),
                "Desconto": data["imovel"].get("desconto_percent", "N/A"),
                "Comarca": data["imovel"].get("comarca", "N/A"),
                "Arquivo": str(analysis_file)
            })
        except Exception as e:
            st.warning(f"Erro ao carregar {analysis_file.name}: {str(e)}")
    
    if not rankings:
        st.error("Nenhuma análise válida encontrada")
        st.stop()
    
    # Criar DataFrame
    df = pd.DataFrame(rankings)
    df = df.sort_values("Nota Final", ascending=False).reset_index(drop=True)
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Total Analisados", len(df))
    
    with col2:
        st.metric("🏆 Melhor Nota", f"{df['Nota Final'].max():.1f}")
    
    with col3:
        st.metric("📊 Média Geral", f"{df['Nota Final'].mean():.1f}")
    
    with col4:
        excelentes = len(df[df["Nota Final"] >= 7])
        st.metric("⭐ Excelentes (≥7)", excelentes)
    
    st.markdown("---")
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nota_minima = st.slider("Nota Mínima", 0.0, 10.0, 0.0, 0.5)
    
    with col2:
        comarcas = ["Todas"] + sorted(df["Comarca"].unique().tolist())
        comarca_filter = st.selectbox("Comarca", comarcas)
    
    with col3:
        quartos_filter = st.multiselect("Quartos", sorted(df["Quartos"].unique()))
    
    # Aplicar filtros
    df_filtered = df[df["Nota Final"] >= nota_minima]
    
    if comarca_filter != "Todas":
        df_filtered = df_filtered[df_filtered["Comarca"] == comarca_filter]
    
    if quartos_filter:
        df_filtered = df_filtered[df_filtered["Quartos"].isin(quartos_filter)]
    
    st.info(f"📊 Mostrando {len(df_filtered)} de {len(df)} imóveis")
    
    st.markdown("---")
    
    # Tabela de ranking
    st.markdown("### 🏆 Ranking")
    
    # Adicionar coluna de posição
    df_display = df_filtered.copy()
    df_display.insert(0, "Posição", range(1, len(df_display) + 1))
    
    # Formatar para exibição
    df_display_formatted = df_display.drop(columns=["Arquivo"])
    
    # Colorir células baseado na nota
    def color_nota(val):
        if isinstance(val, (int, float)):
            if val >= 7:
                return 'background-color: #d4edda'
            elif val >= 5:
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #f8d7da'
        return ''
    
    styled_df = df_display_formatted.style.applymap(
        color_nota,
        subset=['Nota Final']
    )
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Gráfico de distribuição
    st.markdown("---")
    st.markdown("### 📈 Distribuição de Notas")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_display["ID"],
        y=df_display["Nota Final"],
        marker=dict(
            color=df_display["Nota Final"],
            colorscale='RdYlGn',
            cmin=0,
            cmax=10,
            colorbar=dict(title="Nota")
        ),
        text=df_display["Nota Final"].round(1),
        textposition='outside'
    ))
    
    fig.update_layout(
        xaxis_title="ID do Imóvel",
        yaxis_title="Nota Final",
        yaxis=dict(range=[0, 11]),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Exportar
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Ranking (CSV)",
            data=csv,
            file_name=f"ranking_imoveis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Detalhes ao clicar
    st.markdown("---")
    st.markdown("### 🔍 Ver Detalhes de um Imóvel")
    
    selected_id = st.selectbox(
        "Selecione um imóvel para ver detalhes completos:",
        df_display["ID"].tolist()
    )
    
    if st.button("📄 Carregar Detalhes", use_container_width=True):
        selected_row = df[df["ID"] == selected_id].iloc[0]
        analysis_file = Path(selected_row["Arquivo"])
        
        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                analysis_data = json.load(f)
            
            st.markdown("---")
            display_analysis_results(analysis_data)
        except Exception as e:
            st.error(f"Erro ao carregar detalhes: {str(e)}")

