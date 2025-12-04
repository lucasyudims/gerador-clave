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

# --- GERADORES DE HTML E CSS ---

def criar_grid_html_celula(vetor_nums, divisor_visual):
    """
    Função auxiliar que cria APENAS o HTML dos quadradinhos.
    Usada tanto na tabela simples quanto na tabela dupla.
    """
    vetor_loc = gerar_vetor_localizacao(vetor_nums)
    grid_html = '<div style="display: flex; align-items: center; gap: 0px; margin: 0 auto; width: fit-content;">'
    
    for i, val in enumerate(vetor_loc):
        cor_fundo = "#FF5252" if val == 1 else "white"
        dot_html = '<div style="width: 4px; height: 4px; background-color: black; border-radius: 50%;"></div>' if val == 1 else ""

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
        
        line_html = '<div style="width: 2px;"></div>'
        if (i + 1) % divisor_visual == 0 and (i + 1) != len(vetor_loc):
            line_html = '<div style="width: 2px; height: 16px; background-color: #333; margin: 0 4px;"></div>'

        grid_html += f'<div style="display: flex; align-items: center;">{square_html}{line_html}</div>'

    grid_html += '</div>'
    return grid_html

def gerar_html_tabela_padrao(df, divisor_visual):
    # Estilos
    style_table = "width: auto; margin: 0 auto; border-collapse: collapse; font-family: sans-serif; font-size: 14px; color: black; border: 1px solid #ccc;"
    style_th = "background-color: #f0f2f6; color: black; border-bottom: 2px solid #333; border-right: 1px solid #ccc; padding: 10px 15px; text-align: center;"
    style_td = "border-bottom: 1px solid #ddd; border-right: 1px solid #ddd; padding: 8px 15px; vertical-align: middle; text-align: center;"
    
    html = f'<div style="width:100%; display:flex; justify-content:center;"><table style="{style_table}">'
    html += f'''<thead><tr>
            <th style="{style_th}">ID</th>
            <th style="{style_th}">Grid Visual</th>
            <th style="{style_th}">Vetor</th>
            <th style="{style_th}">NS</th>
            <th style="{style_th} border-right: none;">Info</th>
        </tr></thead><tbody>'''
    
    for index, row in df.iterrows():
        bg_color = "white"
        if "ORIGINAL" in str(row['Info']): bg_color = "#e6f3ff"
        elif "Rotação" in str(row['Info']): bg_color = "#f0fff4"
        
        vetor_nums = eval(row['Vetor'])
        grid = criar_grid_html_celula(vetor_nums, divisor_visual)
        
        html += f'<tr style="background-color: {bg_color};">'
        html += f'<td style="{style_td} font-weight: bold; color: #555;">{row["ID"]}</td>'
        html += f'<td style="{style_td} padding: 4px 2px;">{grid}</td>'
        html += f'<td style="{style_td} font-family: monospace; font-weight: bold; color: #333; white-space: nowrap;">{row["Vetor"]}</td>'
        html += f'<td style="{style_td} color: #666;">{row["NS"]}</td>'
        
        # Info Colorida
        info_txt = str(row['Info'])
        cor_info = "#666"
        if "ORIGINAL" in info_txt: cor_info = "green"
        elif "Rotação" in info_txt: cor_info = "#2e7d32"
        elif "Inv." in info_txt: cor_info = "#d84315" # Laranja escuro para inversões
        
        html += f'<td style="border-bottom: 1px solid #ddd; padding: 8px 15px; text-align: center; color: {cor_info}; font-size: 12px; white-space: nowrap;">{info_txt}</td>'
        html += '</tr>'
        
    html += '</tbody></table></div>'
    return html.replace('\n', '')

def gerar_html_tabela_pares(pares, divisor_visual):
    """
    Gera a tabela da aba Inversões com colunas duplas.
    """
    style_table = "width: auto; margin: 0 auto; border-collapse: collapse; font-family: sans-serif; font-size: 13px; color: black; border: 1px solid #ccc;"
    style_th = "background-color: #f0f2f6; color: black; border-bottom: 2px solid #333; border-right: 1px solid #ccc; padding: 8px; text-align: center;"
    style_td = "border-bottom: 1px solid #ddd; border-right: 1px solid #ddd; padding: 6px 10px; vertical-align: middle; text-align: center;"
    style_sep = "border-bottom: 1px solid #ddd; border-right: 2px solid #333; padding: 6px 10px; vertical-align: middle; text-align: center; background-color: #f9f9f9;" # Separador central

    html = f'<div style="width:100%; display:flex; justify-content:center;"><table style="{style_table}">'
    
    # Cabeçalho Duplo
    html += f'''<thead>
        <tr>
            <th style="{style_th} background-color: #e3f2fd;">ID Par</th>
            <th style="{style_th} background-color: #e3f2fd;">Info (Orig/Rot)</th>
            
            <th style="{style_th}">Grid (Forma A)</th>
            <th style="{style_th}">Vetor A</th>
            <th style="{style_sep}">NS</th>
            
            <th style="{style_th}">Grid (Inversão B)</th>
            <th style="{style_th}">Vetor B</th>
            <th style="{style_th} border-right: none;">NS</th>
        </tr></thead><tbody>'''

    for p in pares:
        vetor_a = p['vetor_a']
        vetor_b = p['vetor_b']
        
        grid_a = criar_grid_html_celula(vetor_a, divisor_visual)
        grid_b = criar_grid_html_celula(vetor_b, divisor_visual)
        
        html += '<tr>'
        html += f'<td style="{style_td} font-weight: bold;">{p["id_combinado"]}</td>'
        
        # Info
        cor_info = "green" if "Rot" in p["info"] or "ORIGINAL" in p["info"] else "#999"
        html += f'<td style="{style_td} color: {cor_info}; font-weight: bold;">{p["info"]}</td>'
        
        # Lado A
        html += f'<td style="{style_td} padding: 4px;">{grid_a}</td>'
        html += f'<td style="{style_td} font-family: monospace;">{str(vetor_a)}</td>'
        html += f'<td style="{style_sep} color: #666;">{p["ns_a"]}</td>'
        
        # Lado B
        html += f'<td style="{style_td} padding: 4px;">{grid_b}</td>'
        html += f'<td style="{style_td} font-family: monospace;">{str(vetor_b)}</td>'
        html += f'<td style="border-bottom: 1px solid #ddd; padding: 6px 10px; text-align: center; color: #666;">{p["ns_b"]}</td>'
        
        html += '</tr>'

    html += '</tbody></table></div>'
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
        st.success(f"Ciclo Total: {total_pulsos} pulsos")
    except:
        st.error("Erro no vetor.")
        st.stop()
        
    st.markdown("---")
    if st.button("Sair / Logout"):
        st.session_state['autenticado'] = False
        st.rerun()

# --- PROCESSAMENTO ---

# 1. Dados Básicos
rotacoes = gerar_rotacoes(vetor_original)
perms_unicas = gerar_permutacoes_unicas(vetor_original)

# 2. Processamento de Rotações (Aba 1)
dados_rot = []
for i, rot in enumerate(rotacoes):
    ns = calcular_ns(vetor_original, rot)
    
    # Verifica Inversão dentro das Rotações
    rot_inv = rot[::-1] # Inverso desta rotação
    info_extra = ""
    
    # Procura se o inverso é alguma outra rotação
    if rot_inv in rotacoes:
        idx_inv = rotacoes.index(rot_inv)
        if idx_inv != i:
            info_extra = f" / Inv. Rot {idx_inv}"
        else:
            info_extra = " (Palíndromo)"
            
    base_info = "ORIGINAL" if i == 0 else "-"
    full_info = base_info + (info_extra if info_extra else "")
    
    dados_rot.append({"ID": f"R{i}", "Vetor": str(rot), "NS": ns, "Info": full_info})

df_rot = pd.DataFrame(dados_rot).sort_values("NS")

# 3. Processamento de Permutações (Aba 2)
# Vamos criar uma lista de objetos primeiro para facilitar buscas
lista_perm_objs = []
for i, perm in enumerate(perms_unicas):
    l_perm = list(perm)
    lista_perm_objs.append({
        "idx": i,
        "vetor": l_perm,
        "ns": calcular_ns(vetor_original, l_perm),
        "id_str": f"#{i+1:02d}"
    })

