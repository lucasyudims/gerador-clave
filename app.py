import streamlit as st
import pandas as pd
import itertools

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Claves", layout="wide")

# ==========================================
# 1. SISTEMA DE LOGIN
# ==========================================

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔒 Acesso Restrito")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        senha = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar"):
            if senha == "clave123":
                st.session_state['autenticado'] = True
                st.rerun() 
            else:
                st.error("Senha incorreta.")
    st.stop() 

# ==========================================
# 2. APLICATIVO PRINCIPAL
# ==========================================

# --- FUNÇÕES LÓGICAS ---

def gerar_vetor_localizacao(vetor_clave):
    vetor_loc = []
    for duracao in vetor_clave:
        vetor_loc.append(1) 
        for _ in range(duracao - 1):
            vetor_loc.append(0) 
    return vetor_loc

def calcular_ns(vetor_v, vetor_t):
    loc_v = gerar_vetor_localizacao(vetor_v)
    loc_t = gerar_vetor_localizacao(vetor_t)
    if len(loc_v) != len(loc_t): return -1
    ns = 0
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

# --- GERADOR DE HTML (ESTILO COMPACTO COM LINHAS VERTICAIS) ---

def gerar_html_tabela(df, divisor_visual):
    # 1. Tabela: width: auto (para não esticar), margin: auto (para centralizar na tela)
    style_table = "width: auto; margin: 0 auto; border-collapse: collapse; font-family: sans-serif; font-size: 14px; color: black; border: 1px solid #ccc;"
    
    # 2. Cabeçalho: Com borda vertical (border-right)
    style_th = "background-color: #f0f2f6; color: black; border-bottom: 2px solid #333; border-right: 1px solid #ccc; padding: 10px 15px; text-align: center;"
    
    html = f'<div style="width:100%; display:flex; justify-content:center;"><table style="{style_table}">'
    
    html += f'''
    <thead>
        <tr>
            <th style="{style_th}">ID</th>
            <th style="{style_th}">Grid Visual</th>
            <th style="{style_th}">Vetor</th>
            <th style="{style_th}">NS</th>
            <th style="{style_th} border-right: none;">Info</th> </tr>
    </thead>
    <tbody>
    '''
    
    for index, row in df.iterrows():
        bg_color = "white"
        if "ORIGINAL" in str(row['Info']): bg_color = "#e6f3ff" 
        elif "Rotação" in str(row['Info']): bg_color = "#f0fff4" 
        
        # Estilo Base da Célula: Com borda vertical e alinhamento central
        style_td_base = "border-bottom: 1px solid #ddd; border-right: 1px solid #ddd; padding: 8px 15px; vertical-align: middle; text-align: center;"
        
        # Última coluna não precisa de borda direita
        style_td_last = "border-bottom: 1px solid #ddd; padding: 8px 15px; vertical-align: middle; text-align: center;"
        
        html += f'<tr style="background-color: {bg_color};">'
        
        # 1. ID
        html += f'<td style="{style_td_base} font-weight: bold; color: #555;">{row["ID"]}</td>'
        
        # 2. GRID VISUAL
        grid_html = '<div style="display: flex; align-items: center; gap: 0px; margin: 0 auto; width: fit-content;">'
        
        vetor_nums = eval(row['Vetor']) 
        vetor_loc = gerar_vetor_localizacao(vetor_nums)
        
        for i, val in enumerate(vetor_loc):
            cor_fundo = "#FF5252" if val == 1 else "white" 
            
            dot_html = ""
            if val == 1:
                dot_html = '<div style="width: 4px; height: 4px; background-color: black; border-radius: 50%;"></div>'

            square_html = f'''
                <div style="
                    width: 12px; height: 12px; 
                    background-color: {cor_fundo}; 
                    border: 1px solid #bbb; 
                    display: flex; justify-content: center; align-items: center;
                    margin-right: 1px;
                ">
                    {dot_html}
                </div>
            '''
            
            line_html = ""
            if (i + 1) % divisor_visual == 0 and (i + 1) != len(vetor_loc):
                line_html = '<div style="width: 2px; height: 16px; background-color: #333; margin: 0 4px;"></div>'
            else:
                line_html = '<div style="width: 2px;"></div>'

            grid_html += f'<div style="display: flex; align-items: center;">{square_html}{line_html}</div>'

        grid_html += '</div>'
        
        # Grid usa o estilo base (com linha vertical separando da próxima coluna)
        html += f'<td style="{style_td_base}">{grid_html}</td>'
        
        # 3. Vetor
        html += f'<td style="{style_td_base} font-family: monospace; font-weight: bold; color: #333; white-space: nowrap;">{row["Vetor"]}</td>'
        
        # 4. NS
        html += f'<td style="{style_td_base} color: #666;">{row["NS"]}</td>'
        
        # 5. Info (Última coluna)
        cor_info = "green" if row['Info'] != "-" else "#ccc"
        weight_info = "bold" if row['Info'] != "-" else "normal"
        html += f'<td style="{style_td_last} color: {cor_info}; font-weight: {weight_info}; font-size: 12px; white-space: nowrap;">{row["Info"]}</td>'
        
        html += '</tr>'
        
    html += '</tbody></table></div>' # Fecha a div centralizadora
    
    return html.replace('\n', '')

