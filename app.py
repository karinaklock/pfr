import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- Configurações da Página ---
st.set_page_config(page_title="Simulador PFR - Ka", layout="wide")

st.title("Simulador de Reator PFR: Craqueamento do Etano")

# --- Seção do Enunciado ---
with st.expander("Clique para ver o enunciado do problema", expanded=True):
    st.markdown("""
    **Problema:** Estudo da cinética de decomposição do etano ($C_2H_6$) em um reator tubular (PFR) 
    utilizando Óxido Nítrico ($NO$) como iniciador.
    
    *Considere as reações de iniciação, propagação e terminação conforme o modelo cinético fornecido.*
    """)

# --- Barra Lateral (Inputs do Usuário) ---
st.sidebar.header("Condições de Operação")
T_user = st.sidebar.slider("Temperatura (K)", 900, 1200, 1050)
P_user = st.sidebar.number_input("Pressão (atm)", value=1.0, step=0.1)
Qf_user = st.sidebar.number_input("Vazão Alimentação (cm³/s)", value=600)

# --- O Algoritmo (Mesma lógica que ajustamos antes) ---
def model(t, y, T, P):
    # (Inserir aqui a mesma função 'model' que passamos para o Python)
    # ... 
    return dNdt

# --- Execução da Simulação ---
if st.button("Rodar Simulação"):
    # Cálculo das condições iniciais e integração
    # ...
    
    # Exibição dos Resultados
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Perfil de Moles")
        # Plot do Matplotlib aqui
        st.pyplot(fig1)
    with col2:
        st.subheader("Vazão Volumétrica")
        # Plot do Matplotlib aqui
        st.pyplot(fig3)
