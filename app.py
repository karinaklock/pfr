import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Configurações da página
st.set_page_config(page_title="PFR - Pirólise do Etano", layout="wide")

st.title("🔥 Simulação: Pirólise do Etano com $NO$")

# --- ENUNCIADO DO PROBLEMA ---
with st.expander("📖 Visualizar Enunciado Completo (Exemplo 4.7)", expanded=True):
    st.markdown("""
    A decomposição térmica do etano é inibida pelo óxido nítrico. O mecanismo proposto envolve:
    1. $C_2H_6 + NO \\xrightarrow{k_1} C_2H_5 + HNO$
    2. $C_2H_5 \\xrightarrow{k_2} H + C_2H_4$
    3. $H + C_2H_6 \\xrightarrow{k_3} C_2H_5 + H_2$
    4. $H + NO \\xrightarrow{k_4} HNO$
    5. $HNO \\xrightarrow{k_5} H + NO$
    6. $C_2H_5 + HNO \\xrightarrow{k_6} C_2H_6 + NO$
    """)
    st.info("**Objetivo:** Calcular os fluxos molares e avaliar o efeito da temperatura na conversão.")

# --- BARRA LATERAL: ENTRADAS ---
st.sidebar.header("🕹️ Parâmetros de Entrada")
T_base = st.sidebar.number_input("Temperatura Base (K)", value=1050.0)
P = st.sidebar.number_input("Pressão Constante (atm)", value=1.0)
Qf = st.sidebar.number_input("Vazão Volumétrica de Entrada (cm³/s)", value=600.0)
V_max = st.sidebar.slider("Volume do Reator (cm³)", 100, 3000, 1500)

# Constantes Físicas e Cinéticas (Baseadas na Tabela do Enunciado)
RG1 = 8.314  # J/mol.K (para energia de ativação)
RG2 = 82.06  # cm³.atm/mol.K (para lei dos gases)

A = [1.0e14, 3.0e14, 3.4e12, 1.0e12, 1.0e13, 1.0e12]
E = [217.6e3, 165.3e3, 28.5e3, 0.0, 200.8e3, 0.0]

def dNdv(v, y, T):
    # y = [N_C2H6, N_C2H5, N_C2H4, N_H, N_H2, N_NO, N_HNO]
    N_total = np.sum(y)
    Q = (RG2 * T / P) * N_total
    C = y / Q
    
    # Constantes de velocidade k_i
    k = [A[i] * np.exp(-E[i] / (RG1 * T)) for i in range(6)]
    
    # Taxas de reação r_i
    r = [
        k[0] * C[0] * C[5],       # r1
        k[1] * C[1],              # r2
        k[2] * C[3] * C[0],       # r3
        k[3] * C[3] * C[5],       # r4
        k[4] * C[6],              # r5
        k[5] * C[1] * C[6]        # r6
    ]
    
    # Balanços molares (R_j)
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
# Condição Inicial: 95% Etano, 5% NO
N_total0 = (P * Qf) / (RG2 * T_base)
y0 = [0.95 * N_total0, 0, 0, 0, 0, 0.05 * N_total0, 0]
v_eval = np.linspace(0, V_max, 200)

# Simulação Base (T = 1050 K)
sol_base = solve_ivp(dNdv, (0, V_max), y0, args=(T_base,), t_eval=v_eval, method='LSODA')

# --- INTERFACE DE RESULTADOS ---
tab1, tab2 = st.tabs(["📊 Perfis de Fluxo", "🌡️ Sensibilidade Térmica"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(sol_base.t, sol_base.y[0], 'b-', label="$C_2H_6$")
        ax1.plot(sol_base.t, sol_base.y[2], 'r-', label="$C_2H_4$")
        ax1.plot(sol_base.t, sol_base.y[5], 'g--', label="$NO$")
        ax1.set_xlabel("Volume (cm³)")
        ax1.set_ylabel("Fluxo Molar (mol/s)")
        ax1.legend()
        ax1.grid(alpha=0.3)
        st.pyplot(fig1)
    
    with col2:
        st.write("**Composição de Saída (mol/s):**")
        especies = ["Etano", "Etila", "Etileno", "H+", "H2", "NO", "HNO"]
        for i, esp in enumerate(especies):
            st.metric(esp, f"{sol_base.y[i][-1]:.2e}")

with tab2:
    st.subheader("Efeito de $\pm 50$ K no Etano")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    
    for dT in [-50, 0, 50]:
        T_sim = T_base + dT
        # Ajusta N0 para a nova T para manter Qf e P constantes
        N0_sim = (P * Qf) / (RG2 * T_sim)
        y0_sim = [0.95 * N0_sim, 0, 0, 0, 0, 0.05 * N0_sim, 0]
        
        res = solve_ivp(dNdv, (0, V_max), y0_sim, args=(T_sim,), t_eval=v_eval, method='LSODA')
        ax2.plot(res.t, res.y[0], label=f"T = {T_sim} K")
    
    ax2.set_xlabel("Volume (cm³)")
    ax2.set_ylabel("Fluxo de Etano (mol/s)")
    ax2.legend()
    ax2.grid(alpha=0.3)
    st.pyplot(fig2)
    
    st.write("**Análise:** Note como pequenas variações na temperatura alteram drasticamente a curva. Isso ocorre devido à dependência exponencial da constante de Arrhenius ($k$) em relação a $T$.")
