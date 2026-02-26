import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Configurações da página
st.set_page_config(page_title="Simulador PFR", layout="wide")

st.title("🚀 Simulador de Reator PFR: Craqueamento do Etano")

# --- ENUNCIADO ---
with st.expander("📄 Ver Enunciado do Problema", expanded=True):
    st.markdown("""
    Este simulador modela a decomposição térmica do etano ($C_2H_6$) em um reator tubular (PFR) 
    operando em regime permanente, utilizando óxido nítrico ($NO$) como iniciador de reação. 
    A variação da vazão volumétrica devido à variação do número de moles é considerada.
    """)

# --- PARÂMETROS CINÉTICOS (Constantes) ---
A11, A12, A2 = 1e14, 1e12, 3e14
A3, A41, A42 = 3.4e12, 1e12, 1e13
E11, E12, E2 = 217.6e3, 0, 165.3e3
E3, E41, E42 = 28.5e3, 0, 200.8e3
RG1, RG2 = 8.314, 82.06

# --- SIDEBAR (Entradas do Usuário) ---
st.sidebar.header("⚙️ Condições de Operação")
T = st.sidebar.slider("Temperatura (K)", 900, 1200, 1050)
P = st.sidebar.number_input("Pressão (atm)", value=1.0)
Qf = st.sidebar.number_input("Vazão de Alimentação (cm³/s)", value=600)
V_final = st.sidebar.number_input("Volume Final do Reator (cm³)", value=1500)

def equacoes(t, y, T, P):
    N = np.array(y)
    # Evita divisão por zero ou valores negativos durante a integração
    N = np.maximum(N, 1e-15)
    
    k11 = A11 * np.exp(-E11 / (RG1 * T))
    k12 = A12 * np.exp(-E12 / (RG1 * T))
    k2  = A2  * np.exp(-E2  / (RG1 * T))
    k3  = A3  * np.exp(-E3  / (RG1 * T))
    k41 = A41 * np.exp(-E41 / (RG1 * T))
    k42 = A42 * np.exp(-E42 / (RG1 * T))
    
    Q = (RG2 * T / P) * np.sum(N)
    C = N / Q
    
    r1 = k11 * C[0] * C[5] - k12 * C[1] * C[6]
    r2 = k2  * C[1]
    r3 = k3  * C[3] * C[0]
    r4 = k41 * C[3] * C[5] - k42 * C[6]
    
    return [
        -r1 - r3,          # dN1
        r1 - r2 + r3,      # dN2
        r2,                # dN3
        r2 - r3 - r4,      # dN4
        r3,                # dN5
        -r1 - r4,          # dN6
        r1 + r4            # dN7
    ]

# --- EXECUÇÃO ---
y0 = [0.95*Qf*P/(RG2*T), 0, 0, 0, 0, 0.05*Qf*P/(RG2*T), 0]
v_span = (0, V_final)
v_eval = np.linspace(0, V_final, 200)

sol = solve_ivp(equacoes, v_span, y0, args=(T, P), t_eval=v_eval, method='LSODA')

if sol.success:
    col1, col2 = st.columns(2)

    # Gráfico 1: Moles
    with col1:
        fig1, ax1 = plt.subplots()
        ax1.plot(sol.t, sol.y[0], label="C2H6")
        ax1.plot(sol.t, sol.y[2], label="C2H4")
        ax1.plot(sol.t, sol.y[5], label="NO")
        ax1.set_xlabel("Volume [cm³]")
        ax1.set_ylabel("Vazão Molar [mol/s]")
        ax1.legend()
        ax1.grid(True)
        st.pyplot(fig1)

    # Gráfico 2: Vazão Volumétrica
    with col2:
        fig2, ax2 = plt.subplots()
        Q_total = (RG2 * T / P) * np.sum(sol.y, axis=0)
        ax2.plot(sol.t, Q_total, color='orange')
        ax2.set_xlabel("Volume [cm³]")
        ax2.set_ylabel("Vazão Volumétrica [cm³/s]")
        ax2.grid(True)
        st.pyplot(fig2)
else:
    st.error("Erro na integração das equações. Tente ajustar os parâmetros.")
