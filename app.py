import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Configuração da página
st.set_page_config(page_title="Biblioteca de Reatores - Ka", layout="wide")

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
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
        st.info("### Exemplo 4.7: PFR")
        st.write("**Sistema:** Pirólise do Etano com $NO$")
        st.write("Simulação de um reator tubular com mecanismo de 6 reações elementares e variação da vazão volumétrica.")
        if st.button("Abrir Simulação 4.7"):
            ir_para('4.7')

    with col2:
        st.success("### Exemplo 4.2: CSTR")
        st.write("**Sistema:** Produção de Fenol")
        st.write("Cálculo de dimensionamento (Volume vs Conversão) para uma reação de primeira ordem em fase líquida.")
        if st.button("Abrir Simulação 4.2"):
            ir_para('4.2')

# ==========================================
# PÁGINA DO EXERCÍCIO 4.7 (PFR - ETANO)
# ==========================================
elif st.session_state.pagina == '4.7':
    if st.button("⬅️ Voltar para o Menu Principal"):
        ir_para('home')
        st.rerun()

    st.title("🔥 Pirólise do Etano (Reator PFR)")
    
    with st.expander("📖 Detalhes do Mecanismo (Exemplo 4.7)", expanded=False):
        st.markdown("""
        O mecanismo envolve a decomposição do etano inibida por NO:
        1. $C_2H_6 + NO \\to C_2H_5 + HNO$ | 2. $C_2H_5 \\to H + C_2H_4$ | 3. $H + C_2H_6 \\to C_2H_5 + H_2$
        4. $H + NO \\to HNO$ | 5. $HNO \\to H + NO$ | 6. $C_2H_5 + HNO \\to C_2H_6 + NO$
        """)

    # --- SIDEBAR 4.7 ---
    st.sidebar.header("⚙️ Operação")
    T_base = st.sidebar.number_input("Temperatura Base (K)", value=1050.0)
    P = st.sidebar.number_input("Pressão (atm)", value=1.0)
    Qf = st.sidebar.number_input("Vazão de Entrada (cm³/s)", value=600.0)
    V_max = st.sidebar.slider("Volume do Reator (cm³)", 500, 3000, 1500)

    st.sidebar.header("🧪 Cinética (A_i e E_i)")
    A_defaults = [1.0e14, 3.0e14, 3.4e12, 1.0e12, 1.0e13, 1.0e12]
    E_defaults = [217.6, 165.3, 28.5, 0.0, 200.8, 0.0]
    A_user, E_user = [], []

    for i in range(6):
        with st.sidebar.expander(f"Reação {i+1}"):
            A_user.append(st.number_input(f"A{i+1}", value=A_defaults[i], format="%.1e", key=f"a{i}"))
            E_user.append(st.number_input(f"E{i+1} (kJ/mol)", value=E_defaults[i], key=f"e{i}") * 1000)

    def pfr_model(v, y, T, P, A, E):
        RG1, RG2 = 8.314, 82.06
        N_total = max(sum(y), 1e-15)
        Q = (RG2 * T / P) * N_total
        C = y / Q
        k = [A[i] * np.exp(-E[i] / (RG1 * T)) for i in range(6)]
        r = [k[0]*C[0]*C[5], k[1]*C[1], k[2]*C[3]*C[0], k[3]*C[3]*C[5], k[4]*C[6], k[5]*C[1]*C[6]]
        return [-r[0]-r[2]+r[5], r[0]-r[1]+r[2]-r[5], r[1], r[1]-r[2]-r[3]+r[4], r[2], -r[0]-r[3]+r[4]+r[5], r[0]+r[3]-r[4]-r[5]]

    # Simulação Principal
    RG2 = 82.06
    N0 = [0.95*(P*Qf/(RG2*T_base)), 0, 0, 0, 0, 0.05*(P*Qf/(RG2*T_base)), 0]
    sol = solve_ivp(pfr_model, (0, V_max), N0, args=(T_base, P, A_user, E_user), t_eval=np.linspace(0, V_max, 200), method='LSODA')

    tab1, tab2 = st.tabs(["📊 Perfis de Fluxo", "🌡️ Sensibilidade Térmica"])
    with tab1:
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(sol.t, sol.y[0], label="Etano")
        ax1.plot(sol.t, sol.y[2], label="Etileno")
        ax1.plot(sol.t, sol.y[5], '--', label="NO")
        ax1.set_xlabel("Volume (cm³)"); ax1.set_ylabel("Fluxo (mol/s)"); ax1.legend(); ax1.grid(True, alpha=0.2)
        st.pyplot(fig1)
    with tab2:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        for dT in [-50, 0, 50]:
            Ts = T_base + dT
            N0s = [0.95*(P*Qf/(RG2*Ts)), 0, 0, 0, 0, 0.05*(P*Qf/(RG2*Ts)), 0]
            res = solve_ivp(pfr_model, (0, V_max), N0s, args=(Ts, P, A_user, E_user), t_eval=np.linspace(0, V_max, 100), method='LSODA')
            ax2.plot(res.t, res.y[0], label=f"T = {Ts} K")
        ax2.set_title("Efeito da Temperatura no Etano"); ax2.legend(); ax2.grid(True, alpha=0.2)
        st.pyplot(fig2)

# ==========================================
# PÁGINA DO EXERCÍCIO 4.2 (CSTR - FENOL)
# ==========================================
elif st.session_state.pagina == '4.2':
    if st.button("⬅️ Voltar para o Menu Principal"):
        ir_para('home')
        st.rerun()

    st.title("⚗️ Produção de Fenol (Reator CSTR)")
    
    col_inp, col_res = st.columns([1, 2])
    
    with col_inp:
        st.subheader("Parâmetros do Processo")
        qf = st.number_input("Vazão Volumétrica $Q_f$ (m³/h)", value=26.9)
        k_val = st.number_input("Constante de Velocidade $k$ (h⁻¹)", value=4.12)
        xa_target = st.slider("Conversão Desejada ($X_A$)", 0.05, 0.95, 0.85)
        
        # Cálculo Algébrico
        vr_calc = (qf * xa_target) / (k_val * (1 - xa_target))
        st.write("---")
        st.metric("Volume Requerido", f"{vr_calc:.2f} m³")

    with col_res:
        st.subheader("Curva de Dimensionamento")
        x_range = np.linspace(0.01, 0.98, 100)
        v_range = (qf * x_range) / (k_val * (1 - x_range))
        
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ax3.plot(x_range, v_range, 'g-', linewidth=2, label="Volume Necessário")
        ax3.scatter([xa_target], [vr_calc], color='red', s=100, label="Ponto de Operação")
        ax3.set_ylim(0, vr_calc * 3) # Limita o eixo Y para melhor visualização
        ax3.set_xlabel("Conversão ($X_A$)"); ax3.set_ylabel("Volume ($V_R$ [m³])")
        ax3.legend(); ax3.grid(True, alpha=0.3)
        st.pyplot(fig3)
        
    st.info("**Nota Técnica:** Para reatores CSTR em fase líquida com volume constante, o tempo de residência é $\\tau = V_R / Q_f$.")
