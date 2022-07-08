#import relevant libraries 
import pandas as pd 
import numpy as np 
import plotly.express as px
import streamlit as st
from datetime import datetime
###############################################################################

st.set_page_config(
     page_title="Ex-stream-ly Cool App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="collapsed",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

# loading datasets and some reengineering
@st.cache(allow_output_mutation=True)
def load_data():
    df_game_gen = pd.read_csv('data/GeneralEsportData.csv',encoding='cp1252')
    df_game_his = pd.read_csv('data/HistoricalEsportData.csv',encoding='cp1252')
    df_teams = pd.read_csv('data/highest_earning_teams.csv',encoding='cp1252')
    df_players = pd.read_csv('data/highest_earning_players.csv')
    df_players['CountryCode'] = df_players['CountryCode'].apply(lambda x: x.upper())
    df_countries = pd.read_csv('data/country-and-continent-codes-list.csv')
    return df_countries,df_game_gen,df_game_his,df_teams,df_players

df_countries,df_game_gen,df_game_his,df_teams,df_players = load_data()

###############################################################################

#Data reengineering


df_game_gen.Genre = df_game_gen.Genre.replace(['Fighting Game','First-Person Shooter','Multiplayer Online Battle Arena','Collectible Card Game','Puzzle Game','Battle Royale','Third-Person Shooter','Role-Playing Game'],['Fighting','FPP','MOBA','Card','Puzzle','BR','TPP','RPG'])
print(df_game_gen.Genre.value_counts())
df_players.Genre = df_players.Genre.replace(['Fighting Game','First-Person Shooter','Multiplayer Online Battle Arena','Collectible Card Game','Puzzle Game','Battle Royale','Third-Person Shooter','Role-Playing Game'],['Fighting','FPP','MOBA','Card','Puzzle','BR','TPP','RPG'])
#df_teams['TeamName'].value_counts()
df_teams.Genre = df_teams.Genre.replace(['Fighting Game','First-Person Shooter','Multiplayer Online Battle Arena','Collectible Card Game','Puzzle Game','Battle Royale','Third-Person Shooter','Role-Playing Game'],['Fighting','FPP','MOBA','Card','Puzzle','BR','TPP','RPG'])
#filter out games who do not meet earning and tournament restrictions For example: games without any recorded cash prizes or an extremely low amount (in the low hundreds), the same goes for the number of tournaments, a game which held only a tournament or to should not be considered in my opinion

df_game_his['Date'] = pd.to_datetime(df_game_his['Date'])
df_game_his['year'] = df_game_his['Date'].dt.year
filterd_game = df_game_his[df_game_his['Earnings'] > 1]
filterd_game = pd.merge(filterd_game, df_game_gen[['Game','Genre']],how='left', on='Game')











###############################################################################
#Start building Streamlit App
   #game_details()
st.title('Esports Summery(1998 - 2021)')
st.text("")
col1,col2,col3 = st.columns(3)
with col1:
    st.metric(label= 'Total Number of Tournaments', value = (filterd_game['Tournaments'].sum()))
with col2:
     st.metric(label= 'Total prizepool(Billions)', value = '{0:.3g}'.format(((filterd_game['Earnings'].sum()/1000000000))))
with col3:
    st.metric(label= 'Number of  E-sports players', value = (filterd_game['Players'].sum()))
       
st.text("")     
   
    
   #prize pool evelution
col4,col5 = st.columns(2)
with col4:
    st.header('Esports Evolution')
    evolution_tuple = ('Earnings','Players','Tournaments')
    evolution = st.selectbox('Select :', evolution_tuple)
    evolution_graph = pd.DataFrame(filterd_game.groupby('year')[evolution].sum().reset_index()).sort_values(by = 'year')
    fig1 = px.line(evolution_graph, x="year", y= evolution,width=650, height=450)
    fig1.update_layout(hovermode="x unified")
    st.plotly_chart(fig1)
with col5:
    st.header('Genre - Prizepool Distribution')
    year_5 = reversed(tuple(set(filterd_game['year'])))
    select_year = st.selectbox('Select year:',year_5)
    genre_pie_df = filterd_game[filterd_game['year'] == select_year]
    genre_pie = genre_pie_df[genre_pie_df['year']==select_year] 
    fig2 = px.pie(genre_pie,values='Earnings',names = 'Genre',color_discrete_sequence=px.colors.sequential.RdBu,hole = .5)
    st.plotly_chart(fig2)


   
col6,col7 = st.columns(2)
with col6:
    st.header('Esports Evolution')
    genre_tuple = ('Fighting','FPP','TPP','Sports','Racing','Strategy','MOBA','Card','Puzzle','BR','RPG')
    genres = st.selectbox('Select genre:',genre_tuple)
    mode = st.radio(" ",('Earnings','Tournaments'))
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    if mode == 'Earnings':
        genre_prize = filterd_game[filterd_game['Genre'] == genres]
        genre_pool = pd.DataFrame(genre_prize.groupby('year')['Earnings'].sum().reset_index()).sort_values(by = 'year')
        fig3 = px.line(genre_pool, x="year", y="Earnings")
        fig3.update_layout(hovermode="x unified")
        st.plotly_chart(fig3)
    else:
        genre_prize = filterd_game[filterd_game['Genre'] == genres]
        genre_pool = pd.DataFrame(genre_prize.groupby('year')['Tournaments'].sum().reset_index()).sort_values(by = 'year')
        fig3 = px.line(genre_pool, x="year", y="Tournaments")
        fig3.update_layout(hovermode="x unified")
        st.plotly_chart(fig3)
    
with col7:
    st.header('Popular Games')
    fields = ('TotalEarnings','TotalTournaments')
    field = st.selectbox('Select field:',fields)
    most_popular = df_game_gen.sort_values(by=field,ascending = False).reset_index().loc[:9]
    gamelist = list(most_popular['Game'])
    fig4 = px.bar(most_popular,x=field, y='Game',color='Genre')
    fig4.update_yaxes(categoryorder='array', categoryarray=gamelist)
    st.plotly_chart(fig4)
    
df_teams['Game'].value_counts()
    
st.header('Popular Teams&Players')
game_tuple = tuple(set(df_teams['Game']))
games1 = st.selectbox('Select:',game_tuple)
mode1 = st.radio(" ",('Teams','Players'))
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
if mode1 == 'Teams':
    top_teams = df_teams[df_teams['Game'] == games1].sort_values(by='TotalUSDPrize',ascending = False).reset_index().loc[:9]
    fig5 = px.bar(top_teams,x='TeamName',y='TotalUSDPrize' ,color = 'TotalUSDPrize',hover_name='TotalTournaments',width = 1200,height=500)
    st.plotly_chart(fig5)
else:
    df_players['CountryCode'] = df_players['CountryCode'].apply(lambda x: x.upper())
    df_countries = df_countries.rename(columns={'Two_Letter_Country_Code':'CountryCode'})
    top_players = df_players[df_players['Game'] == games1].sort_values(by='TotalUSDPrize',ascending = False).reset_index().loc[:9]
    top_players = pd.merge(top_players, df_countries,how='left', on='CountryCode')
    fig6 = px.bar(top_players, x='CurrentHandle', y='TotalUSDPrize',hover_name= 'Country_Name',color='TotalUSDPrize',width = 1200,height=500)
    st.plotly_chart(fig6)


st.header('Player Distribution')
df_players['CountryCode'] = df_players['CountryCode'].apply(lambda x: x.upper())
df_countries = df_countries.rename(columns={'Two_Letter_Country_Code':'CountryCode'})
df = pd.merge(df_players, df_countries,how='left', on='CountryCode')
player_country = pd.DataFrame(df.groupby('Three_Letter_Country_Code')['PlayerId'].count().sort_values(ascending=False).reset_index())
player_country = pd.merge(player_country,df[['Three_Letter_Country_Code','Country_Name']],how='left',on = 'Three_Letter_Country_Code')
plot = px.choropleth(player_country , locations="Three_Letter_Country_Code",color ='PlayerId',hover_name='Country_Name',width = 1200,height=600)
st.plotly_chart(plot)


