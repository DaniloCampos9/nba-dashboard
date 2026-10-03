def classificar_arquetipo(stats, def_stats):
    """
    Analisa os dados de ataque e defesa e classifica o jogador em um arquétipo do NBA 2K.
    A ordem dos IFs importa! Os mais raros/difíceis ficam no topo.
    """
    if not stats:
        return None

    # Normalizar dados (Per Game e Porcentagens)
    jogos = stats.get('jogos_disputados', 1)
    if jogos == 0: jogos = 1
    
    ppg = stats.get('pontos_totais', 0) / jogos
    rpg = stats.get('rebotes_totais', 0) / jogos
    apg = stats.get('assistencias_totais', 0) / jogos
    usg = (stats.get('usg_pct') or 0) * 100
    ts = (stats.get('ts_pct') or 0) * 100
    ast_pct = (stats.get('ast_pct') or 0) * 100

    spg = def_stats.get('roubos_totais', 0) / jogos if def_stats else 0
    bpg = def_stats.get('tocos_totais', 0) / jogos if def_stats else 0
    defl = def_stats.get('deflections', 0) / jogos if def_stats else 0

    # 1. Superstar / Franchise Player
    if ppg >= 26 and usg >= 28:
        return {
            "nome": "Franchise Cornerstone", "icone": "👑", 
            "cor": "linear-gradient(135deg, #FFD700, #FDB931)", 
            "desc": "A estrela máxima. Carrega o ataque nas costas com altíssimo volume e atrai toda a atenção da defesa."
        }

    # 2. Maestro / Playmaker Mágico
    if apg >= 8 and ast_pct >= 35:
        return {
            "nome": "Floor General", "icone": "🧠", 
            "cor": "linear-gradient(135deg, #00C9FF, #92FE9D)", 
            "desc": "O maestro do time. Controla o ritmo do jogo, lê a defesa e é o motor que faz o sistema funcionar."
        }

    # 3. Monstro dos Dois Lados da Quadra
    if ppg >= 20 and (spg >= 1.5 or bpg >= 1.2 or defl >= 2.5):
        return {
            "nome": "Two-Way Star", "icone": "🦅", 
            "cor": "linear-gradient(135deg, #f12711, #f5af19)", 
            "desc": "Elite nos dois lados da quadra. Pontua em alto volume no ataque e destrói posses adversárias na defesa."
        }

    # 4. Protetor de Aro Dominante
    if rpg >= 10 and bpg >= 1.5:
        return {
            "nome": "Paint Beast", "icone": "🧱", 
            "cor": "linear-gradient(135deg, #3a7bd5, #3a6073)", 
            "desc": "O dono do garrafão. Domina a tábua de rebotes e protege o aro, alterando os arremessos adversários."
        }

    # 5. Cestinha / Microondas
    if ppg >= 15 and usg >= 25 and apg < 5:
        return {
            "nome": "Pure Bucket", "icone": "🔥", 
            "cor": "linear-gradient(135deg, #FF416C, #FF4B2B)", 
            "desc": "Pontuador nato. Especialista em criar o próprio arremesso, isolar (ISO) e castigar defesas."
        }

    # 6. Atirador de Elite / 3&D
    if ts >= 60 and usg <= 20 and ppg >= 10:
        return {
            "nome": "Elite Sniper", "icone": "🎯", 
            "cor": "linear-gradient(135deg, #11998e, #38ef7d)", 
            "desc": "Baixo uso de bola, mas altíssima eficiência. Pega a bola para definir e pune as dobras nos astros do time."
        }

    # 7. Faz-Tudo
    if ppg >= 12 and rpg >= 6 and apg >= 4:
        return {
            "nome": "Swiss Army Knife", "icone": "🛠️", 
            "cor": "linear-gradient(135deg, #8E2DE2, #4A00E0)", 
            "desc": "O canivete suíço. Faz de tudo um pouco com versatilidade pura para preencher qualquer buraco tático."
        }

    # 8. Carrapato Defensivo
    if (spg >= 1.5 or defl >= 2.5) and usg <= 18:
        return {
            "nome": "Lockdown Defender", "icone": "🔒", 
            "cor": "linear-gradient(135deg, #333333, #dd1818)", 
            "desc": "Especialista defensivo. Sua principal função é infernizar e anular a principal arma ofensiva adversária."
        }

    # 9. A Cola do Time
    if stats.get('net_rating', 0) >= 3.0 and usg <= 16:
        return {
            "nome": "Glue Guy", "icone": "🧩", 
            "cor": "linear-gradient(135deg, #56ab2f, #a8e063)", 
            "desc": "A cola do time. Não precisa tocar na bola para impactar positivamente; focado nos detalhes que vencem jogos."
        }

    # 10. Base da Rotação
    return {
        "nome": "System Player", "icone": "⚙️", 
        "cor": "linear-gradient(135deg, #4b6cb7, #182848)", 
        "desc": "Peça de rotação sólida que cumpre sua função dentro do esquema tático estabelecido."
    }