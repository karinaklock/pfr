import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Configurações da página
st.set_page_config(page_title="PFR - Pirólise do Etano", layout="wide")

st.title("🔥 Simulação Interativa: Pirólise do Etano com $NO$")

# --- ENUNCIADO DO PROBLEMA ---
with st.expander("📖 Visualizar Mecanismo de Reação", expanded=False):
    st.markdown("""
    1. $C_2H_6 + NO \\xrightarrow{k_1} C_2H_5 + HNO$
    2. $C_2H_5 \\xrightarrow{k_2} H + C_2H_4$
    3. $H + C_2H_6 \\xrightarrow{k_3} C_2H_5 + H_2$
    4. $H + NO \\xrightarrow{k_4} HNO$
    5. $HNO \\xrightarrow{k_5} H + NO$
    6. $C_2H_5 + HNO \\xrightarrow{k_6} C_2H_6 + NO$
    """)

# --- BARRA LATERAL: INPUTS ---
st.sidebar.header("⚙️ Condições de Operação")
T_base = st.sidebar.number_input("Temperatura Base (K)", value=1050.0)
P = st.sidebar.number_input("Pressão Constante (atm)", value=1.0)
Qf = st.sidebar.number_input("Vazão de Entrada (cm³/s)", value=600.0)
V_max = st.sidebar.slider("Volume do Reator (cm³)", 100, 3000, 1500)

st.sidebar.header("🧪 Parâmetros Cinéticos ($A_i$ e $E_i$)")

# Listas para armazenar os inputs do usuário
A_user = []
E_user = []

# Valores padrão do enunciado para preencher os campos
A_defaults = [1.0e14, 3.0e14, 3.4e12, 1.0e12, 1.0e13, 1.0e12]
E_defaults = [217.6, 165.3, 28.5, 0.0, 200.8, 0.0]

# Criando inputs dinâmicos na sidebar
for i in range(6):
    with st.sidebar.expander(f"Reação {i+1}", expanded=False):
        # O usuário digita A_i e E_i (em kJ/mol)
        val_a = st.number_input(f"A{i+1}", value=A_defaults[i], format="%.1e", key=f"a{i}")
        val_e = st.number_input(f"E{i+1} (kJ/mol)", value=E_defaults[i], key=f"e{i}")
        A_user.append(val_a)
        E_user.append(val_e * 1000) # Converte kJ para J para o cálculo

# Constantes Físicas
RG1 = 8.314  # J/mol.K
RG2 = 82.06  # cm³.atm/mol.K

def dNdv(v, y, T, A, E):
    N_total = np.sum(y)
    Q = (RG2 * T / P) * max(N_total, 1e-15)
    C = y / Q
    
    # Constantes k_i calculadas com os inputs do usuário
    k = [A[i] * np.exp(-E[i] / (RG1 * T)) for i in range(6)]
    
    r = [
        k[0] * C[0] * C[5],       # r1
        k[1] * C[1],              # r2
        k[2] * C[3] * C[0],       # r3
        k[3] * C[3] * C[5],       # r4
        k[4] * C[6],              # r5
        k[5] * C[1] * C[6]        # r6
    ]
    
    return [
        -r[0] - r[2] + r[5],      # C2H6
        r[0] - r[1] + r[2] - r[5], # C2H5
        r[1],                      # C2H4
        r[1] - r[2] - r[3] + r[4], # H
        r[2],                      # H2
        -r[0] - r[3] + r[4] + r[5],# NO
        r[0] + r[3] - r[4] - r[5]  # HNO
    ]

# --- PROCESSAMENTO ---
N_total0 = (P * Qf) / (RG2 * T_base)
y0 = [0.95 * N_total0, 0, 0, 0, 0, 0.05 * N_total0, 0]
v_eval = np.linspace(0, V_max, 200)

# Simulação com os parâmetros atuais
sol = solve_ivp(dNdv, (0, V_max), y0, args=(T_base, A_user, E_user), t_eval=v_eval, method='LSODA')

# --- INTERFACE DE RESULTADOS ---
if sol.success:
    tab1, tab2 = st.tabs(["📊 Perfis de Fluxo", "🌡️ Sensibilidade à Temperatura"])

    with tab1:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(sol.t, sol.y[0], label="Ethane ($C_2H_6$)")
        ax1.plot(sol.t, sol.y[2], label="Ethylene ($C_2H_4$)")
        ax1.plot(sol.t, sol.y[5], '--', label="Nitric Oxide ($NO$)")
        ax1.set_xlabel("Volume (cm³)")
        ax1.set_ylabel("Molar Flow (mol/s)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        st.pyplot(fig1)

    with tab2:
        st.subheader("Efeito de ±50 K no Fluxo de Etano")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        for dT in [-50, 0, 50]:
            T_s = T_base + dT
            N0_s = (P * Qf) / (RG2 * T_s)
            y0_s = [0.95 * N0_s, 0, 0, 0, 0, 0.05 * N0_s, 0]
            res = solve_ivp(dNdv, (0, V_max), y0_s, args=(T_s, A_user, E_user), t_eval=v_eval, method='LSODA')
            ax2.plot(res.t, res.y[0], label=f"T = {T_s} K")
        
        ax2.set_xlabel("Volume (cm³)")
        ax2.set_ylabel("Ethane Flow (mol/s)")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
else:
    st.error("A simulação falhou com esses parâmetros. Verifique se os valores de $A$ e $E$ são fisicamente razoáveis.")
