import plotly.express as px
import os
import pandas as pd
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi
from usa_token import kaggle_username, kaggle_key


def download_dataset():
    api = KaggleApi()
    api.set_config_value('username', kaggle_username)
    api.set_config_value('key', kaggle_key)
    api.authenticate()
    
    dataset = 'piterfm/massive-missile-attacks-on-ukraine'
    path = './dados'
    api.dataset_download_files(dataset, path=path, unzip=True)
    print(f"Dataset {dataset} baixado com sucesso!")


def process_dataset(data):
    data.drop(columns=['time_end', 'model', 'launch_place', 'target', 'destroyed_details', 'carrier', 'source'], inplace=True)
    data['time_start'] = data['time_start'].astype(str).apply(lambda x: x.split(' ')[0])
    data.rename(columns={'time_start': 'date'}, inplace=True)
    data['date'] = pd.to_datetime(data['date']).dt.date
    return data


def monthly_interception_rate(data):
    data['date'] = pd.to_datetime(data['date'])
    monthly_data = data.resample('M', on='date').sum().reset_index()
    monthly_data['interception_rate'] = (monthly_data['destroyed'] / monthly_data['launched'] * 100).fillna(0).round(0).astype(int)
    monthly_data['interception_rate'] = monthly_data['interception_rate'].astype(str) + '%'
    monthly_data['date'] = monthly_data['date'].dt.strftime('%Y-%m')
    return monthly_data


def plot_data(data):
    fig = px.bar(data, x='date', y=['launched', 'destroyed'],
                 labels={'value': 'Contagem', 'variable': 'Categoria'},
                 color_discrete_map={'launched': 'darkblue', 'destroyed': 'darkgray'},
                 barmode='group')
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        title='Mísseis Lançados vs Destruídos ao Longo do Tempo',
        xaxis_title='Data',
        yaxis_title='Número de Mísseis',
        xaxis=dict(
            title_font=dict(size=18, color='black'),
            tickfont=dict(size=16, color='black'),
            rangeslider=dict(visible=True),
            type='date'
        ),
        yaxis=dict(
            title_font=dict(size=20, color='black'),
            tickfont=dict(size=18, color='black'),
            range=[0, 110]
        )
    )
    return fig


def plot_interception_rate(data):
    fig = px.line(data, x='date', y='interception_rate', color_discrete_sequence=['darkblue'])
    fig.update_traces(line=dict(width=4))
    fig.update_layout(
        title='Taxa de Interceptação Média Mensal ao Longo do Tempo',
        xaxis_title='Mês',
        yaxis_title='Taxa de Interceptação (%)',
        xaxis=dict(
            title_font=dict(size=18, color='black'),
            tickfont=dict(size=16, color='black'),
            tickangle=-90,
            tickmode='linear',
            dtick='M1',
            rangeslider=dict(visible=True),
            type='date'
        ),
        yaxis=dict(
            title_font=dict(size=20, color='black'),
            tickfont=dict(size=18, color='black'),
            range=[50, 100]
        )
    )
    return fig


def exibir_graficos(data):
    data_processed = process_dataset(data.copy())
    st.subheader("Mísseis Lançados vs Destruídos ao Longo do Tempo")
    fig1 = plot_data(data_processed)
    st.plotly_chart(fig1)

    st.subheader("Taxa de Interceptação Média Mensal ao Longo do Tempo")
    monthly_data = monthly_interception_rate(data_processed)
    fig2 = plot_interception_rate(monthly_data)
    st.plotly_chart(fig2)


root = os.getcwd()
dados_dir = f'{root}/dados'

if st.sidebar.button('Download dos dados', type="primary"):
    download_dataset()
    data = pd.read_csv(f"{root}/dados/missile_attacks_daily.csv")
    exibir_graficos(data)
