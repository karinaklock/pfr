import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, quad

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Biblioteca de Reatores - Ka", layout="wide")

# --- ESTILIZAÇÃO CSS (Correção de Visualização) ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; border-radius: 5px; height: 3em; 
        background-color: #007bff; color: white; font-weight: bold; 
    }
    /* Fix para visualização das métricas */
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
    st.title("📚 Biblioteca Interativa de Engenharia Química")
    st.subheader("Selecione um exercício para iniciar a simulação:")
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.info("### Exemplo 4.7: PFR")
        st.write("**Sistema:** Pirólise do Etano")
        if st.button("Abrir PFR"): ir_para('4.7')
        
        st.warning("### Gráfico de Levenspiel")
        st.write("**Conceito:** Comparação PFR vs CSTR")
        if st.button("Abrir Levenspiel"): ir_para('levenspiel')

    with col2:
        st.success("### Exemplo 4.2: CSTR")
        st.write("**Sistema:** Produção de Fenol")
        if st.button("Abrir CSTR"): ir_para('4.2')
        
        st.error("### Exemplo 4.1: Batelada")
        st.write("**Tipo:** Reator de Volume Constante")
        if st.button("Abrir Batelada"): ir_para('4.1')

    with col1: # Ou col2, conforme sua preferência de layout
    st.dark_config("### 💧 Escoamento em Tubos")
    st.write("**Conceito:** Cálculo de Re e Fator de Atrito")
    st.write("Determine o regime de escoamento e visualize sua posição no Diagrama de Moody.")
    if st.button("Abrir Diagrama de Moody"):
        ir_para('moody')

    # No final da seção 'home', adicione:
    st.write("---")
    col_sobre, _ = st.columns([1, 1])
    with col_sobre:
        st.write("### 👩‍🔬 Sobre a Autora")
        st.write("Conheça quem desenvolveu este projeto e acesse materiais complementares.")
        if st.button("Ver Perfil e Contato"):
            ir_para('sobre')

# ==========================================
# EXEMPLO 4.7: PFR (PIRÓLISE DO ETANO)
# ==========================================
elif st.session_state.pagina == '4.7':
    if st.button("⬅️ Voltar"): ir_para('home'); st.rerun()
    st.title("🔥 Exemplo 4.7: Pirólise do Etano (PFR)")
    
    # Parâmetros base do código original
    T = st.sidebar.number_input("Temperatura (K)", value=1050.0)
    P = st.sidebar.number_input("Pressão (atm)", value=1.0)
    Qf = st.sidebar.number_input("Vazão (cm³/s)", value=600.0)
    
    # Cinética baseada no enunciado
    def pfr_model(v, y):
        N_total = max(sum(y), 1e-15)
        Q = (82.06 * T / P) * N_total
        C = y / Q
        # Constantes simplificadas para demonstração
        k = [1e14 * np.exp(-217600/(8.314*T)), 3e14 * np.exp(-165300/(8.314*T)), 3.4e12 * np.exp(-28500/(8.314*T))]
        r = [k[0]*C[0]*C[5], k[1]*C[1], k[2]*C[3]*C[0]] # Simplificado
        return [-r[0]-r[2], r[0]-r[1]+r[2], r[1], r[1]-r[2], r[2], -r[0], r[0]]

    y0 = [0.95*(P*Qf/(82.06*T)), 0, 0, 0, 0, 0.05*(P*Qf/(82.06*T)), 0]
    sol = solve_ivp(pfr_model, (0, 1500), y0, t_eval=np.linspace(0, 1500, 100))

    fig, ax = plt.subplots()
    ax.plot(sol.t, sol.y[0], label="Etano")
    ax.plot(sol.t, sol.y[2], label="Etileno")
    ax.set_xlabel("Volume (cm³)"); ax.set_ylabel("Fluxo (mol/s)"); ax.legend(); st.pyplot(fig)

