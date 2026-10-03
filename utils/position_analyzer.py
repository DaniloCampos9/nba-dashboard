def analisar_perfil_posicional(perfil, stats):
    """
    Analisa a posição base e as estatísticas (APG, RPG, USG) para determinar 
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

    # Casos especiais de elite / Playmakers universais (ex: LeBron, Jokic, Luka)
    if "LEBRON" in nome or "DONCIC" in nome or "JOKIC" in nome or (apg >= 7 and rpg >= 7):
        return {
            "papel": "Primary Playmaker / Point-Forward",
            "posicao_ideal": "Ala / Armador Universal (Posições 1 a 4)",
            "versatilidade": "🌟 Extrema (Domínio absoluto em múltiplas funções)",
            "dominancia": "Capaz de digitar o ritmo da partida, pontuar em alta eficiência e gerenciar o ataque como armador principal."
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
        else:
            return {
                "papel": "Scoring Guard / Ala-Armador de Impacto",
                "posicao_ideal": "Armador / Ala-Armador (PG / SG)",
                "versatilidade": " Moderada (foco em espaçamento e pontuação)",
                "dominancia": "Especialista em arremessos de perímetro, transição rápida e pressão defensiva na bola."
            }
            
    # Alas e Alas-Pivôs
    elif "FORWARD" in posicao or "F" in posicao or "F-C" in posicao:
        if rpg >= 8.5 and apg >= 4:
            return {
                "papel": "Versatile Forward / Forward Dominante",
                "posicao_ideal": "Ala-Pivô Moderno (SF / PF)",
                "versatilidade": "🌟 Extrema (Troca de marcação em qualquer posição e puxa contra-ataques)",
                "dominancia": "Mistura força no garrafão com visão de quadra de armador e arremesso exterior."
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
                "papel": "3&D Wing / Ala de Sistema",
                "posicao_ideal": "Ala (SF / PF)",
                "versatilidade": "⚡ Sólida (Defesa de perímetro e espaçamento)",
                "dominancia": "Foco total em eficiência sem bola, contestação de arremessos e defesa de alas adversários."
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
        else:
            return {
                "papel": "Rim Protector / Big Man Tradicional",
                "posicao_ideal": "Pivô (C)",
                "versatilidade": " Limitada ao garrafão",
                "dominancia": "Domínio absoluto de rebotes defensivos, proteção de aro e finalizações aéreas (Pick and Roll)."
            }
            
    return {
        "papel": "Rotation Player / Peça de Sistema",
        "posicao_ideal": "Posição Base",
        "versatilidade": "Padrão",
        "dominancia": "Cumpre funções táticas específicas determinadas pela comissão técnica."
    }