# --- INTERFACE VISUAL DO APP ---

st.title("🎹 Gerador de Claves")

with st.sidebar:
    st.header("Configuração")
    entrada_texto = st.text_input("Vetor de Entrada", "3, 3, 4, 2, 4")
    
    st.markdown("---")
    st.subheader("Visualização")
    tipo_compasso = st.radio("Tipo de Compasso (Divisão Visual)", ["Simples (/4)", "Composto (/6)"])
    divisor = 4 if "Simples" in tipo_compasso else 6
    
    try:
        vetor_original = [int(x.strip()) for x in entrada_texto.split(',')]
        total_pulsos = sum(vetor_original)
        st.success(f"Ciclo Total: {total_pulsos} pulsos (semicolcheias)")
    except:
        st.error("Erro: Digite apenas números separados por vírgula.")
        st.stop()
        
    st.markdown("---")
    if st.button("Sair / Logout"):
        st.session_state['autenticado'] = False
        st.rerun()

# --- PROCESSAMENTO ---

rotacoes = gerar_rotacoes(vetor_original)
dados_rot = []
for i, rot in enumerate(rotacoes):
    ns = calcular_ns(vetor_original, rot)
    dados_rot.append({"ID": f"R{i}", "Vetor": str(rot), "NS": ns, "Info": "ORIGINAL" if i == 0 else "-"})
df_rot = pd.DataFrame(dados_rot).sort_values("NS")

perms = gerar_permutacoes_unicas(vetor_original)
dados_perm = []
for i, perm in enumerate(perms):
    l_perm = list(perm)
    ns = calcular_ns(vetor_original, l_perm)
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
                
    dados_perm.append({"ID": f"#{i+1:02d}", "Vetor": str(l_perm), "NS": ns, "Info": match, "ordem": 0 if eh_orig else 1})

df_perm = pd.DataFrame(dados_perm).sort_values(["ordem", "NS"])
df_perm.loc[df_perm['Info'] == ">>> VETOR ORIGINAL <<<", 'ID'] = "ORIG"
df_perm = df_perm.drop(columns=["ordem"])

# --- EXIBIÇÃO ---

aba1, aba2 = st.tabs(["🔄 Rotações Cíclicas", "🔀 Todas Permutações"])

with aba1:
    st.caption("Visualização das rotações do vetor original.")
    html_rot = gerar_html_tabela(df_rot, divisor)
    st.markdown(html_rot, unsafe_allow_html=True)

with aba2:
    st.caption(f"Total de {len(df_perm)} permutações encontradas.")
    html_perm = gerar_html_tabela(df_perm, divisor)
    st.markdown(html_perm, unsafe_allow_html=True)
