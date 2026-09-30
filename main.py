import time
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

# =====================================================================
# BLINDAGEM ANTI-BLOQUEIO (Disfarce de Navegador para o GitHub Actions)
# =====================================================================
original_get = requests.get

def get_disfarcado(*args, **kwargs):
    """Injeta cabeçalhos de navegador real e aumenta o timeout para a NBA não bloquear o script."""
    # Aumenta a paciência do robô para 60 segundos (o padrão era 30)
    kwargs.setdefault('timeout', 60)
    
    # Cria o disfarce de usuário comum
    headers = kwargs.get('headers', {})
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    })
    kwargs['headers'] = headers
    return original_get(*args, **kwargs)

# Substitui globalmente a função do Python pela nossa função disfarçada
requests.get = get_disfarcado
# =====================================================================

from nba_api.stats.endpoints import commonallplayers
from extrator import (
    buscar_dados_brutos_jogador, 
    buscar_estatisticas_carreira, 
    buscar_estatisticas_avancadas_liga, 
    buscar_estatisticas_hustle_liga, 
    buscar_estatisticas_clutch_liga
)
from transformador import (
    limpar_dados_jogador, 
    limpar_estatisticas_carreira, 
    limpar_estatisticas_avancadas, 
    limpar_estatisticas_hustle, 
    limpar_estatisticas_clutch,
    criar_perfil_basico_liga
)
from carregador import (
    enviar_para_banco, 
    enviar_estatisticas_para_banco, 
    enviar_stats_avancadas, 
    enviar_stats_hustle, 
    enviar_stats_clutch,
    limpar_dados_temporada_atual
)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def obter_ids_jogadores_ativos():
    print("Mapeando todos os jogadores ativos da liga...")
    lista_completa = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_dict()
    id_index = lista_completa['resultSets'][0]['headers'].index("PERSON_ID")
    ids = [linha[id_index] for linha in lista_completa['resultSets'][0]['rowSet']]
    print(f"Total de {len(ids)} jogadores encontrados.\n")
    return ids

def executar_atualizacao_diaria(temporada_atual="2026-27"):
    """Rotina ultrarrápida otimizada para rodar diariamente via GitHub Actions."""
    print(f"--- INICIANDO ATUALIZAÇÃO DIÁRIA DA NBA ({temporada_atual}) ---")
    
    ids_jogadores = obter_ids_jogadores_ativos()
    limpar_dados_temporada_atual(temporada_atual)
    
    try:
        bruto_adv, _ = buscar_estatisticas_avancadas_liga(temporada_atual)
        
        perfil_basico = criar_perfil_basico_liga(bruto_adv, temporada_atual)
        if perfil_basico: 
            enviar_para_banco(perfil_basico)

        limpa_adv = limpar_estatisticas_avancadas(bruto_adv, temporada_atual)
        filtrada_adv = [s for s in limpa_adv if s["jogador_id"] in ids_jogadores]
        
        bruto_hustle, _ = buscar_estatisticas_hustle_liga(temporada_atual)
        limpa_hustle = limpar_estatisticas_hustle(bruto_hustle, temporada_atual)
        filtrada_hustle = [s for s in limpa_hustle if s["jogador_id"] in ids_jogadores]
        
        bruto_clutch, _ = buscar_estatisticas_clutch_liga(temporada_atual)
        limpa_clutch = limpar_estatisticas_clutch(bruto_clutch, temporada_atual)
        filtrada_clutch = [s for s in limpa_clutch if s["jogador_id"] in ids_jogadores]
        
        print(f"\n[CARGA] Enviando métricas atualizadas de {temporada_atual}...")
        if filtrada_adv: enviar_stats_avancadas(filtrada_adv)
        if filtrada_hustle: enviar_stats_hustle(filtrada_hustle)
        if filtrada_clutch: enviar_stats_clutch(filtrada_clutch)
        
        print("\n--- ATUALIZAÇÃO DIÁRIA CONCLUÍDA COM SUCESSO! ---")
        
    except Exception as e:
        print(f"[ERRO FATAL NA ATUALIZAÇÃO DIÁRIA]: {e}")

if __name__ == "__main__":
    executar_atualizacao_diaria("2026-27")