import pandas as pd

def calcular_percentil(valor_jogador, lista_todos_valores):
    """Calcula em qual percentil (0 a 100) o jogador está comparado ao resto da liga."""
    if valor_jogador is None or valor_jogador == "N/A" or not lista_todos_valores:
        return None
        
    # Limpa valores vazios da liga
    lista_limpa = [v for v in lista_todos_valores if v is not None]
    if not lista_limpa:
        return None
        
    serie = pd.Series(lista_limpa)
    # Calcula a porcentagem de jogadores que estão abaixo dele
    percentil = round((serie < valor_jogador).mean() * 100)
    return percentil

def gerar_texto_snapshot(usg_percentil, ts_percentil):
    """Gera o texto inteligente baseado no volume (USG%) e eficiência (TS%)."""
    if usg_percentil is None or ts_percentil is None:
        return "Dados insuficientes para gerar a análise de perfil deste jogador."
        
    # Análise de Volume (USG%)
    secao_volume = ""
    if usg_percentil >= 85:
        secao_volume = f"apresenta um **altíssimo volume ofensivo** (USG% no percentil {usg_percentil}), sendo uma das principais opções de ataque da equipe"
    elif usg_percentil >= 65:
        secao_volume = f"possui um **volume ofensivo relevante** (USG% no percentil {usg_percentil}), assumindo boa parte da criação do time"
    elif usg_percentil >= 35:
        secao_volume = f"tem um **papel ofensivo complementar** (USG% no percentil {usg_percentil}), atuando mais dentro do fluxo do sistema"
    else:
        secao_volume = f"possui **baixo volume de finalização** (USG% no percentil {usg_percentil}), focado em funções específicas ou finalizações esporádicas"

    # Análise de Eficiência (TS%)
    secao_eficiencia = ""
    if ts_percentil >= 80:
        secao_eficiencia = f"mantendo uma **eficiência de elite** na pontuação (TS% no percentil {ts_percentil})."
    elif ts_percentil >= 50:
        secao_eficiencia = f"com uma **eficiência acima da média** da liga (TS% no percentil {ts_percentil})."
    elif ts_percentil >= 30:
        secao_eficiencia = f"mas com uma **eficiência abaixo da média** em seus arremessos (TS% no percentil {ts_percentil})."
    else:
        secao_eficiencia = f"sofrendo com **baixa eficiência** na conversão de pontos (TS% no percentil {ts_percentil})."

    return f"Este jogador {secao_volume}, {secao_eficiencia}"

def gerar_tabela_comparativa(stats_jogador, df_liga):
    """Gera o DataFrame comparativo Jogador vs Liga com Percentis formatados."""
    if df_liga.empty or not stats_jogador:
        return pd.DataFrame()

    # Define as métricas que vamos comparar e as colunas correspondentes no df_liga
    metricas = [
        {"nome": "Pontos (PPG)", "coluna": "PPG", "formato": "{:.1f}"},
        {"nome": "Rebotes (RPG)", "coluna": "RPG", "formato": "{:.1f}"},
        {"nome": "Assistências (APG)", "coluna": "APG", "formato": "{:.1f}"},
        {"nome": "True Shooting (TS%)", "coluna": "ts_pct", "formato": "{:.1%}"},
        {"nome": "Usage Rate (USG%)", "coluna": "usg_pct", "formato": "{:.1%}"},
        {"nome": "Net Rating", "coluna": "net_rating", "formato": "{:.1f}"}
    ]
    
    tabela = []
    
    # Vamos precisar calcular o PPG, RPG, APG do jogador de novo aqui rapidinho
    jogos = stats_jogador.get("jogos_disputados", 1)
    valores_jogador = {
        "PPG": stats_jogador.get("pontos_totais", 0) / jogos,
        "RPG": stats_jogador.get("rebotes_totais", 0) / jogos,
        "APG": stats_jogador.get("assistencias_totais", 0) / jogos,
        "ts_pct": stats_jogador.get("ts_pct", 0),
        "usg_pct": stats_jogador.get("usg_pct", 0),
        "net_rating": stats_jogador.get("net_rating", 0)
    }

    for m in metricas:
        col = m["coluna"]
        val_jogador = valores_jogador[col]
        
        # Média da liga
        media_liga = df_liga[col].mean()
        
        # Percentil
        percentil = calcular_percentil(val_jogador, df_liga[col].tolist())
        
        # Formatação bonitinha
        fmt = m["formato"]
        
        tabela.append({
            "Métrica": m["nome"],
            "Jogador": fmt.format(val_jogador) if val_jogador is not None else "N/A",
            "Média da Liga": fmt.format(media_liga),
            "Percentil": f"{percentil}º" if percentil else "N/A"
        })
        
    return pd.DataFrame(tabela)