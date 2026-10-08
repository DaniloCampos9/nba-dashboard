def gerar_scouting_report_dinamico(nome, stats, def_stats, perfil_tatico):
    """
    Motor de regras de negócio que traduz estatísticas avançadas em parágrafos de scouting.
    """
    if not stats:
        return "Dados insuficientes para gerar o relatório de scouting."

    jogos = stats.get("jogos_disputados", 1)
    if jogos == 0: jogos = 1

    # Variáveis base
    usg = (stats.get("usg_pct") or 0) * 100
    ts = (stats.get("ts_pct") or 0) * 100
    net_rtg = stats.get("net_rating") or 0
    
    # Variáveis de Defesa
    defl = def_stats.get("deflections", 0) / jogos if def_stats else 0
    spg = def_stats.get("roubos_totais", 0) / jogos if def_stats else 0
    bpg = def_stats.get("tocos_totais", 0) / jogos if def_stats else 0

    papel = perfil_tatico.get("papel", "Peça de Rotação")

    # --- PARÁGRAFO 1: ATAQUE E VOLUME ---
    p_ataque = f"**Análise Ofensiva:** Atuando primariamente como *{papel}*, {nome} "
    
    if usg >= 28:
        p_ataque += f"assume uma carga massiva do ataque (Usage de {usg:.1f}%), sendo o ponto focal do sistema. "
    elif usg >= 22:
        p_ataque += f"possui alto volume de finalização (Usage de {usg:.1f}%), operando como uma das principais armas ofensivas. "
    elif usg >= 15:
        p_ataque += f"atua dentro do fluxo ofensivo da equipe com volume moderado (Usage de {usg:.1f}%), sem forçar o jogo. "
    else:
        p_ataque += f"tem baixo volume de finalização (Usage de {usg:.1f}%), focando em espaçamento ou em finalizações de alta probabilidade. "

    if ts >= 60:
        p_ataque += f"Sua eficiência é de elite, ostentando um True Shooting de {ts:.1f}%, o que maximiza o valor de cada posse."
    elif ts >= 56:
        p_ataque += f"Ele converte suas chances com eficiência sólida e acima da média (TS% de {ts:.1f}%)."
    else:
        p_ataque += f"No entanto, sofre com a eficiência nos arremessos, registrando um True Shooting de apenas {ts:.1f}% nesta temporada."

    # --- PARÁGRAFO 2: DEFESA E ESFORÇO ---
    p_defesa = "\n\n**Impacto Defensivo:** "
    
    if defl >= 2.5 or spg >= 1.5:
        p_defesa += f"Fora da bola, é um terror nas linhas de passe. Com {defl:.1f} deflections e {spg:.1f} roubos por jogo, ele gera caos e pontos fáceis em transição. "
    elif bpg >= 1.5:
        p_defesa += f"Sua presença protege o aro com maestria ({bpg:.1f} tocos por jogo), alterando arremessos e intimidando infiltrações. "
    elif defl < 1.0 and bpg < 0.5 and spg < 0.8:
        p_defesa += f"Estatisticamente, apresenta baixo volume em métricas de disrupção (roubos e tocos), indicando que atua mais na contenção ou depende do sistema coletivo. "
    else:
        p_defesa += f"Apresenta um esforço defensivo honesto, contribuindo com rotações e contestações dentro do esquema estabelecido. "

    # --- PARÁGRAFO 3: VEREDITO (NET RATING) ---
    p_veredito = "\n\n**Veredito Global:** "
    
    if net_rtg >= 5.0:
        p_veredito += f"Os números confirmam seu impacto positivo: a equipe atropela os adversários com ele em quadra, registrando um formidável Net Rating de +{net_rtg:.1f} a cada 100 posses de bola."
    elif net_rtg >= 1.0:
        p_veredito += f"Ele impacta a vitória. Com ele em quadra, a equipe vence seus minutos (Net Rating de +{net_rtg:.1f})."
    elif net_rtg > -2.0:
        p_veredito += f"Seu impacto de quadra é neutro (Net Rating de {net_rtg:.1f}), com a equipe jogando de igual para igual durante seus minutos."
    else:
        p_veredito += f"A equipe enfrenta dificuldades estruturais durante seus minutos, refletidas em um Net Rating negativo de {net_rtg:.1f} a cada 100 posses."

    return p_ataque + p_defesa + p_veredito