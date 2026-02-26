import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, quad

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Biblioteca de Engenharia - Ka", layout="wide")

# --- ESTILIZAÇÃO CSS (Correção de Visualização e Botões) ---
st.markdown("""
    <style>
    /* Estilo Geral dos Botões */
    .stButton>button { 
        width: 100%; border-radius: 5px; height: 3.5em; 
        background-color: #007bff; color: white; font-weight: bold; 
    }
    /* Correção para as métricas (Texto visível) */
    [data-testid="stMetricValue"] { color: #003366 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #333333 !important; }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'

def ir_para(nome_da_pagina):
    st.session_state.pagina = nome_da_pagina

# ==========================================
# PÁGINA INICIAL (HOME)
# ==========================================
if st.session_state.pagina == 'home':
    st.title("📚 Biblioteca Interativa de Engenharia")
    st.subheader("Escolha um módulo para iniciar:")
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.info("### 🧪 Reatores Químicos")
        if st.button("Exemplo 4.7: PFR (Etano)"): ir_para('4.7')
        if st.button("Exemplo 4.2: CSTR (Fenol)"): ir_para('4.2')
        if st.button("Gráfico de Levenspiel (Comparador)"): ir_para('levenspiel')

    with col2:
        st.success("### 💧 Mecânica dos Fluidos")
        if st.button("Diagrama de Moody (Atrito em Tubos)"): ir_para('moody')
        st.write("---")
        st.warning("### 👩‍🔬 Sobre o Projeto")
        if st.button("Sobre Mim / YouTube"): ir_para('sobre')

# ==========================================
# PÁGINA: DIAGRAMA DE MOODY
# ==========================================
elif st.session_state.pagina == 'moody':
    if st.button("⬅️ Voltar ao Início"): ir_para('home'); st.rerun()
    st.title("📉 Diagrama de Moody Interativo")

    with st.expander("📌 Referência de Rugosidade (ε)", expanded=False):
        st.table({"Material": ["PVC", "Aço Comercial", "Aço Inox", "Ferro Fundido", "Concreto"],
                  "ε (mm)": [0.0015, 0.045, 0.015, 0.26, 0.3]})

    # Inputs
    st.sidebar.header("Parâmetros")
    vazao = st.sidebar.number_input("Vazão (m³/h)", value=10.0)
    diam_mm = st.sidebar.number_input("Diâmetro (mm)", value=50.0)
    rug_mm = st.sidebar.number_input("Rugosidade ε (mm)", value=0.045, format="%.4f")
    
    # Cálculos
    v = (vazao/3600) / (np.pi * (diam_mm/1000)**2 / 4)
    re = (998 * v * (diam_mm/1000)) / 0.001
    rr = rug_mm / diam_mm
    
    if re < 2000: f = 64/re
    else: f = 0.25 / (np.log10((rr/3.7) + (5.74/(re**0.9))))**2

    c1, c2, c3 = st.columns(3)
    c1.metric("Reynolds", f"{re:.0f}")
    c2.metric("Fator de Atrito", f"{f:.4f}")
    c3.metric("Velocidade", f"{v:.2f} m/s")

    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    re_plot = np.logspace(3, 8, 500)
    for eps in [0, 1e-4, 1e-3, 0.01, 0.05]:
        f_p = [0.25/(np.log10((eps/3.7)+(5.74/(r**0.9))))**2 if r>2000 else 64/r for r in re_plot]
        ax.plot(re_plot, f_p, color='gray', alpha=0.2)
    ax.scatter([re], [f], color='red', s=100, label="Sua Condição", marker='*')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.grid(True, which='both', alpha=0.3)
    st.pyplot(fig)

# ==========================================
# PÁGINA: SOBRE MIM
# ==========================================
elif st.session_state.pagina == 'sobre':
    if st.button("⬅️ Voltar ao Início"): ir_para('home'); st.rerun()
    st.title("Olá, eu sou a Ka! 👋")
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        st.image("https://cdn-icons-png.flaticon.com/512/1995/1995531.png", width=200)
    with col_txt:
        st.write("Estudante de Engenharia apaixonada por tecnologia e educação.")
        st.write("Criei este site para facilitar o entendimento de fenômenos de transporte e reatores.")
        st.link_button("Acesse meu Canal no YouTube", "https://www.youtube.com/@karinakc", type="primary")

# ==========================================
# LÓGICA DAS OUTRAS PÁGINAS (4.7, 4.2, LEVENSPIEL)
# ==========================================
elif st.session_state.pagina == '4.7':
    if st.button("⬅️ Voltar"): ir_para('home'); st.rerun()
    st.title("🔥 Exemplo 4.7: PFR")
    st.write("Simulação do craqueamento do etano baseada no script MATLAB.")
    # (Inserir aqui o código detalhado do PFR fornecido anteriormente)

elif st.session_state.pagina == '4.2':
    if st.button("⬅️ Voltar"): ir_para('home'); st.rerun()
    st.title("⚗️ Exemplo 4.2: CSTR")
    st.write("Cálculo de volume para produção de Fenol.")
    # (Inserir aqui o código detalhado do CSTR fornecido anteriormente)

elif st.session_state.pagina == 'levenspiel':
    if st.button("⬅️ Voltar"): ir_para('home'); st.rerun()
    st.title("📊 Gráfico de Levenspiel")
    # (Inserir aqui o código detalhado do Levenspiel fornecido anteriormente)