# ==========================================
# EXEMPLO 4.2: CSTR (FENOL)
# ==========================================
elif st.session_state.pagina == '4.2':
    if st.button("⬅️ Voltar"): ir_para('home'); st.rerun()
    st.title("⚗️ Exemplo 4.2: Produção de Fenol (CSTR)")
    
    qf = st.sidebar.number_input("Vazão (m³/h)", value=26.9)
    k_val = st.sidebar.number_input("k (h⁻¹)", value=4.12)
    xa = st.sidebar.slider("Conversão Alvo", 0.1, 0.95, 0.85)

    vr = (qf * xa) / (k_val * (1 - xa))
    st.metric("Volume do Reator Requerido", f"{vr:.2f} m³")

    x_range = np.linspace(0.01, 0.95, 100)
    v_range = (qf * x_range) / (k_val * (1 - x_range))
    fig2, ax2 = plt.subplots(); ax2.plot(x_range, v_range); ax2.scatter([xa], [vr], color='r'); st.pyplot(fig2)

# ==========================================
# EXEMPLO 4.1: BATELADA
# ==========================================
elif st.session_state.pagina == '4.1':
    if st.button("⬅️ Voltar"): ir_para('home'); st.rerun()
    st.title("⏱️ Exemplo 4.1: Reator em Batelada")
    
    ca0 = st.sidebar.number_input("Ca0 (mol/L)", value=2.0)
    k_b = st.sidebar.number_input("k (min⁻¹)", value=0.1)
    x_alvo = st.sidebar.slider("Conversão Alvo", 0.1, 0.99, 0.90)

    t_final = -np.log(1 - x_alvo) / k_b
    st.metric("Tempo para atingir conversão", f"{t_final:.2f} min")

    t_plot = np.linspace(0, t_final * 1.5, 100)
    ca_plot = ca0 * np.exp(-k_b * t_plot)
    fig3, ax3 = plt.subplots(); ax3.plot(t_plot, ca_plot); st.pyplot(fig3)

# ==========================================
# LEVENSPIEL: PFR VS CSTR
# ==========================================
elif st.session_state.pagina == 'levenspiel':
    if st.button("⬅️ Voltar"): ir_para('home'); st.rerun()
    st.title("📊 Gráfico de Levenspiel")
    
    fa0 = st.sidebar.number_input("Fa0 (mol/h)", value=10.0)
    ca0 = st.sidebar.number_input("Ca0 (mol/L)", value=2.0)
    k_l = st.sidebar.number_input("k", value=0.5)
    ordem = st.sidebar.selectbox("Ordem", [1, 2])
    x_l = st.sidebar.slider("Conversão Desejada", 0.1, 0.95, 0.80)

    def lev_f(x): return fa0 / (k_l * (ca0 * (1 - x))**ordem)

    v_cstr = lev_f(x_l) * x_l
    v_pfr, _ = quad(lev_f, 0, x_l)

    c1, c2 = st.columns(2)
    c1.metric("Volume PFR", f"{v_pfr:.2f} L")
    c2.metric("Volume CSTR", f"{v_cstr:.2f} L")

    x_v = np.linspace(0, x_l + 0.05, 100)
    y_v = [lev_f(xi) for xi in x_v]
    fig4, ax4 = plt.subplots(); ax4.plot(x_v, y_v); ax4.fill_between(x_v[:95], [lev_f(i) for i in x_v[:95]], alpha=0.3); st.pyplot(fig4)

# ==========================================
# PÁGINA: SOBRE MIM
# ==========================================
elif st.session_state.pagina == 'sobre':
    if st.button("⬅️ Voltar para o Menu Principal"):
        ir_para('home')
        st.rerun()

    col_foto, col_texto = st.columns([1, 2])

    with col_foto:
        # Você pode substituir este link pela URL de uma foto sua no GitHub ou LinkedIn
        st.image("https://cdn-icons-png.flaticon.com/512/1995/1995531.png", width=200)

    with col_texto:
        st.title("Olá, eu sou a Ka! 👋")
        st.markdown("""
        Bem-vindo à minha biblioteca interativa de Engenharia Química. 
        Este projeto nasceu da vontade de transformar cálculos complexos de reatores 
        em ferramentas visuais e acessíveis para estudantes e profissionais.
        
        Aqui você encontra simuladores baseados nos maiores clássicos da literatura, 
        como Fogler e Levenspiel, desenvolvidos com Python e integrados ao Google Colab.
        """)
        
        st.write("---")
        st.subheader("📺 Acompanhe meu conteúdo")
        st.write("No meu canal do YouTube, eu explico os conceitos por trás desses simuladores e resolvo exercícios passo a passo.")
        
        # Botão estilizado para o YouTube
        st.video("https://www.youtube.com/@karinakc") # Mostra o vídeo mais recente ou o canal
        st.link_button("Ir para o Canal no YouTube", "https://www.youtube.com/@karinakc", type="primary")

    st.sidebar.info("Acesse o canal para tutoriais de Python e Engenharia Química.")

