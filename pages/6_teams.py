import streamlit as st
import pandas as pd
from data.queries import obter_dados_times
from components.charts import grafico_quadrantes_times

st.title("🏀 Team Analytics & Landscape")
st.markdown("Análise de sistema: descubra a identidade de jogo, o ritmo e a eficiência de cada franquia da NBA.")

temporada_selecionada = st.session_state.get('filtro_temporada')
# 👇 1. Resgatando o filtro de tipo de temporada
tipo_temporada = st.session_state.get('filtro_tipo_temporada', 'Regular Season')

if not temporada_selecionada:
    st.warning("Selecione uma temporada no menu lateral.")
    st.stop()

# 👇 2. Dando contexto visual para o usuário
st.caption(f"Exibindo dados da temporada **{temporada_selecionada}** ({tipo_temporada})")
st.divider()

# 👇 3. Passando a variável tipo_temporada como segundo parâmetro!
dados_times = obter_dados_times(temporada_selecionada, tipo_temporada)

if dados_times:
    # 1. Gráfico de Quadrantes
    st.subheader("📍 League Landscape (Quadrantes de Eficiência)")
    st.markdown("Entenda como ler este gráfico:")
    
    # Legenda colorida com colunas
    col1, col2, col3, col4 = st.columns(4)
    col1.success("↗️ Contenders\n\nAtaque e Defesa de Elite.")
    col2.info("↘️ Tiroteio\n\nÓtimo Ataque, Péssima Defesa.")
    col3.warning("↖️ Trincheira\n\nÓtima Defesa, Péssimo Ataque.")
    col4.error("↙️️ Loteria\n\nRuins em ambos os lados.")
    
    fig = grafico_quadrantes_times(dados_times)
    if fig:
        # st.plotly_chart com use_container_width=True faz ele abraçar a tela toda
        st.plotly_chart(fig, use_container_width=True)
        
    st.divider()

    # 2. Tabela de Ritmo e Eficiência
    st.subheader("📋 Tabela de Ritmo e Rating")
    st.markdown("Times classificados pelo **Net Rating** (Saldo de pontos a cada 100 posses). O **Pace** mostra a velocidade da equipe (Posses por partida).")
    
    df_times = pd.DataFrame(dados_times)
    df_times = df_times.sort_values(by='net_rating', ascending=False)
    
    # Prepara a tabela bonita para exibição
    df_exibicao = df_times[['nome_time', 'vitorias', 'derrotas', 'off_rating', 'def_rating', 'net_rating', 'pace']].copy()
    
    # 👇 Arredondando as casas decimais para a tabela não ficar com números gigantes
    df_exibicao['off_rating'] = df_exibicao['off_rating'].round(1)
    df_exibicao['def_rating'] = df_exibicao['def_rating'].round(1)
    df_exibicao['net_rating'] = df_exibicao['net_rating'].round(1)
    df_exibicao['pace'] = df_exibicao['pace'].round(1)
    
    df_exibicao.columns = ['Time', 'Vitórias', 'Derrotas', 'Off Rating', 'Def Rating', 'Net Rating', 'Pace (Ritmo)']
    
    st.dataframe(
        df_exibicao, 
        hide_index=True, 
        use_container_width=True,
        height=500
    )
    
else:
    st.warning(f"Nenhum dado de time encontrado para a temporada {temporada_selecionada} ({tipo_temporada}).")