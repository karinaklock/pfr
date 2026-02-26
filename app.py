import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Configuração da página
st.set_page_config(page_title="Biblioteca de Reatores - Ka", layout="wide")

# --- ESTILIZAÇÃO (Opcional para deixar mais bonito) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
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
    st.title("📚 Biblioteca Interativa de Engenharia Química")
    st.subheader("Selecione um exercício para iniciar a simulação:")
    st.write("---")

    col1, col2 = st.columns(2)

    with col1:
        st.info("### Exemplo 4.7")
        st.write("**Tipo:** PFR (Reator Tubular)")
        st.write("**Sistema:** Pirólise do Etano com NO")
        st.write("Simulação diferencial de 6 reações elementares com variação de volume.")
        if st.button("Abrir Simulação 4.7"):
            ir_para('4.7')

    with col2:
        st.success("### Exemplo 4.2")
        st.write("**Tipo:** CSTR (Reator de Mistura)")
        st.write("**Sistema:** Produção de Fenol")
        st.write("Cálculo algébrico de volume e conversão para reações de primeira ordem.")
        if st.button("Abrir Simulação 4.2"):
            ir_para('4.2')

# ==========================================
# PÁGINA DO EXERCÍCIO 4.7 (PFR)
# ==========================================
elif st.session_state.pagina == '4.7':
    if st.button("⬅️ Voltar para o Início"):
        ir_para('home')
        st.rerun()

    st.title("🔥 Pirólise do Etano (PFR)")
    
    # Agora a barra lateral só aparece aqui
    st.sidebar.header("Configurações 4.7")
    T = st.sidebar.slider("Temperatura (K)", 900, 1200, 1050)
    # ... (restante do código do PFR que já fizemos)
    st.write("Aqui entra todo o seu simulador do etano...")

# ==========================================
# PÁGINA DO EXERCÍCIO 4.2 (CSTR)
# ==========================================
elif st.session_state.pagina == '4.2':
    if st.button("⬅️ Voltar para o Início"):
        ir_para('home')
        st.rerun()

    st.title("⚗️ Produção de Fenol (CSTR)")
    
    # Especificações técnicas bem visíveis
    col_inf, col_sim = st.columns([1, 2])
    
    with col_inf:
        st.markdown("### Especificações")
        st.write("- **Fase:** Líquida")
        st.write("- **Cinética:** Primeira Ordem")
        st.latex(r"r = k \cdot C_{CHP}")
        
        # Inputs específicos
        qf = st.number_input("Vazão (m³/h)", value=26.9)
        k_val = st.number_input("k (h⁻¹)", value=4.12)
        xa = st.slider("Conversão Alvo", 0.1, 0.99, 0.85)

    with col_sim:
        vr = (qf * xa) / (k_val * (1 - xa))
        st.metric("Volume do Reator (Vr)", f"{vr:.2f} m³")
        
        # Gráfico
        x_plot = np.linspace(0.01, 0.95, 100)
        v_plot = (qf * x_plot) / (k_val * (1 - x_plot))
        fig, ax = plt.subplots()
        ax.plot(x_plot, v_plot)
        ax.scatter([xa], [vr], color='red')
        ax.set_title("Curva de Dimensionamento CSTR")
        st.pyplot(fig)
