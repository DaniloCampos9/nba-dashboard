import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def grafico_percentis_snapshot(usg_percentil, ts_percentil):
    """Gera um gráfico horizontal de percentis minimalista e moderno."""
    
    categorias = ['Eficiência (TS%)', 'Volume Ofensivo (USG%)']
    valores = [ts_percentil or 0, usg_percentil or 0]

    # Lógica de cores inteligente (Vermelho -> Laranja -> Azul Claro -> Azul Escuro)
    cores = []
    for val in valores:
        if val >= 80: cores.append('#1D428A')     # Elite (Azul NBA)
        elif val >= 50: cores.append('#4B92FF')   # Acima da média
        elif val >= 30: cores.append('#FFA500')   # Abaixo da média (Alerta)
        else: cores.append('#FF4B4B')             # Ruim (Vermelho)

    fig = go.Figure(go.Bar(
        x=valores,
        y=categorias,
        orientation='h',
        marker_color=cores,
        text=[f"{v}º Percentil" if v else "N/A" for v in valores],
        textposition='inside',
        insidetextanchor='middle',
        insidetextfont=dict(color='white', size=14, family="Arial Black")
    ))

    # Limpando o fundo para ficar elegante (sem linhas de grade feias)
    fig.update_layout(
        xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=14, color="#FAFAFA")),
        margin=dict(l=0, r=0, t=10, b=0), # Margens super apertadas
        height=120,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        dragmode=False # Impede o usuário de dar zoom sem querer
    )
    return fig

def grafico_scatter_ataque(df, x_col, y_col, titulo, subtitulo, jogador_destaque=None):
    """Cria um gráfico de dispersão com destaque dinâmico para o jogador selecionado."""
    
    # Configurar cores: cinza escuro para a liga, Azul NBA para o jogador em destaque
    df['Cor'] = 'Liga'
    df['Tamanho'] = 8
    
    if jogador_destaque:
        df.loc[df['nome_completo'] == jogador_destaque, 'Cor'] = 'Selecionado'
        df.loc[df['nome_completo'] == jogador_destaque, 'Tamanho'] = 20 # Deixa o ponto bem maior!

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        hover_name="nome_completo",
        hover_data={x_col: True, y_col: True, 'Cor': False, 'Tamanho': False},
        color='Cor',
        color_discrete_map={'Liga': '#444444', 'Selecionado': '#1D428A'},
        size='Tamanho'
    )

    # Estilização limpa e moderna
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b><br><span style='font-size:12px;color:gray'>{subtitulo}</span>"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA'),
        xaxis=dict(showgrid=True, gridcolor='#333333', title=x_col),
        yaxis=dict(showgrid=True, gridcolor='#333333', title=y_col),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig

def grafico_quadrantes_times(dados_times):
    """Gera o Scatter Plot de Landscape da liga."""
    df = pd.DataFrame(dados_times)
    if df.empty:
        return None

    # Calculamos a média da liga para desenhar a cruz no meio do gráfico
    avg_off = df['off_rating'].mean()
    avg_def = df['def_rating'].mean()

    fig = px.scatter(
        df,
        x='off_rating',
        y='def_rating',
        text='nome_time',
        hover_data=['vitorias', 'derrotas', 'net_rating', 'pace'],
        labels={
            'off_rating': 'Ataque (Pts marcados a cada 100 posses)',
            'def_rating': 'Defesa (Pts sofridos a cada 100 posses)'
        },
        title='League Landscape: Identidade e Eficiência'
    )

    # O SEGREDO ANALÍTICO: Inverter o eixo Y. 
    # Em Def Rating, números menores são melhores (sofreu menos pontos).
    # Invertendo, a melhor defesa fica no TOPO do gráfico.
    fig.update_yaxes(autorange="reversed")

    # Adiciona as linhas pontilhadas cinzas cruzando as médias
    fig.add_hline(y=avg_def, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=avg_off, line_dash="dash", line_color="gray", opacity=0.5)

    # Melhora o design das bolinhas e ajusta o texto para não ficar em cima da bolinha
    fig.update_traces(
        textposition='top center', 
        textfont=dict(size=10, color="lightgray"),
        marker=dict(size=12, color='#1f77b4', line=dict(width=1, color='DarkSlateGrey'))
    )
    
    # Deixa o fundo transparente para combinar com o Dark Mode do Streamlit
    fig.update_layout(
        height=650, # Deixa o gráfico bem grande e imponente
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig