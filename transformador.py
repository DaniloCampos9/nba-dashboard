def converter_para_inteiro(valor):
    if valor is None: return None
    return int(float(valor))

def limpar_dados_jogador(dados_brutos):
    bloco_principal = dados_brutos['resultSets'][0]
    headers = bloco_principal['headers']
    valores = bloco_principal['rowSet'][0]
    jogador_completo = dict(zip(headers, valores))
    return {
        "id": jogador_completo.get("PERSON_ID"),
        "nome_completo": jogador_completo.get("DISPLAY_FIRST_LAST"),
        "data_nascimento": jogador_completo.get("BIRTHDATE"),
        "pais": jogador_completo.get("COUNTRY"),
        "altura_pes": jogador_completo.get("HEIGHT"),
        "peso_lbs": converter_para_inteiro(jogador_completo.get("WEIGHT")),
        "camisa": jogador_completo.get("JERSEY"),
        "posicao": jogador_completo.get("POSITION"),
        "time_atual_id": jogador_completo.get("TEAM_ID"),
        "ano_draft": jogador_completo.get("DRAFT_YEAR")
    }

def limpar_estatisticas_carreira(dados_brutos, tipo="Regular Season"):
    indice_bloco = 0 if tipo == "Regular Season" else 2
    try:
        bloco_temporadas = dados_brutos['resultSets'][indice_bloco]
        headers = bloco_temporadas['headers']
        linhas = bloco_temporadas['rowSet']
        lista_temporadas = []
        for linha in linhas:
            temporada = dict(zip(headers, linha))
            lista_temporadas.append({
                "jogador_id": temporada.get("PLAYER_ID"),
                "temporada": temporada.get("SEASON_ID"),
                "tipo_temporada": tipo,
                "time_abrev": temporada.get("TEAM_ABBREVIATION"),
                "idade": converter_para_inteiro(temporada.get("PLAYER_AGE")),
                "jogos_disputados": converter_para_inteiro(temporada.get("GP")),
                "pontos_totais": converter_para_inteiro(temporada.get("PTS")),
                "assistencias_totais": converter_para_inteiro(temporada.get("AST")),
                "rebotes_totais": converter_para_inteiro(temporada.get("REB"))
            })
        return lista_temporadas
    except:
        return []

def limpar_estatisticas_avancadas(dados_brutos, temporada, tipo="Regular Season"):
    headers = dados_brutos['resultSets'][0]['headers']
    linhas = dados_brutos['resultSets'][0]['rowSet']
    lista_avancada = []
    for linha in linhas:
        jogador = dict(zip(headers, linha))
        lista_avancada.append({
            "jogador_id": jogador.get("PLAYER_ID"),
            "temporada": temporada,
            "tipo_temporada": tipo,
            "ts_pct": jogador.get("TS_PCT"),
            "efg_pct": jogador.get("EFG_PCT"),
            "off_rating": jogador.get("OFF_RATING"),
            "def_rating": jogador.get("DEF_RATING"),
            "net_rating": jogador.get("NET_RATING"),
            "usg_pct": jogador.get("USG_PCT"),
            "pie": jogador.get("PIE"),
            "ast_pct": jogador.get("AST_PCT"),
            "ast_tov": jogador.get("AST_TOV"),
            "pace": jogador.get("PACE")
        })
    return lista_avancada

def limpar_estatisticas_hustle(dados_brutos, temporada, tipo="Regular Season"):
    headers = dados_brutos['resultSets'][0]['headers']
    linhas = dados_brutos['resultSets'][0]['rowSet']
    lista_hustle = []
    for linha in linhas:
        jogador = dict(zip(headers, linha))
        lista_hustle.append({
            "jogador_id": jogador.get("PLAYER_ID"),
            "temporada": temporada,
            "tipo_temporada": tipo,
            "deflections": jogador.get("DEFLECTIONS"),
            "charges_drawn": jogador.get("CHARGES_DRAWN"),
            "contested_shots": jogador.get("CONTESTED_SHOTS"),
            "screen_assists": jogador.get("SCREEN_ASSISTS"),
            "loose_balls_recovered": jogador.get("LOOSE_BALLS_RECOVERED")
        })
    return lista_hustle

def criar_perfil_basico_liga(dados_brutos, temporada):
    headers = dados_brutos['resultSets'][0]['headers']
    linhas = dados_brutos['resultSets'][0]['rowSet']
    idx_id = headers.index("PLAYER_ID")
    idx_nome = headers.index("PLAYER_NAME")
    idx_time = headers.index("TEAM_ID") if "TEAM_ID" in headers else None
    
    perfis_basicos = []
    ids_vistos = set()
    for linha in linhas:
        p_id = linha[idx_id]
        if p_id not in ids_vistos:
            ids_vistos.add(p_id)
            perfis_basicos.append({
                "id": p_id,
                "nome_completo": linha[idx_nome],
                "time_atual_id": linha[idx_time] if idx_time is not None else None
            })
    return perfis_basicos

def carregar_defesa_supabase(df_defesa, cliente_supabase):
    registros_sucesso = 0
    for _, linha in df_defesa.iterrows():
        dados = {
            "jogador_id": int(linha['PLAYER_ID']),
            "temporada": linha['temporada'],
            "tipo_temporada": linha['tipo_temporada'],
            "roubos_totais": int(linha['STL']),
            "tocos_totais": int(linha['BLK']),
            "deflections": int(linha['DEFLECTIONS'])
        }
        try:
            cliente_supabase.table("stats_defesa").insert(dados).execute()
            registros_sucesso += 1
        except: pass
    print(f"Defesa: {registros_sucesso} inseridos.")

def carregar_times_supabase(df_times, cliente_supabase):
    registros_sucesso = 0
    for _, linha in df_times.iterrows():
        dados = {
            "time_id": int(linha['TEAM_ID']),
            "nome_time": str(linha['TEAM_NAME']),
            "temporada": str(linha['temporada']),
            "tipo_temporada": str(linha['tipo_temporada']),
            "jogos": int(linha['GP']),
            "vitorias": int(linha['W']),
            "derrotas": int(linha['L']),
            "off_rating": float(linha['OFF_RATING']),
            "def_rating": float(linha['DEF_RATING']),
            "net_rating": float(linha['NET_RATING']),
            "pace": float(linha['PACE'])
        }
        try:
            cliente_supabase.table("stats_times").insert(dados).execute()
            registros_sucesso += 1
        except: pass
    print(f"Times: {registros_sucesso} inseridos.")
    
def limpar_estatisticas_clutch(dados_brutos, temporada, tipo="Regular Season"):
    headers = dados_brutos['resultSets'][0]['headers']
    linhas = dados_brutos['resultSets'][0]['rowSet']
    lista_clutch = []
    
    for linha in linhas:
        jogador = dict(zip(headers, linha))
        lista_clutch.append({
            "jogador_id": jogador.get("PLAYER_ID"),
            "temporada": temporada,
            "tipo_temporada": tipo, # 👉 Adicionamos o tipo aqui também!
            "clutch_pts": jogador.get("PTS"),
            "clutch_fg_pct": jogador.get("FG_PCT"),
            "clutch_3p_pct": jogador.get("FG3_PCT"),
            "clutch_net_rating": jogador.get("PLUS_MINUS"),
            "clutch_usg_pct": jogador.get("USG_PCT")
        })
    return lista_clutch