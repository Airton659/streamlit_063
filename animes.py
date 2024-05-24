import streamlit as st
import pandas as pd
#import plotly.express as px
import re

# Função para remover redundância
def remover_redundancia(texto):
    return re.sub(r'([A-Za-z]+)\1', r'\1', texto)

# Carregar dados
df_original = pd.read_csv('Top_Anime_data.csv')
df = df_original.copy()

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

# Filtro por Gênero
generos = df['MainGenres'].unique().tolist()
genero_selecionado = st.sidebar.multiselect('Selecione o Gênero:', generos)

# Filtro por Tipo
tipos = df['Type'].unique().tolist()
tipo_selecionado = st.sidebar.multiselect('Selecione o Tipo:', tipos)

# Verificar se nenhum tipo foi selecionado
if not tipo_selecionado:
    tipo_selecionado = tipos

# Filtro por Popularidade
popularidade_min = st.sidebar.slider('Popularidade Mínima:', min_value=df['Popularity'].min(), max_value=df['Popularity'].max(), value=df['Popularity'].min())
popularidade_max = st.sidebar.slider('Popularidade Máxima:', min_value=df['Popularity'].min(), max_value=df['Popularity'].max(), value=df['Popularity'].max())

# Filtro por Rank
rank_min = st.sidebar.slider('Rank Mínimo:', min_value=int(df['Rank'].min()), max_value=int(df['Rank'].max()), value=int(df['Rank'].min()))
rank_max = st.sidebar.slider('Rank Máximo:', min_value=int(df['Rank'].min()), max_value=int(df['Rank'].max()), value=int(df['Rank'].max()))



# Verificar se nenhum filtro foi selecionado
if not genero_selecionado:
    df_filtrado = df[(df['Type'].isin(tipo_selecionado)) &
                     (df['Popularity'].between(popularidade_min, popularidade_max)) &
                     (df['Rank'].between(rank_min, rank_max))]
else:
    df_filtrado = df[(df['MainGenres'].isin(genero_selecionado)) &
                     (df['Type'].isin(tipo_selecionado)) &
                     (df['Popularity'].between(popularidade_min, popularidade_max)) &
                     (df['Rank'].between(rank_min, rank_max))]

# Definir cor padrão
cor_padrao = '#1f77b4'  

# Organizar os gráficos em duas colunas
col1, col2 = st.columns(2)

# Gráfico de barras para gêneros
with col1:
    st.subheader("Número de Animes por Gênero")
    soma_por_genero = df_filtrado['MainGenres'].value_counts().reset_index()
    soma_por_genero.columns = ['MainGenres', 'Count']
    fig1 = px.bar(soma_por_genero, x='Count', y='MainGenres', orientation='h', 
                 labels={'Count': 'Número de Animes', 'MainGenres': 'Gênero'},
                 color_discrete_sequence=[cor_padrao])
    fig1.update_layout(legend=dict(font=dict(size=8)))
    st.plotly_chart(fig1, use_container_width=True)
    st.write("Este gráfico mostra o número de animes por gênero.")

# Gráfico de pizza para status dos animes
with col2:
    st.subheader("Proporção de Status dos Animes (Filtrado)")
    
    # Renomear as categorias
    df_filtrado['Status'] = df_filtrado['Status'].replace({'Finished Airing': 'Concluído', 
                                                           'Currently Airing': 'No ar'})
    
    status_counts = df_filtrado['Status'].value_counts()
    fig2 = px.pie(values=status_counts, names=status_counts.index, 
                  color_discrete_sequence=[cor_padrao])
    
    # Alterar a legenda
    fig2.update_traces(textposition='inside', textinfo='percent',insidetextfont=dict(color='white'))
    
    st.plotly_chart(fig2, use_container_width=True)
    st.write("Este gráfico de pizza mostra a proporção de status dos animes")

# Gráfico de caixa Gênero por Pontos
st.subheader("Score por Gênero")
df_filtrado['Outlier_Info'] = df_filtrado.apply(lambda row: f"Rank: {row['Rank']}, English: {row['English']}" if row['Score'] > df_filtrado['Score'].quantile(0.95) else '', axis=1)
fig5 = px.box(df_filtrado, x='MainGenres', y='Score',
             labels={'MainGenres': 'Gênero', 'Score': 'Pontuação'},
             color_discrete_sequence=[cor_padrao])

fig5.update_traces(marker=dict(color='rgb(158,202,225)', size=7),
                  selector=dict(type='box'), boxpoints='outliers', hoverinfo='y+text',
                  hovertext=df_filtrado['Outlier_Info'])

st.plotly_chart(fig5, use_container_width=True)
st.write("Este gráfico de caixa mostra a distribuição dos scores por gênero.")


# Gráfico de Dispersão para Popularidade vs Score
with col1:
    st.subheader("Dispersão de Popularidade vs. Score")
    fig3 = px.scatter(df_filtrado, x='Popularity', y='Score',
                      hover_name=df_filtrado.apply(lambda row: row['English'] if pd.notnull(row['English']) else row['Japanese'], axis=1),
                      hover_data=['Rank', 'MainGenres'],
                      color_discrete_sequence=[cor_padrao])
    st.plotly_chart(fig3, use_container_width=True)
    st.write("Este gráfico mostra a relação entre popularidade e score dos animes.")

# Histograma para Duração dos Episódios
with col2:
    st.subheader("Histograma da Duração dos Animes")
    fig4 = px.histogram(df_filtrado, x='Duration', color_discrete_sequence=[cor_padrao])
    st.plotly_chart(fig4, use_container_width=True)
    st.write("Este histograma mostra a distribuição da duração dos episódios dos animes.")

# Gráfico de barras de animes por estúdio
st.subheader('Animes por Estúdio')
studio_counts = df_filtrado['Studios'].value_counts().sort_values(ascending=False)
st.bar_chart(studio_counts, use_container_width=True)
st.write("Este gráfico mostra os estúdios que têm produzido mais animes")


