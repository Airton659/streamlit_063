import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Função para remover redundância
def remover_redundancia(texto):
    return re.sub(r'([A-Za-z]+)\1', r'\1', texto)

# Carregar dados
df_original = pd.read_csv('Top_Anime_data.csv')
df = df_original.copy()

# st.write(df_original)

# Tratando coluna Genres
df['MainGenres'] = df['Genres'].str.split(',').str[0]
df['MainGenres'] = df['MainGenres'].astype(str)
df['MainGenres'] = df['MainGenres'].apply(remover_redundancia)
df['MainGenres'] = df['MainGenres'].replace({'Avant GardeAvant Garde': 'Avant Garde', 
                                             'Award WiningAward Wining': 'Award Winning', 
                                             'Boys LoveBoys Love': 'Boys Love', 
                                             'Sci-FiSci-Fi': 'Sci-Fi', 
                                             'Slice of LifeSlice of Life': 'Slice of Life', 
                                             'nan': 'Não identificado'})

# Configurações da página
st.set_page_config(
    page_title='Top 1000 animes 2024',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Título da página
st.title('Top 1000 Animes 2024')

# Barra lateral com filtros
# st.sidebar.header('Filtros')
st.sidebar.markdown("José Airton Marques Júnior - 063", unsafe_allow_html=True)

# Definir a cor dos gráficos
cor_padrao = st.sidebar.color_picker('Escolha a cor padrão para os gráficos', '#1f77b4')

# Filtro por Gênero
generos = df['MainGenres'].unique().tolist() #Criando uma lista com as opções disponíveis na coluna MainGenres
genero_selecionado = st.sidebar.multiselect('Selecione o Gênero:', generos) #genero_selecionado recebe as multiplas opções selecionadas no filtro

# Filtro por Tipo
tipos = df['Type'].unique().tolist()
tipo_selecionado = st.sidebar.multiselect('Selecione o Tipo:', tipos)

# Verificar se nenhum tipo foi selecionado
if not tipo_selecionado: #verifica se not tipo_selecionado é False (preenchida) ou True (Sem seleção), caso seja true, define como todos os tipos
    tipo_selecionado = tipos


# Filtro por Popularidade (Range Slider)
popularidade_range = st.sidebar.slider(
    'Selecione o intervalo de Popularidade:',
    min_value=int(df['Popularity'].min()),
    max_value=int(df['Popularity'].max()),
    value=(int(df['Popularity'].min()), int(df['Popularity'].max()))
)

popularidade_min, popularidade_max = popularidade_range


# Filtro por Rank (Range Slider)
rank_range = st.sidebar.slider(
    'Selecione o intervalo de Rank:',
    min_value=int(df['Rank'].min()),
    max_value=int(df['Rank'].max()),
    value=(int(df['Rank'].min()), int(df['Rank'].max()))
    
)

rank_min, rank_max = rank_range

# Verificar se nenhum filtro foi selecionado
#Se nenhum gênero for selecionado, aplica apenas os filtros de tipo, popularidade e rank. Se um gênero for selecionado, aplica todos os filtros incluindo o gênero.
if not genero_selecionado:
    df_filtrado = df[(df['Type'].isin(tipo_selecionado)) &
                     (df['Popularity'].between(popularidade_min, popularidade_max)) &
                     (df['Rank'].between(rank_min, rank_max))]
else:
    df_filtrado = df[(df['MainGenres'].isin(genero_selecionado)) &
                     (df['Type'].isin(tipo_selecionado)) &
                     (df['Popularity'].between(popularidade_min, popularidade_max)) &
                     (df['Rank'].between(rank_min, rank_max))]

# Exibir número de registros filtrados na barra lateral
st.sidebar.markdown(f"### Número de registros filtrados: {len(df_filtrado)}")

# Organizar os gráficos em duas colunas
col1, col2, col3 = st.columns(3)

# Gráfico de barras para gêneros
with col1:
    st.subheader("Animes x Gênero")
    soma_por_genero = df_filtrado['MainGenres'].value_counts().reset_index()
    soma_por_genero.columns = ['MainGenres', 'Count']
    fig1 = px.bar(soma_por_genero, x='Count', y='MainGenres', orientation='h', 
                 labels={'Count': 'Número de Animes', 'MainGenres': 'Gênero'},
                 color_discrete_sequence=[cor_padrao],
                 width=400, height=300)
    fig1.update_layout(legend=dict(font=dict(size=8)))
    st.plotly_chart(fig1, use_container_width=True)
    st.write("Este gráfico mostra o número de animes por gênero.")


# Gráfico de pizza para status dos animes
with col2:
    st.subheader("Animes x Status")
    
    # Renomear as categorias
    df_filtrado['Status'] = df_filtrado['Status'].replace({'Finished Airing': 'Concluído', 
                                                           'Currently Airing': 'No ar'})
    
    status_counts = df_filtrado['Status'].value_counts()
    fig2 = px.pie(values=status_counts, names=status_counts.index, 
                  color_discrete_sequence=[cor_padrao],
                  width=400, height=300)
    
    fig2.update_traces(textinfo='percent')
    
    st.plotly_chart(fig2, use_container_width=True)
    st.write("Este gráfico de pizza mostra a proporção de status dos animes")


# Card para o anime com maior Rank
with col3:
    st.subheader("Anime com Melhor Rank")
    anime_melhor_rank = df_filtrado.loc[df_filtrado['Rank'].idxmin()]
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 10px; width: 100%;  height: 390px;">
            <p><strong>Nome:</strong> {anime_melhor_rank['English'] if pd.notnull(anime_melhor_rank['English']) else anime_melhor_rank['Japanese']}</p>
            <p><strong>Rank:</strong> {anime_melhor_rank['Rank']}</p>
            <p><strong>Popularidade:</strong> {anime_melhor_rank['Popularity']}</p>
            <p><strong>Score:</strong> {anime_melhor_rank['Score']}</p>
            <p><strong>Estudio:</strong> {anime_melhor_rank['Studios']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Gráfico de Dispersão para Popularidade vs Score
with col1:
    st.subheader("Popularidade x Score")
    fig3 = px.scatter(df_filtrado, x='Popularidade', y='Pontuação',
                      hover_name=df_filtrado.apply(lambda row: row['English'] if pd.notnull(row['English']) else row['Japanese'], axis=1), #Caso não tenha o nome em inglês, trazer o nome em japonês ao passar o mouse por cima
                      hover_data=['Rank', 'MainGenres'],
                      color_discrete_sequence=[cor_padrao],
                      width=400, height=300)
    st.plotly_chart(fig3, use_container_width=True)
    st.write("Este gráfico mostra a relação entre popularidade e score dos animes.")


with col3:
    st.subheader("Anime mais Popular")
    anime_mais_popular = df_filtrado.loc[df_filtrado['Popularity'].idxmax()]
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 10px; width: 100%;  height: 420px;">
            <p><strong>Nome:</strong> {anime_mais_popular['English'] if pd.notnull(anime_mais_popular['English']) else anime_mais_popular['Japanese']}</p>
            <p><strong>Rank:</strong> {anime_mais_popular['Rank']}</p>
            <p><strong>Popularidade:</strong> {anime_mais_popular['Popularity']}</p>
            <p><strong>Score:</strong> {anime_mais_popular['Score']}</p>
            <p><strong>Estúdio:</strong> {anime_mais_popular['Studios']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Gráfico de caixa Gênero por Pontos
with col2:   
    st.subheader("Score x Gênero")
    fig5 = px.box(df_filtrado, x='MainGenres', y='Score',
                 labels={'MainGenres': 'Gênero', 'Score': 'Pontuação'},
                 color_discrete_sequence=[cor_padrao],
                 width=400, height=300)
    
    st.plotly_chart(fig5, use_container_width=True)
    st.write("Este gráfico de caixa mostra a distribuição dos scores por gênero.")


# # Gráfico de barras de animes por estúdio
# st.subheader('Animes por Estúdio')
# studio_counts = df_filtrado['Studios'].value_counts().sort_values(ascending=False)
# st.bar_chart(studio_counts, use_container_width=True)
# st.write("Este gráfico mostra os estúdios que têm produzido mais animes")

# # # Histograma para Duração dos Episódios
# with col2:
#     st.subheader("Histograma da Duração dos Animes")
#     fig4 = px.histogram(df_filtrado, x='Duration', color_discrete_sequence=[cor_padrao],
#                  width=400, height=300)
#     st.plotly_chart(fig4, use_container_width=True)
#     st.write("Este histograma mostra a distribuição da duração dos episódios dos animes.")