dados_perm = []
for p in lista_perm_objs:
    vetor_atual = p['vetor']
    info_parts = []
    
    # A. É Rotação?
    if vetor_atual == vetor_original:
        info_parts.append("ORIGINAL")
    elif vetor_atual in rotacoes:
        info_parts.append(f"Rotação {rotacoes.index(vetor_atual)}")
        
    # B. É Inversão de alguém?
    vetor_inv = vetor_atual[::-1]
    
    # Procura o índice do inverso na lista de permutações
    # (Isso é um pouco custoso O(N^2), mas ok para vetores pequenos)
    idx_inv_perm = -1
    for cand in lista_perm_objs:
        if cand['vetor'] == vetor_inv:
            idx_inv_perm = cand['idx']
            break
            
    if idx_inv_perm != -1:
        # Se for ele mesmo, é palíndromo
        if idx_inv_perm == p['idx']:
            # Só marcamos palíndromo se não for rotação (para não poluir)
            # ou podemos adicionar " (Palíndromo)"
            pass 
        else:
            # É inverso de outra permutação
            # Verificamos se esse inverso é uma rotação conhecida
            if vetor_inv in rotacoes:
                idx_rot_inv = rotacoes.index(vetor_inv)
                info_parts.append(f"Inv. de Rot {idx_rot_inv}")
            else:
                info_parts.append(f"Inv. de #{idx_inv_perm+1:02d}")

    str_info = " / ".join(info_parts) if info_parts else "-"
    
    dados_perm.append({
        "ID": p['id_str'],
        "Vetor": str(vetor_atual),
        "NS": p['ns'],
        "Info": str_info,
        "ordem": 0 if vetor_atual == vetor_original else 1
    })

df_perm = pd.DataFrame(dados_perm).sort_values(["ordem", "NS"])
if "ORIGINAL" in str(df_perm.iloc[0]['Info']):
    df_perm.iloc[0, df_perm.columns.get_loc('ID')] = "ORIG"
df_perm = df_perm.drop(columns=["ordem"])

# 4. Processamento da Aba Inversões (Aba 3)
# Lógica: Agrupar pares (A, Inverso de A)
ids_processados = set()
pares_inversoes = []

# Usamos a lista ordenada por NS (df_perm) para manter a ordem lógica visual
for index, row in df_perm.iterrows():
    vec_str = row['Vetor']
    vec_lista = eval(vec_str)
    vec_inv = vec_lista[::-1]
    
    # Acha o ID e NS do inverso
    # Precisamos encontrar o objeto correspondente ao inverso
    obj_inv = next((item for item in dados_perm if item["Vetor"] == str(vec_inv)), None)
    
    id_curr = row['ID']
    id_inv = obj_inv['ID']
    
    # Cria uma chave única para o par (ordem alfabética para evitar duplicatas A-B e B-A)
    ids = sorted([id_curr, id_inv])
    chave_par = f"{ids[0]}-{ids[1]}"
    
    if chave_par not in ids_processados:
        ids_processados.add(chave_par)
        
        # Identificação da Info (Prioriza Rotações)
        info_par = "-"
        if vec_lista in rotacoes:
            info_par = f"Rotação {rotacoes.index(vec_lista)}"
            if vec_lista == vetor_original: info_par = "VETOR ORIGINAL"
        elif vec_inv in rotacoes:
            info_par = f"Inv. de Rot {rotacoes.index(vec_inv)}"
            
        pares_inversoes.append({
            "id_combinado": f"{id_curr} / {id_inv}",
            "vetor_a": vec_lista,
            "ns_a": row['NS'],
            "vetor_b": vec_inv,
            "ns_b": obj_inv['NS'],
            "info": info_par
        })

# --- EXIBIÇÃO ---

aba1, aba2, aba3 = st.tabs(["🔄 Rotações", "🔀 Permutações", "mirror Inversões (Pares)"])

with aba1:
    st.caption("Rotações e suas relações de inversão.")
    st.write(gerar_html_tabela_padrao(df_rot, divisor), unsafe_allow_html=True)

with aba2:
    st.caption("Todas as permutações com identificação de inversões cruzadas.")
    st.write(gerar_html_tabela_padrao(df_perm, divisor), unsafe_allow_html=True)

with aba3:
    st.caption("Visualização lado a lado: Vetor e seu Retrógrado (Inversão).")
    st.write(gerar_html_tabela_pares(pares_inversoes, divisor), unsafe_allow_html=True)
