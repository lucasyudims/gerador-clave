import streamlit as st
import pandas as pd
import itertools

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Claves", layout="wide")

# CSS para garantir que a tabela fique bonita e alinhada
st.markdown("""
<style>
    table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px; }
    th { background-color: #f0f2f6; border-bottom: 2px solid #333; padding: 10px; text-align: left; }
    td { border-bottom: 1px solid #ddd; padding: 8px; vertical-align: middle; }
    .grid-container { display: flex; align-items: center; gap: 0px; }
    .beat-wrapper { display: flex; align-items: center; height: 20px; padding-right: 4px; margin-right: 2px; }
    .square { width: 12px; height: 12px; border: 1px solid #bbb; display: flex; justify-content: center; align-items: center; }
    .dot { width: 6px; height: 6px; background-color: black; border-radius: 50%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SISTEMA DE LOGIN (Session State)
# ==========================================

# Inicializa o estado de autenticação se não existir
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Se NÃO estiver autenticado, mostra apenas a tela de login
if not st.session_state['autenticado']:
    st.title("🔒 Acesso Restrito")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        senha = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar"):
            if senha == "clave123":
                st.session_state['autenticado'] = True
                st.rerun() # Recarrega a página para esconder o login
            else:
                st.error("Senha incorreta.")
    
    st.stop() # Para a execução do código aqui se não estiver logado

# ==========================================
# 2. APLICATIVO PRINCIPAL (Só roda se logado)
# ==========================================

# --- FUNÇÕES LÓGICAS ---

def gerar_vetor_localizacao(vetor_clave):
    # 1 unidade = 1 pulso (Semicolcheia)
    vetor_loc = []
    for duracao in vetor_clave:
        vetor_loc.append(1) # Ataque
        for _ in range(duracao - 1):
            vetor_loc.append(0) # Sustentação
    return vetor_loc

def calcular_ns(vetor_v, vetor_t):
    loc_v = gerar_vetor_localizacao(vetor_v)
    loc_t = gerar_vetor_localizacao(vetor_t)
    ns = 0
    # Compara pulso a pulso. Se V tem ataque (1) e T não tem, conta NS.
    # Nota: Assumimos vetores de mesmo tamanho total.
    if len(loc_v) != len(loc_t): return -1
    
    for i in range(len(loc_v)):
        if loc_v[i] == 1 and loc_t[i] != 1:
            ns += 1
    return ns

def gerar_rotacoes(vetor):
    todas_rot = []
    n = len(vetor)
    for i in range(n):
        nova_rot = vetor[i:] + vetor[:i]
        todas_rot.append(nova_rot)
    return todas_rot

def gerar_permutacoes_unicas(vetor):
    todas = itertools.permutations(vetor)
    unicas = list(set(todas))
    unicas.sort()
    return unicas

# --- GERADOR DE HTML DA TABELA ---

def gerar_html_tabela(df, divisor_visual):
    """
    Cria uma string HTML pura para renderizar a tabela com o Grid Visual.
    """
    html = '<table>'
    
    # Cabeçalho
    html += '''
    <thead>
        <tr>
            <th style="width: 50px;">ID</th>
            <th>Grid Visual</th>
            <th style="text-align: center;">Vetor</th>
            <th style="text-align: center;">NS</th>
            <th>Info</th>
        </tr>
    </thead>
    <tbody>
    '''
    
    for index, row in df.iterrows():
        bg_color = "white"
        # Destaca linhas especiais
        if "ORIGINAL" in str(row['Info']): bg_color = "#e6f3ff" # Azul claro
        elif "Rotação" in str(row['Info']): bg_color = "#f0fff4" # Verde claro
        
        html += f'<tr style="background-color: {bg_color};">'
        
        # Coluna ID
        html += f'<td style="font-weight: bold; color: #555;">{row["ID"]}</td>'
        
        # Coluna GRID VISUAL
        grid_html = '<div class="grid-container">'
        
        # Converte string de volta para lista para processar
        vetor_nums = eval(row['Vetor']) 
        vetor_loc = gerar_vetor_localizacao(vetor_nums)
        
        for i, val in enumerate(vetor_loc):
            # Lógica de Estilo do Quadrado
            cor_fundo = "#ffcccc" if val == 1 else "white" # Vermelho claro se ataque
            dot_html = '<div class="dot"></div>' if val == 1 else ""
            
            # Lógica da Linha Divisória
            # Se for múltiplo do divisor (4 ou 6) e não for o último, adiciona borda direita
            style_wrapper = ""
            if (i + 1) % divisor_visual == 0 and (i + 1) != len(vetor_loc):
                style_wrapper = "border-right: 2px solid #333;" # Linha grossa
            
            grid_html += f'''
            <div class="beat-wrapper" style="{style_wrapper}">
                <div class="square" style="background-color: {cor_fundo};">
                    {dot_html}
                </div>
            </div>
            '''
        grid_html += '</div>'
        
        html += f'<td>{grid_html}</td>'
        
        # Outras Colunas
        html += f'<td style="text-align: center; font-family: monospace; font-weight: bold;">{row["Vetor"]}</td>'
        html += f'<td style="text-align: center; color: #666;">{row["NS"]}</td>'
        
        cor_info = "green" if row['Info'] != "-" else "#ccc"
        weight_info = "bold" if row['Info'] != "-" else "normal"
        html += f'<td style="color: {cor_info}; font-weight: {weight_info}; font-size: 12px;">{row["Info"]}</td>'
        
        html += '</tr>'
        
    html += '</tbody></table>'
    return html

# --- INTERFACE VISUAL DO APP ---

st.title("🎹 Gerador de Claves")

# Barra Lateral
with st.sidebar:
    st.header("Configuração")
    entrada_texto = st.text_input("Vetor de Entrada", "3, 3, 4, 2, 4")
    
    st.markdown("---")
    st.subheader("Visualização")
    # Seletor de Compasso (Simples ou Composto)
    tipo_compasso = st.radio("Tipo de Compasso (Divisão Visual)", ["Simples (/4)", "Composto (/6)"])
    divisor = 4 if "Simples" in tipo_compasso else 6
    
    # Processamento inicial do input
    try:
        vetor_original = [int(x.strip()) for x in entrada_texto.split(',')]
        total_pulsos = sum(vetor_original)
        st.success(f"Ciclo Total: {total_pulsos} pulsos (semicolcheias)")
    except:
        st.error("Erro: Digite apenas números separados por vírgula.")
        st.stop()
        
    # Botão de Logout
    st.markdown("---")
    if st.button("Sair / Logout"):
        st.session_state['autenticado'] = False
        st.rerun()

# --- PROCESSAMENTO DOS DADOS ---

# 1. Rotações
rotacoes = gerar_rotacoes(vetor_original)
dados_rot = []
for i, rot in enumerate(rotacoes):
    ns = calcular_ns(vetor_original, rot)
    dados_rot.append({
        "ID": f"R{i}", 
        "Vetor": str(rot), 
        "NS": ns, 
        "Info": "ORIGINAL" if i == 0 else "-"
    })
df_rot = pd.DataFrame(dados_rot).sort_values("NS")

# 2. Permutações
perms = gerar_permutacoes_unicas(vetor_original)
dados_perm = []
for i, perm in enumerate(perms):
    l_perm = list(perm)
    ns = calcular_ns(vetor_original, l_perm)
    
    # Verifica se é uma rotação disfarçada
    match = "-"
    eh_orig = False
    if l_perm == vetor_original:
        match = ">>> VETOR ORIGINAL <<<"
        eh_orig = True
    else:
        for idx_rot, rot_existente in enumerate(rotacoes):
            if l_perm == rot_existente:
                match = f"Rotação {idx_rot}"
                break
                
    dados_perm.append({
        "ID": f"#{i+1:02d}", 
        "Vetor": str(l_perm), 
        "NS": ns, 
        "Info": match,
        "ordem": 0 if eh_orig else 1
    })

df_perm = pd.DataFrame(dados_perm).sort_values(["ordem", "NS"])
# Ajuste visual do ID original
df_perm.loc[df_perm['Info'] == ">>> VETOR ORIGINAL <<<", 'ID'] = "ORIG"
df_perm = df_perm.drop(columns=["ordem"])

# --- EXIBIÇÃO NAS ABAS ---

aba1, aba2 = st.tabs(["🔄 Rotações Cíclicas", "🔀 Todas Permutações"])

with aba1:
    st.caption("Visualização das rotações do vetor original.")
    # Aqui está o segredo: unsafe_allow_html=True permite renderizar as DIVs coloridas
    html_rot = gerar_html_tabela(df_rot, divisor)
    st.markdown(html_rot, unsafe_allow_html=True)

with aba2:
    st.caption(f"Total de {len(df_perm)} permutações encontradas.")
    html_perm = gerar_html_tabela(df_perm, divisor)
    st.markdown(html_perm, unsafe_allow_html=True)