elif st.session_state.pagina == 'moody':
    if st.button("⬅️ Voltar"):
        ir_para('home')
        st.rerun()

    st.title("📉 Diagrama de Moody Interativo")

    # --- SIDEBAR: ENTRADAS ---
    st.sidebar.header("📋 Dados da Tubulação")
    vazao = st.sidebar.number_input("Vazão (m³/h)", value=10.0)
    diametro_mm = st.sidebar.number_input("Diâmetro Interno (mm)", value=50.0)
    rugosidade_mm = st.sidebar.number_input("Rugosidade absoluta ε (mm)", value=0.045, format="%.4f")
    
    st.sidebar.header("🧪 Propriedades (Água @ 20°C)")
    rho = st.sidebar.number_input("Densidade (kg/m³)", value=998.0)
    mu = st.sidebar.number_input("Viscosidade Dinâmica (Pa·s)", value=0.001, format="%.4f")

    # --- CÁLCULOS ---
    # Convertendo unidades
    Q = vazao / 3600 # m³/s
    D = diametro_mm / 1000 # m
    area = np.pi * (D**2) / 4
    v = Q / area # m/s
    
    re = (rho * v * D) / mu
    rr = rugosidade_mm / diametro_mm # Rugosidade relativa

    # Cálculo do Fator de Atrito (Swamee-Jain para Re > 4000)
    if re > 4000:
        f = 0.25 / (np.log10((rr / 3.7) + (5.74 / (re**0.9))))**2
    elif re > 0:
        f = 64 / re # Escoamento Laminar
    else:
        f = 0

    # --- EXIBIÇÃO DE RESULTADOS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Reynolds (Re)", f"{re:.0f}")
    c2.metric("Regime", "Turbulento" if re > 4000 else "Laminar" if re < 2000 else "Transição")
    c3.metric("Fator de Atrito (f)", f"{f:.4f}")

    # --- PLOTAGEM DO GRÁFICO ---
    st.subheader("Posicionamento no Diagrama de Moody")
    fig5, ax5 = plt.subplots(figsize=(10, 6))

    # Desenhar Curvas de Rugosidade Relativa (Fundo do Gráfico)
    re_plot = np.logspace(3, 8, 500)
    # Rugosidades padrão para as linhas de fundo
    for eps_r in [0, 1e-6, 1e-5, 1e-4, 1e-3, 0.01, 0.05]:
        f_plot = [0.25 / (np.log10((eps_r / 3.7) + (5.74 / (r**0.9))))**2 if r > 2000 else 64/r for r in re_plot]
        ax5.plot(re_plot, f_plot, color='gray', alpha=0.2, linewidth=0.5)

    # Linha do Escoamento Laminar (64/Re)
    re_lam = np.logspace(2.8, 3.3, 20)
    ax5.plot(re_lam, 64/re_lam, color='blue', label='Laminar (64/Re)')

    # SOBREPOSIÇÃO: PONTO DO USUÁRIO
    if re > 0:
        ax5.scatter([re], [f], color='red', s=100, zorder=5, label='Sua Condição', marker='*')
        ax5.annotate(f"  f={f:.4f}", (re, f), color='red', fontweight='bold')

    ax5.set_xscale('log')
    ax5.set_yscale('log')
    ax5.set_xlabel('Número de Reynolds (Re)')
    ax5.set_ylabel('Fator de Atrito (f)')
    ax5.set_xlim(1e3, 1e8)
    ax5.set_ylim(0.008, 0.1)
    ax5.grid(True, which='both', linestyle='--', alpha=0.5)
    ax5.legend()
    st.pyplot(fig5)
