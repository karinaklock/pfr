import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, quad

# Configuração da página
st.set_page_config(page_title="Biblioteca de Reatores - Ka", layout="wide")

# --- ESTILIZAÇÃO ATUALIZADA ---
st.markdown("""
    <style>
    /* Estilo para os botões */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        height: 3em; 
        background-color: #007bff; 
        color: white; 
        font-weight: bold; 
    }
    /* Correção para os cards de métricas (Gráfico de Levenspiel) */
    [data-testid="stMetricValue"] {
        color: #003366 !important; /* Azul escuro para o número */
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #333333 !important; /* Cinza escuro para o rótulo */
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6; /* Fundo cinza claro para contraste */
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d1d5db;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# PÁGINA INICIAL (HOME)
# ==========================================
if st.session_state.pagina == 'home':
    st.title("📚 Biblioteca Interativa de Engenharia Química")
    st.subheader("Selecione um exercício para iniciar a simulação:")
    st.write("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("### Exemplo 4.7: PFR")
        st.write("**Sistema:** Pirólise do Etano")
        st.write("Simulação diferencial de 6 reações com variação de vazão.")
        if st.button("Abrir PFR"): ir_para('4.7')

    with col2:
        st.success("### Exemplo 4.2: CSTR")
        st.write("**Sistema:** Produção de Fenol")
        st.write("Cálculo algébrico simples para reações em fase líquida.")
        if st.button("Abrir CSTR"): ir_para('4.2')

    with col3:
        st.warning("### Comparador Levenspiel")
        st.write("**Conceito:** PFR vs CSTR")
        st.write("Visualização de áreas e comparação de volumes para diferentes cinéticas.")
        if st.button("Abrir Comparador"): ir_para('levenspiel')

# ==========================================
# PÁGINA: LEVENSPIEL (PFR vs CSTR)
# ==========================================
elif st.session_state.pagina == 'levenspiel':
    if st.button("⬅️ Voltar para o Menu Principal"):
        ir_para('home')
        st.rerun()

    st.title("📊 Gráfico de Levenspiel: PFR vs CSTR")
    st.markdown("Neste exemplo, comparamos o volume necessário para atingir a mesma conversão em dois reatores diferentes.")

    # Sidebar
    st.sidebar.header("Parâmetros da Reação")
    fa0 = st.sidebar.number_input("Fluxo Molar Inicial Fa0 (mol/h)", value=10.0)
    ca0 = st.sidebar.number_input("Conc. Inicial Ca0 (mol/L)", value=2.0)
    k_const = st.sidebar.number_input("Constante k", value=0.5)
    ordem = st.sidebar.selectbox("Ordem da Reação", [1, 2])
    xa_target = st.sidebar.slider("Conversão Desejada (X)", 0.05, 0.95, 0.80)

    # Lógica de cálculo
    def lev_func(x):
        # -ra = k * Ca^n = k * (Ca0 * (1-x))^n
        ra = k_const * (ca0 * (1 - x))**ordem
        return fa0 / ra

    # Volume CSTR: (Fa0/-ra)_exit * X
    v_cstr = lev_func(xa_target) * xa_target
    
    # Volume PFR: Integral de (Fa0/-ra) dX de 0 a X
    v_pfr, _ = quad(lev_func, 0, xa_target)

    # Exibição de Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Volume PFR", f"{v_pfr:.2f} L")
    c2.metric("Volume CSTR", f"{v_cstr:.2f} L")
    c3.metric("Razão CSTR/PFR", f"{v_cstr/v_pfr:.2f}")

    # Gráfico
    x_vals = np.linspace(0, xa_target + 0.05, 100)
    y_vals = [lev_func(x) for x in x_vals]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_vals, y_vals, 'k-', linewidth=2, label="$F_{A0}/-r_A$")
    
    # Área PFR (Sombreado sob a curva)
    x_pfr = np.linspace(0, xa_target, 50)
    y_pfr = [lev_func(x) for x in x_pfr]
    ax.fill_between(x_pfr, y_pfr, color='blue', alpha=0.3, label='Volume PFR')
    
    # Área CSTR (Retângulo)
    ax.add_patch(plt.Rectangle((0, 0), xa_target, lev_func(xa_target), 
                                edgecolor='red', facecolor='none', hatch='//', linewidth=2, label='Volume CSTR'))

    ax.set_xlabel("Conversão (X)")
    ax.set_ylabel("$F_{A0}/-r_A$ (L)")
    ax.set_title(f"Gráfico de Levenspiel (Ordem {ordem})")
    ax.legend()
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)
    
    st.info("**Explicação:** No gráfico de Levenspiel, o volume do PFR é a área **sob a curva**, enquanto o volume do CSTR é a área do **retângulo** definido pelo ponto de saída. Para reações de ordem positiva, o PFR será sempre menor que o CSTR.")

# ==========================================
# PÁGINA DO EXERCÍCIO 4.7 (PFR - ETANO)
# ==========================================
elif st.session_state.pagina == '4.7':
    if st.button("⬅️ Voltar para o Menu Principal"):
        ir_para('home')
        st.rerun()

    st.title("🔥 Pirólise do Etano (Reator PFR)")
    
    # --- SIDEBAR 4.7 ---
    st.sidebar.header("⚙️ Operação")
    T_base = st.sidebar.number_input("Temperatura Base (K)", value=1050.0)
    P = st.sidebar.number_input("Pressão (atm)", value=1.0)
    Qf = st.sidebar.number_input("Vazão de Entrada (cm³/s)", value=600.0)
    V_max = st.sidebar.slider("Volume do Reator (cm³)", 500, 3000, 1500)

    st.sidebar.header("🧪 Cinética")
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

    RG2 = 82.06
    N0 = [0.95*(P*Qf/(RG2*T_base)), 0, 0, 0, 0, 0.05*(P*Qf/(RG2*T_base)), 0]
    sol = solve_ivp(pfr_model, (0, V_max), N0, args=(T_base, P, A_user, E_user), t_eval=np.linspace(0, V_max, 200), method='LSODA')

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(sol.t, sol.y[0], label="Etano")
    ax1.plot(sol.t, sol.y[2], label="Etileno")
    ax1.set_xlabel("Volume (cm³)"); ax1.set_ylabel("Fluxo (mol/s)"); ax1.legend(); ax1.grid(True, alpha=0.2)
    st.pyplot(fig1)

# ==========================================
# PÁGINA DO EXERCÍCIO 4.2 (CSTR - FENOL)
# ==========================================
elif st.session_state.pagina == '4.2':
    if st.button("⬅️ Voltar para o Menu Principal"):
        ir_para('home')
        st.rerun()

    st.title("⚗️ Produção de Fenol (Reator CSTR)")
    
    qf = st.number_input("Vazão Volumétrica $Q_f$ (m³/h)", value=26.9)
    k_val = st.number_input("Constante de Velocidade $k$ (h⁻¹)", value=4.12)
    xa_target = st.slider("Conversão Desejada ($X_A$)", 0.05, 0.95, 0.85)
    
    vr_calc = (qf * xa_target) / (k_val * (1 - xa_target))
    st.metric("Volume Requerido", f"{vr_calc:.2f} m³")

    x_range = np.linspace(0.01, 0.98, 100)
    v_range = (qf * x_range) / (k_val * (1 - x_range))
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.plot(x_range, v_range, 'g-', label="Curva CSTR")
    ax3.scatter([xa_target], [vr_calc], color='red')
    ax3.set_ylim(0, vr_calc * 3)
    ax3.set_xlabel("Conversão"); ax3.set_ylabel("Volume (m³)"); ax3.grid(True, alpha=0.3)
    st.pyplot(fig3)
