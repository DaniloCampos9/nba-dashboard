def classificar_arquetipo(stats, def_stats):
    """
    Analisa os dados de ataque, defesa e eficiência para classificar 
    o jogador em um arquétipo dinâmico da NBA moderna.
    A ordem importa: os mais dominantes/raros estão no topo.
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
    net_rtg = stats.get('net_rating') or 0
    
    fg3a = stats.get('fg3a_totais', 0) / jogos
    fg3m = stats.get('fg3m_totais', 0) / jogos
    pct_3pt = (fg3m / fg3a * 100) if fg3a > 0 else 0

    spg = def_stats.get('roubos_totais', 0) / jogos if def_stats else 0
    bpg = def_stats.get('tocos_totais', 0) / jogos if def_stats else 0
    defl = def_stats.get('deflections', 0) / jogos if def_stats else 0

    # ==========================================
    # TIER 1: SUPERSTARS E MOTORES OFENSIVOS
    # ==========================================
    
# 1A. Franchise Playmaker (Luka Doncic, Nikola Jokic)
    if ppg >= 24 and usg >= 28 and apg >= 7.5:
        return {
            "nome": "Franchise Playmaker", "icone": "🪄", 
            "cor": "linear-gradient(135deg, #FFD700, #FDB931)", 
            "desc": "O sistema ofensivo inteiro. Carrega a pontuação em altíssimo volume e atua simultaneamente como o principal maestro da equipe."
        }

    # 1B. Franchise Anchor (Joel Embiid, Giannis Antetokounmpo)
    if ppg >= 25 and usg >= 28 and rpg >= 10:
        return {
            "nome": "Franchise Anchor", "icone": "🦍", 
            "cor": "linear-gradient(135deg, #FFD700, #FDB931)", 
            "desc": "Força física e técnica imparável. Domina as tábuas de rebote, atrai marcação dupla constante e castiga defesas como a âncora da franquia."
        }

    # 1C. Franchise Scorer (Shai Gilgeous-Alexander, Kevin Durant, Jayson Tatum)
    if ppg >= 26 and usg >= 28:
        return {
            "nome": "Franchise Scorer", "icone": "👑", 
            "cor": "linear-gradient(135deg, #FFD700, #FDB931)", 
            "desc": "A primeira opção ofensiva indiscutível. Um pontuador letal, capaz de criar o próprio arremesso e destruir defesas em qualquer nível da quadra."
        }

    # 2. Offensive Engine (LaMelo Ball, Trae Young, Haliburton)
    if ppg >= 20 and apg >= 7:
        return {
            "nome": "Offensive Engine", "icone": "🏎️", 
            "cor": "linear-gradient(135deg, #FF512F, #DD2476)", 
            "desc": "O motor do ataque. Gera um volume absurdo de pontos por conta própria e criando para os companheiros."
        }

    # 3. Two-Way Star (Tatum, SGA, Edwards)
    if ppg >= 22 and (spg >= 1.3 or bpg >= 1.0 or defl >= 2.5):
        return {
            "nome": "Two-Way Star", "icone": "🦅", 
            "cor": "linear-gradient(135deg, #f12711, #f5af19)", 
            "desc": "Elite nos dois lados da quadra. Pontua em alto volume no ataque e destrói posses adversárias na defesa."
        }

    # 4. Three-Level Scorer (Booker, Mitchell)
    if ppg >= 22 and usg >= 25:
        return {
            "nome": "Three-Level Scorer", "icone": "🔥", 
            "cor": "linear-gradient(135deg, #cb2d3e, #ef473a)", 
            "desc": "Pontuador nato capaz de castigar a defesa atacando o aro, na meia-distância e da linha de 3 pontos."
        }

    # ==========================================
    # TIER 2: ELITE ROLE PLAYERS E ESPECIALISTAS
    # ==========================================

    # 5. Maestro Puro / Floor General (Chris Paul)
    if apg >= 7.5 and ast_pct >= 30:
        return {
            "nome": "Floor General", "icone": "🧠", 
            "cor": "linear-gradient(135deg, #00C9FF, #92FE9D)", 
            "desc": "O maestro do time. Controla o ritmo do jogo, lê a defesa e é o cérebro que faz o sistema funcionar."
        }

    # 6. Lethal Sharpshooter
    if pct_3pt >= 38.0 and fg3a >= 6.0:
        return {
            "nome": "Lethal Sharpshooter", "icone": "🎯", 
            "cor": "linear-gradient(135deg, #11998e, #38ef7d)", 
            "desc": "Arma letal do perímetro. Exige marcação colada e pune a defesa com alto volume e precisão de 3 pontos."
        }

    # 7. 3&D Specialist (Mikal Bridges, OG Anunoby)
    if pct_3pt >= 36.0 and fg3a >= 4.0 and (spg >= 1.0 or defl >= 2.0 or bpg >= 0.8) and usg <= 22:
        return {
            "nome": "3&D Specialist", "icone": "🏹", 
            "cor": "linear-gradient(135deg, #00b4db, #0083b0)", 
            "desc": "O arquétipo perfeito. Mata bolas de fora com eficiência e defende múltiplos jogadores no perímetro."
        }

    # 8. Athletic Finisher / Lob Threat (Aaron Gordon, Jarrett Allen)
    if ts >= 60.0 and ppg >= 11 and rpg >= 5 and usg <= 22:
        return {
            "nome": "Athletic Finisher", "icone": "🚁", 
            "cor": "linear-gradient(135deg, #e52d27, #b31217)", 
            "desc": "Força física e altíssima eficiência. Vive de enterradas, cortes para a cesta (cuts) e pontuação no garrafão sem precisar amassar a bola."
        }

    # 9. Paint Beast / Protetor de Aro Dominante (Gobert)
    if rpg >= 9 and bpg >= 1.2:
        return {
            "nome": "Paint Beast", "icone": "🧱", 
            "cor": "linear-gradient(135deg, #3a7bd5, #3a6073)", 
            "desc": "O dono do garrafão. Domina a tábua de rebotes e protege o aro, alterando os arremessos adversários."
        }

    # 10. Stretch Big / O Unicórnio (KAT, Porzingis)
    if rpg >= 6.0 and fg3a >= 3.5 and pct_3pt >= 34.0:
        return {
            "nome": "Stretch Big", "icone": "🦄",
            "cor": "linear-gradient(135deg, #DA4453, #89216B)",
            "desc": "O pivô moderno. Abre o ataque castigando de 3 pontos e tira o protetor de aro adversário do garrafão."
        }

    # ==========================================
    # TIER 3: ROTAÇÃO E ENGENHARIA DE EQUIPE
    # ==========================================

    # 11. Swiss Army Knife (Derrick White, Josh Hart)
    if ppg >= 10 and rpg >= 4.5 and apg >= 3.5:
        return {
            "nome": "Swiss Army Knife", "icone": "🛠️", 
            "cor": "linear-gradient(135deg, #8E2DE2, #4A00E0)", 
            "desc": "O canivete suíço. Faz de tudo um pouco com versatilidade pura para preencher qualquer buraco tático."
        }

    # 12. Spark Plug / Microondas (Jordan Clarkson, Malik Monk)
    if ppg >= 12 and usg >= 23 and apg < 4.5:
        return {
            "nome": "Spark Plug Scorer", "icone": "🔋", 
            "cor": "linear-gradient(135deg, #f2709c, #ff9472)", 
            "desc": "O famoso 'Microondas'. Entra para acelerar o ritmo, isolar e injetar pontos rápidos no placar."
        }

    # 13. Lockdown Defender
    if (spg >= 1.5 or defl >= 2.5) and usg <= 18:
        return {
            "nome": "Lockdown Defender", "icone": "🔒", 
            "cor": "linear-gradient(135deg, #333333, #dd1818)", 
            "desc": "Especialista defensivo. Sua principal função é infernizar e anular a principal arma ofensiva adversária."
        }

    # 14. Glue Guy (A Cola do Time)
    if net_rtg >= 3.0 and usg <= 16:
        return {
            "nome": "Glue Guy", "icone": "🧩", 
            "cor": "linear-gradient(135deg, #56ab2f, #a8e063)", 
            "desc": "A cola do time. Não precisa tocar na bola para impactar positivamente; vence minutos cuidando dos detalhes."
        }

    # 15. Base da Rotação
    return {
        "nome": "System Player", "icone": "⚙️", 
        "cor": "linear-gradient(135deg, #4b6cb7, #182848)", 
        "desc": "Peça de rotação sólida que cumpre sua função dentro do esquema tático estabelecido."
    }