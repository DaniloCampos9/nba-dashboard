import streamlit as st
import pandas as pd
from data.db import supabase

@st.cache_data(ttl=3600) # Cache de 1 hora. O Streamlit não vai bater no banco toda hora!
def obter_lista_jogadores():
    """Busca a lista de todos os jogadores disponíveis no banco para popular o filtro."""
    try:
        # Ajuste "nome_completo" para o nome exato da coluna na sua tabela "jogadores"
        resposta = supabase.table("jogadores").select("nome_completo").execute()
        jogadores = [linha['nome_completo'] for linha in resposta.data if linha.get('nome_completo')]
        return sorted(jogadores) # Retorna em ordem alfabética
    except Exception as e:
        st.sidebar.error(f"Erro ao buscar jogadores: {e}")
        return ["Erro ao carregar"]

def obter_perfil_jogador(nome_jogador):
    """Busca os dados cadastrais de um jogador específico."""
    try:
        resposta = supabase.table("jogadores").select("*").eq("nome_completo", nome_jogador).execute()
        if resposta.data:
            return resposta.data[0] # Retorna o primeiro (e único) registro encontrado
        return None
    except Exception as e:
        st.error(f"Erro ao buscar perfil: {e}")
        return None

# 👇 AQUI FOI CORRIGIDO: Alinhado na margem e colado na função dele!
@st.cache_data(ttl=300) # Cache de 5 minutos
def obter_estatisticas_resumo(jogador_id, temporada):
    """Busca estatísticas tradicionais e avançadas do jogador para a temporada selecionada."""
    try:
        # Busca tradicionais (PPG, RPG, APG)
        resp_trad = supabase.table("estatisticas_temporada").select("*").eq("jogador_id", jogador_id).eq("temporada", temporada).execute()
        
        # Busca avançadas (TS%, USG%, Net Rating)
        resp_adv = supabase.table("stats_avancadas").select("*").eq("jogador_id", jogador_id).eq("temporada", temporada).execute()
        
        # Junta tudo em um único dicionário
        stats_completas = {}
        if resp_trad.data:
            stats_completas.update(resp_trad.data[0])
        if resp_adv.data:
            stats_completas.update(resp_adv.data[0])
            
        return stats_completas
    except Exception as e:
        st.error(f"Erro ao buscar estatísticas: {e}")
        return {}
    
@st.cache_data(ttl=3600)
def obter_dados_liga_avancados(temporada):
    """Busca os dados de USG% e TS% de TODOS os jogadores para calcularmos percentis."""
    try:
        resp = supabase.table("stats_avancadas").select("usg_pct, ts_pct").eq("temporada", temporada).execute()
        return resp.data if resp.data else []
    except Exception as e:
        return []

@st.cache_data(ttl=3600)
def obter_dados_completos_liga(temporada):
    """Busca as estatísticas de todos os jogadores para calcularmos as médias da liga."""
    try:
        # Busca tradicionais
        resp_trad = supabase.table("estatisticas_temporada").select("jogador_id, jogos_disputados, pontos_totais, rebotes_totais, assistencias_totais").eq("temporada", temporada).execute()
        # Busca avançadas
        resp_adv = supabase.table("stats_avancadas").select("jogador_id, ts_pct, usg_pct, net_rating, efg_pct, ast_pct").eq("temporada", temporada).execute()
        
        df_trad = pd.DataFrame(resp_trad.data)
        df_adv = pd.DataFrame(resp_adv.data)
        
        if df_trad.empty or df_adv.empty:
            return pd.DataFrame()
            
        # Mescla os dois bancos usando o ID do jogador
        df = pd.merge(df_trad, df_adv, on="jogador_id", how="inner")
        
        # Filtra quem não jogou para não quebrar a divisão
        df = df[df['jogos_disputados'] > 0].copy()
        
        # Calcula as métricas por jogo (Per Game)
        df['PPG'] = df['pontos_totais'] / df['jogos_disputados']
        df['RPG'] = df['rebotes_totais'] / df['jogos_disputados']
        df['APG'] = df['assistencias_totais'] / df['jogos_disputados']
        
        return df
    except Exception as e:
        st.error(f"Erro ao compilar dados da liga: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def obter_dados_graficos_ataque(temporada):
    """Busca dados de ataque e nomes da liga inteira para os scatter plots."""
    try:
        resp_trad = supabase.table("estatisticas_temporada").select("jogador_id, jogos_disputados, pontos_totais").eq("temporada", temporada).execute()
        resp_adv = supabase.table("stats_avancadas").select("jogador_id, ts_pct, usg_pct").eq("temporada", temporada).execute()
        resp_jog = supabase.table("jogadores").select("id, nome_completo").execute()

        df_trad = pd.DataFrame(resp_trad.data)
        df_adv = pd.DataFrame(resp_adv.data)
        df_jog = pd.DataFrame(resp_jog.data)

        if df_trad.empty or df_adv.empty or df_jog.empty:
            return pd.DataFrame()

        # Junta as 3 tabelas (Estatísticas Tradicionais + Avançadas + Cadastro de Jogadores)
        df = pd.merge(df_trad, df_adv, on="jogador_id")
        df = pd.merge(df, df_jog, left_on="jogador_id", right_on="id")

        # Filtra e formata para o gráfico ficar elegante
        df = df[df['jogos_disputados'] > 0].copy()
        df['PPG'] = round(df['pontos_totais'] / df['jogos_disputados'], 1)
        df['TS%'] = round(df['ts_pct'] * 100, 1)
        df['USG%'] = round(df['usg_pct'] * 100, 1)

        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados para gráficos: {e}")
        return pd.DataFrame()
    
@st.cache_data(ttl=300)
def obter_estatisticas_defesa(jogador_id, temporada):
    """Busca as métricas defensivas (Roubos, Tocos e Deflections)."""
    try:
        resposta = supabase.table("stats_defesa").select("*").eq("jogador_id", jogador_id).eq("temporada", temporada).execute()
        return resposta.data[0] if resposta.data else {}
    except Exception as e:
        st.error(f"Erro ao buscar defesa: {e}")
        return {}
    
@st.cache_data(ttl=300)
def obter_dados_times(temporada):
    """Busca as métricas avançadas dos times (Pace, Ratings) no banco."""
    try:
        resposta = supabase.table("stats_times").select("*").eq("temporada", temporada).execute()
        return resposta.data if resposta.data else []
    except Exception as e:
        st.error(f"Erro ao buscar dados dos times: {e}")
        return []