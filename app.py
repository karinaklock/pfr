import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Configurações iniciais
st.set_page_config(page_title="Simulador de Reatores - Ka", layout="wide")

# Menu de navegação na lateral
st.sidebar.title("📚 Biblioteca de Exercícios")
exercicio = st.sidebar.selectbox(
    "Escolha o exemplo:",
    ["Exemplo 4.7: Pirólise do Etano (PFR)", "Exemplo 4.2: Produção de Fenol (CSTR)"]
)

# --- CONSTANTES GLOBAIS ---
RG1, RG2 = 8.314, 82.06

# ==========================================
# OPÇÃO 1: PIRÓLISE DO ETANO (PFR)
# ==========================================
if exercicio == "Exemplo 4.7: Pirólise do Etano (PFR)":
    st.title("🔥 Pirólise do Etano com $NO$ (PFR)")
    
    with st.expander("📖 Enunciado", expanded=False):
        st.write("Cálculo dos fluxos molares em um PFR isotérmico com mecanismo de 6 reações.")

    # Sidebar específica para PFR
    st.sidebar.header("⚙️ Parâmetros Operacionais")
    T_base = st.sidebar.number_input("Temperatura (K)", value=1050.0)
    P = st.sidebar.number_input("Pressão (atm)", value=1.0)
    Qf = st.sidebar.number_input("Vazão (cm³/s)", value=600.0)
    
    # Inputs de Cinética (com valores default do código original)
    st.sidebar.header("🧪 Cinética (Ai e Ei)")
    A = []
    E = []
    A_defaults = [1e14, 3e14, 3.4e12, 1e12, 1e13, 1e12]
    E_defaults = [217.6, 165.3, 28.5, 0.0, 200.8, 0.0]
    
    for i in range(6):
        with st.sidebar.expander(f"Reação {i+1}"):
            A.append(st.number_input(f"A{i+1}", value=A_defaults[i], format="%.1e"))
            E.append(st.number_input(f"E{i+1} (kJ/mol)", value=E_defaults[i]) * 1000)

    # Função das EDOs (conforme o mecanismo do Exemplo 4.7)
    def pfr_system(v, y, T, P, A, E):
        N_total = max(np.sum(y), 1e-15)
        Q = (RG2 * T / P) * N_total
        C = y / Q
        k = [A[i] * np.exp(-E[i] / (RG1 * T)) for i in range(6)]
        r = [k[0]*C[0]*C[5], k[1]*C[1], k[2]*C[3]*C[0], k[3]*C[3]*C[5], k[4]*C[6], k[5]*C[1]*C[6]]
        return [-r[0]-r[2]+r[5], r[0]-r[1]+r[2]-r[5], r[1], r[1]-r[2]-r[3]+r[4], r[2], -r[0]-r[3]+r[4]+r[5], r[0]+r[3]-r[4]-r[5]]

    # Simulação
    y0 = [0.95*(Qf*P/(RG2*T_base)), 0, 0, 0, 0, 0.05*(Qf*P/(RG2*T_base)), 0]
    sol = solve_ivp(pfr_system, (0, 1500), y0, args=(T_base, P, A, E), t_eval=np.linspace(0, 1500, 200), method='LSODA')

    # Gráfico PFR
    fig, ax = plt.subplots()
    ax.plot(sol.t, sol.y[0], label="C2H6")
    ax.plot(sol.t, sol.y[2], label="C2H4")
    ax.set_xlabel("Volume (cm³)")
    ax.set_ylabel("Fluxo (mol/s)")
    ax.legend()
    st.pyplot(fig)

# ==========================================
# OPÇÃO 2: PRODUÇÃO DE FENOL (CSTR)
# ==========================================
elif exercicio == "Exemplo 4.2: Produção de Fenol (CSTR)":
    st.title("⚗️ Produção de Fenol em CSTR")
    
    with st.expander("📖 Enunciado e Solução", expanded=True):
        st.markdown("""
        Reação: $(C_6H_5)C(CH_3)_2OOH \\to (C_6H_5)OH + (CH_3)_2CO$
        
        Considerando uma reação de primeira ordem em fase líquida, onde a variação de volume é desprezada ($Q = Q_f$).
        O objetivo é encontrar o volume do reator ($V_R$) para atingir uma conversão específica ($X_A$).
        """)
        # Exibe a fórmula do volume conforme a imagem enviada
        st.latex(r"V_R = \frac{Q_f \cdot X_A}{k \cdot (1 - X_A)}")

    # Inputs baseados na imagem 7a8dda.png e 7a8dbb.png
    st.sidebar.header("⚙️ Parâmetros do CSTR")
    Qf_cstr = st.sidebar.number_input("Vazão (m³/h)", value=26.9)
    k_cstr = st.sidebar.number_input("Constante Cinética k (hr⁻¹)", value=4.12)
    Xa_target = st.sidebar.slider("Conversão Desejada (Xa)", 0.01, 0.99, 0.85)

    # Cálculo do Volume
    Vr = (Qf_cstr * Xa_target) / (k_cstr * (1 - Xa_target)) #

    # Resultados
    st.success(f"### Volume do Reator Necessário: {Vr:.2f} m³") #

    # Gráfico de Sensibilidade (Volume vs Conversão)
    st.subheader("Sensibilidade: Volume vs Conversão")
    X_range = np.linspace(0.1, 0.95, 50)
    V_range = (Qf_cstr * X_range) / (k_cstr * (1 - X_range))
    
    fig2, ax2 = plt.subplots()
    ax2.plot(X_range, V_range, 'g-', linewidth=2)
    ax2.scatter([Xa_target], [Vr], color='red', label=f'Ponto Operacional ({Xa_target*100}%)')
    ax2.set_xlabel("Conversão (Xa)")
    ax2.set_ylabel("Volume (m³)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)
