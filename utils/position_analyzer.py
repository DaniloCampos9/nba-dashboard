def analisar_perfil_posicional(perfil, stats):
    """
    Analisa a posição base e as estatísticas para determinar 
    o papel tático real e a versatilidade posicional do atleta.
    """
    if not perfil or not stats:
        return {
            "papel": "Especialista de Rotação", 
            "versatilidade": "Padrão", 
            "escopo": "Função fixa dentro do sistema tático."
        }
        
    posicao = str(perfil.get("posicao", "")).upper()
    nome = str(perfil.get("nome_completo", "")).upper()
    
    jogos = stats.get("jogos_disputados", 1)
    if jogos == 0: jogos = 1
    
    apg = stats.get("assistencias_totais", 0) / jogos
    rpg = stats.get("rebotes_totais", 0) / jogos
    ppg = stats.get("pontos_totais", 0) / jogos
    
    # --- NOVAS MÉTRICAS DE PERÍMETRO ---
    fg3a = stats.get("fg3a_totais", 0) / jogos
    fg3m = stats.get("fg3m_totais", 0) / jogos
    pct_3 = (fg3m / fg3a * 100) if fg3a > 0 else 0

    # Casos especiais de elite / Playmakers universais
    if "LEBRON" in nome or "DONCIC" in nome or "JOKIC" in nome or (apg >= 7 and rpg >= 7):
        return {
            "papel": "Primary Playmaker / Point-Forward",
            "posicao_ideal": "Ala / Armador Universal (Posições 1 a 4)",
            "versatilidade": "🌟 Extrema (Domínio absoluto em múltiplas funções)",
            "dominancia": "Capaz de ditar o ritmo da partida, pontuar em alta eficiência e gerenciar o ataque."
        }
    
    # Armadores criadores de jogo
    if "GUARD" in posicao or "G" in posicao:
        if apg >= 6.5:
            return {
                "papel": "Floor General / Guard Criador",
                "posicao_ideal": "Armador (PG) / Combo Guard",
                "versatilidade": "⚡ Alta (cria para si e para os companheiros)",
                "dominancia": "Controla o P&R (Pick and Roll), acha linhas de passe e define nos momentos críticos."
            }
        # NOVO: Filtro de atirador de elite para armadores
        elif fg3a >= 6.0 and pct_3 >= 37.0:
            return {
                "papel": "Perimeter Threat / Sharpshooter",
                "posicao_ideal": "Armador / Ala-Armador (PG / SG)",
                "versatilidade": "🔥 Ofensiva (Gravidade no perímetro)",
                "dominancia": "Volume letal de 3 pontos. Distorce a defesa adversária apenas por estar posicionado na linha de 3."
            }
        else:
            return {
                "papel": "Scoring Guard / Ala-Armador de Impacto",
                "posicao_ideal": "Armador / Ala-Armador (PG / SG)",
                "versatilidade": "Moderada (foco em espaçamento e pontuação)",
                "dominancia": "Especialista em pontuação, transição rápida e pressão ofensiva na bola."
            }
            
    # Alas e Alas-Pivôs
    elif "FORWARD" in posicao or "F" in posicao or "F-C" in posicao:
        if rpg >= 8.5 and apg >= 4:
            return {
                "papel": "Versatile Forward / Forward Dominante",
                "posicao_ideal": "Ala-Pivô Moderno (SF / PF)",
                "versatilidade": "🌟 Extrema (Troca de marcação e puxa contra-ataques)",
                "dominancia": "Mistura força no garrafão com visão de quadra de armador e presença exterior."
            }
        # NOVO: O Verdadeiro 3&D Wing (Volume de 3pts ao invés de apenas pontos gerais)
        elif fg3a >= 4.5 and pct_3 >= 36.0:
            return {
                "papel": "3&D Wing / Elite Spacer",
                "posicao_ideal": "Ala (SF / PF)",
                "versatilidade": "⚡ Sólida (Defesa de perímetro e espaçamento)",
                "dominancia": "Especialista em abrir a quadra (catch-and-shoot) e defender os alas adversários."
            }
        elif ppg >= 18:
            return {
                "papel": "Wing Scorer / Ala Pontuador",
                "posicao_ideal": "Ala (SF) / Ala-Armador (SG)",
                "versatilidade": "⚡ Média-Alta (Ataca iso e atua sem a bola)",
                "dominancia": "Principal válvula de escape ofensiva nas alas, excelente em cortes e infiltrações."
            }
        else:
            return {
                "papel": "System Wing / Ala de Rotação",
                "posicao_ideal": "Ala (SF / PF)",
                "versatilidade": "Funcional",
                "dominancia": "Atua no fluxo da equipe, focando em rebotes longos, cortes e defesa de sistema."
            }
            
    # Pivôs tradicionais ou modernos
    elif "CENTER" in posicao or "C" in posicao:
        if apg >= 5:
            return {
                "papel": "Hub Big / Pivô Distribuidor",
                "posicao_ideal": "Pivô Central (C)",
                "versatilidade": "🌟 Alta (Passador de elite a partir do poste alto)",
                "dominancia": "Atrai dobras no garrafão e pune a defesa com passes cirúrgicos para cortadores."
            }
        # NOVO: O Pivô que arremessa de 3 (Stretch Big)
        elif fg3a >= 3.0 and pct_3 >= 34.0:
            return {
                "papel": "Stretch Big / Pivô Espaçador",
                "posicao_ideal": "Pivô Moderno (C / PF)",
                "versatilidade": "🎯 Tática (Tira o protetor de aro do garrafão)",
                "dominancia": "Arremessa de fora, obrigando o pivô adversário a sair da zona de conforto perto do aro."
            }
        else:
            return {
                "papel": "Rim Protector / Big Man Tradicional",
                "posicao_ideal": "Pivô (C)",
                "versatilidade": "Limitada ao garrafão",
                "dominancia": "Domínio absoluto de rebotes defensivos, proteção de aro e finalizações aéreas (Pick and Roll)."
            }
            
    return {
        "papel": "Rotation Player / Peça de Sistema",
        "posicao_ideal": "Posição Base",
        "versatilidade": "Padrão",
        "dominancia": "Cumpre funções táticas específicas determinadas pela comissão técnica."
    }