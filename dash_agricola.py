import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import geopandas as gpd


# ======================== Leitura dos dados =========================== #

gdf = gpd.read_file('https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-23-mun.json')
df_prod = pd.read_csv("df_producao_novo.csv")   # Produção agricola
df_area = pd.read_csv("df_area_novo.csv")       # Aréa plantada
df_rend = pd.read_csv("df_rendimento_novo.csv") # Rendimento agrícola

df_prod = df_prod[df_prod['ano']>=1988]
df_area = df_area[df_area['ano']>=1988]

# ===================== Funções e variavéis uteis ====================== #
years = df_prod['ano'].unique()

card_style = {
    "margin-top": "10px",
    "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
    "color": "#FFFFFF"}

config_graph={"displayModeBar": False, "showTips": False}

def filtro1(dfp, dfa, start_year, end_year):
        df_prod1 =  dfp[(dfp['ano'] >=start_year) & (dfp['ano'] <= end_year)]
        df_area1 = dfa[(dfa['ano'] >=start_year) & (dfa['ano'] <= end_year)]
        return df_prod1, df_area1

def filtro2(df_prod1, municipio, df_area1):
    prod_media_mun = df_prod1[df_prod1['mun'] == municipio]['total'].mean().round(2)
    area_media_mun = df_area1[df_area1['mun'] == municipio]['total'].mean().round(2)
    rend_media_mun = prod_media_mun*1000/area_media_mun
    return prod_media_mun, area_media_mun, rend_media_mun

# ========================== mapa do ceará ============================ #

df_prod2 = df_prod[df_prod['ano'] == 2007]
df_prod2.loc[:,'cod'] = df_prod2['cod'].astype('str')

fig_mapa = px.choropleth_mapbox(
    df_prod2,                           # df com os dados que deseja plotar
    locations="cod",                    # Coluna do seu df com os códigos dos municípios
    color="total",                      # Coluna do df usada para colorir o mapa
    geojson=gdf,                        # GeoDataFrame com as geometrias dos municípios
    featureidkey="properties.id",       # Chave de identificação no GeoJSON
    mapbox_style="carto-positron",      # Estilo do mapa
    center={"lat": -5.2, "lon": -39.6},
    zoom=6.5,
    opacity=0.8,
    labels={'total':'Total'},
    color_continuous_scale="Brwnyl",
    hover_name = 'mun',
    hover_data = { "ano":True,'total':True, "cod":False},
    range_color = [0, 20000]
    
)
fig_mapa.update_layout(
    paper_bgcolor="#242424",
    mapbox_style="carto-darkmatter",
    autosize=True,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False,
    font=dict(color='white')
)

# ========================== Indicadores iniciais ====================== #



# ========================== Layout do dash ============================ #
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([

    dbc.Row([

        dbc.Col([
            
            html.Div([
            
                dbc.Row([
                    html.H5(id='titulo-text', 
                    children='Produção Agrícola - Ceará', 
                    style={'text-align':'center', 'margin-top':'10px', 'margin-bottom':'45px'}),
                ])
            
            ]),

            html.Div([

                dbc.Row([

                    dbc.Col([
                        html.H6('Esolha a safra:', style={'margin-top':'-20px'}),   
                        dcc.Checklist(options=[
                            {'label':'Feijão', 'value':'feijao'},
                            {'label':'Milho', 'value':'milho'}], id='chek_prod', value=['feijao', 'milho'],
                            inputStyle={'margin-top':'5px', 'margin-right':'5px'},
                            labelStyle={'display': 'block'}
                            ),
                        ]),
                    
                    dbc.Col([
                        html.P("Ano início: ", style={"margin-top":"-20px", "color": "white"}),
                        dcc.Dropdown(
                            id='start-year',
                            options=[{'label': str(year), 'value': year} for year in years],
                            value=years[0])
                        ]),

                    dbc.Col([
                        html.P("Ano fim: ", style={"margin-top":"-20px", "color": "white"}),
                        dcc.Dropdown(
                            id='end-year',
                            options=[{'label': str(year), 'value': year} for year in years],
                            value=years[-1])
                    ])
                    
                ]),

                dbc.Row([
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span("Produção média anual:", style={'font-size':'16px'}),
                                html.H6(id="prod-media-text", style={"color":"#adfc92"}),

                            ])
                        ], style=card_style)
                    ], sm=4),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span("Área plantada média:", style={'font-size':'16px'}),
                                html.H6(id="area-media-text", style={"color":"#adfc92"})
                            ])
                        ], style=card_style)
                    ], sm=4),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span("Rendimento médio:", style={'font-size':'16px'}),
                                html.H6(id="rend-medio-text", style={"color":"#adfc92"})
                            ])
                        ], style=card_style)
                    ], sm=4)
                ], style={'margin-top':'10px'}),

                dbc.Row([
                    html.P('Produção agrícola (t)', style={"margin-top":"15px", "color":"white"}),
                    dcc.Graph(id='serie-prod', style={"background-color": "#242424"}, config=config_graph)
                ], style={"background-color": "#1E1E1E", "margin": "-25px", "padding": "25px"}),

                dbc.Row([
                    html.P('Área plantada (ha)', style={"margin-top":"-5px", "color":"white"}),
                    dcc.Graph(id='serie-rend', style={"background-color": "#242424"}, config=config_graph)
                ], style={"background-color": "#1E1E1E", "margin": "-25px", "padding": "25px"})
                    
            ], style={"background-color": "#1E1E1E", "margin": "-25px", "padding": "25px"})

        ], sm = 6, style={"height":"100vh"}),
        
        dbc.Col([

            dcc.Graph(id='mapa-ceara', 
                figure=fig_mapa, config={"displayModeBar": False},
                style={"height":"100vh", "margin-right":"10px"},
                ),
            
#           html.Div(
#               id='municipio',
#               children='Ceará',
#               style={
#               'position': 'absolute',
#               'top': '50px',  # Posição vertical
#               'right': '200px',  # Posição horizontal
#               'backgroundColor': None,
#               'padding': '10px',
#               "color":"white",
#               'font-size':'30px'
#                }),
        
        ], sm = 6)
    ])


], fluid=True)

# ============================== Callbacks ============================= #
@app.callback(
    Output('end-year', 'options'),
    [Input('start-year', 'value')]
)
def update_end_year_options(selected_start_year):
    updated_years = [year for year in years if year >= selected_start_year]
    updated_options = [{'label': str(year), 'value': year} for year in updated_years]
    return updated_options


@app.callback(
    [
        Output('prod-media-text', 'children'),
        Output('area-media-text', 'children'),
        Output('rend-medio-text', 'children'),
        Output('titulo-text', 'children'),
    ],

    [
        Input('start-year', 'value'),
        Input('end-year', 'value'),
        Input('chek_prod', 'value'),
        Input('mapa-ceara', 'clickData')      
    ]
)
def render_graf1(start_year, end_year, chek_prod, clickData):

    if clickData and 'points' in clickData and clickData['points']:
        municipio = clickData['points'][0]['hovertext']
    
        if set(['feijao', 'milho']) == set(chek_prod):
            dfp = df_prod.loc[:, ['cod', 'mun', 'ano', 'total']]
            dfa = df_area.loc[:, ['cod', 'mun', 'ano', 'total']]
            df_prod1, df_area1 = filtro1(dfp, dfa, start_year, end_year)
            prod_media_mun, area_media_mun, rend_media_mun = filtro2(df_prod1, municipio, df_area1)
            
        elif ('feijao' in chek_prod) and ('milho' not in chek_prod):
            dfp = df_prod.loc[:, ['cod', 'mun', 'ano', 'feijao']]
            dfp.rename(columns={'feijao':'total'}, inplace=True)
            dfa = df_area.loc[:, ['cod', 'mun', 'ano', 'feijao']]
            dfa.rename(columns={'feijao':'total'}, inplace=True)
            df_prod1, df_area1 = filtro1(dfp, dfa, start_year, end_year)
            prod_media_mun, area_media_mun, rend_media_mun = filtro2(df_prod1, municipio, df_area1)


        elif ('feijao' not in chek_prod) and ('milho' in chek_prod):
            dfp = df_prod.loc[:, ['cod', 'mun', 'ano', 'milho']]
            dfp.rename(columns={'milho':'total'}, inplace=True)
            dfa = df_area.loc[:, ['cod', 'mun', 'ano', 'milho']]
            dfa.rename(columns={'milho':'total'}, inplace=True)
            df_prod1, df_area1 = filtro1(dfp, dfa, start_year, end_year)
            prod_media_mun, area_media_mun, rend_media_mun = filtro2(df_prod1, municipio, df_area1)

        else:
            prod_media_mun = 0
            area_media_mun = 0
            rend_media_mun = 0
    
        texto = f'Produção Agrícola - {municipio}'

        return str(int(prod_media_mun)) + " ton.", str(int(area_media_mun)) + ' ha', str(int(rend_media_mun)) + ' kg/ha', texto

    else:

        df_prod3 = df_prod[(df_prod['ano']>=start_year) & (df_prod['ano'] <= end_year)]
        df_area3 = df_area[(df_area['ano']>=start_year) & (df_area['ano'] <= end_year)]

        if set(['feijao', 'milho']) == set(chek_prod):
            df_prod3 = df_prod3.copy()
            df_area3 = df_area3.copy()
            prod_media_anual = df_prod3.groupby('ano')['total'].sum().mean().round(2)
            area_media_anual = df_area3.groupby('ano')['total'].sum().mean().round(2)
            rend_media_anual = (prod_media_anual*1000/area_media_anual).round(2)
        
        elif ('feijao' in chek_prod) and ('milho' not in chek_prod):
            df_prod3 = df_prod3.loc[:, ['cod', 'mun', 'ano', 'feijao']].rename(columns={'feijao':'total'})
            df_area3 = df_area3.loc[:, ['cod', 'mun', 'ano', 'feijao']].rename(columns={'feijao':'total'})
            prod_media_anual = df_prod3.groupby('ano')['total'].sum().mean().round(2)
            area_media_anual = df_area3.groupby('ano')['total'].sum().mean().round(2)
            rend_media_anual = (prod_media_anual*1000/area_media_anual).round(2)

        elif ('feijao' not in chek_prod) and ('milho' in chek_prod):
            df_prod3 = df_prod3.loc[:, ['cod', 'mun', 'ano', 'milho']].rename(columns={'milho':'total'})
            df_area3 = df_area3.loc[:, ['cod', 'mun', 'ano', 'milho']].rename(columns={'milho':'total'})
            prod_media_anual = df_prod3.groupby('ano')['total'].sum().mean().round(2)
            area_media_anual = df_area3.groupby('ano')['total'].sum().mean().round(2)
            rend_media_anual = (prod_media_anual*1000/area_media_anual).round(2)
        
        else:

            prod_media_anual = 0#df_prod3.groupby('ano')['total'].sum().mean().round(2)
            area_media_anual = 0#df_area3.groupby('ano')['total'].sum().mean().round(2)
            rend_media_anual = 0#(prod_media_anual*1000/area_media_anual).round(2)


        return f"{prod_media_anual} ton", f"{area_media_anual} ha", f"{rend_media_anual} kg/ha", 'Produção Agrícola - Ceará' 

@app.callback(
    [
        Output('serie-prod', 'figure'),
        Output('serie-rend', 'figure'),
    ],
    
    [
        Input('mapa-ceara', 'clickData')
    ]
)

def rander_graficos(clickData):

    if clickData and 'points' in clickData and clickData['points']:
        municipio = clickData['points'][0]['hovertext']
        df_prod_mun = df_prod[df_prod['mun'] == municipio]
        df_area_mun = df_area[df_area['mun'] == municipio]

        fig = go.Figure()

        fig.add_trace(go.Bar(x=df_prod_mun['ano'], y=df_prod_mun['feijao'], name='Feijão', marker_color='#E45756'))
        fig.add_trace(go.Bar(x=df_prod_mun['ano'], y=df_prod_mun['milho'], name='Milho', marker_color='rgb(241,226,204)'))

        fig2 = px.line()

        fig2.add_scatter(x = df_area_mun['ano'], y = df_area_mun['feijao'], name='Feijão', line_color='#E45756')
        fig2.add_scatter(x = df_area_mun['ano'], y = df_area_mun['milho'], name='Milho', line_color='rgb(241,226,204)')
        fig2.update_traces(mode='lines+markers')

    else:
        prod_ce = df_prod.groupby('ano')[['feijao', 'milho','total']].sum().reset_index()
        df_area_ce = df_area.groupby(['ano'])[['total', 'feijao', 'milho']].sum().reset_index()
        
        fig = go.Figure()

        fig.add_trace(go.Bar(x=prod_ce['ano'], y=prod_ce['feijao'], name='Feijão', marker_color='#E45756'))
        fig.add_trace(go.Bar(x=prod_ce['ano'], y=prod_ce['milho'], name='Milho', marker_color='rgb(241,226,204)'))

        fig2 = px.line()

        fig2.add_scatter(x = df_area_ce['ano'], y = df_area_ce['feijao'], name='Feijão', line_color='#E45756')        #'gray'
        fig2.add_scatter(x = df_area_ce['ano'], y = df_area_ce['milho'], name='Milho', line_color='rgb(241,226,204)') #'burlywood'
        fig2.update_traces(mode='lines+markers')
    
    fig.update_layout(barmode='group',
                        xaxis = dict(title="Ano"),
                        bargap = 0.3,
                        bargroupgap=0.01,
                        height=180,
                        paper_bgcolor="#242424",
                        autosize=True,
                        margin=dict(l=0, r=0, t=0, b=0),
                        font=dict(color='white'),
                        plot_bgcolor="#242424"
                        )
    
    fig2.update_layout(
            height=180, 
            xaxis=dict(title='Ano', showgrid=False),
            paper_bgcolor="#242424",
            margin=dict(l=0, r=0, t=0, b=10),
            font=dict(color='white'),
            plot_bgcolor="#242424"
         )

    return fig, fig2

@app.callback(
        Output('mapa-ceara', 'figure'),
    
    [
        Input('start-year', 'value'),
        Input('end-year', 'value'),
        Input('chek_prod', 'value')
    ]
)

def update_map(start_year, end_year, prod):

    df_prod2 = df_prod[(df_prod['ano'] >= start_year) & (df_prod['ano'] <= end_year)].groupby(['cod','mun'])[['feijao','milho','total']].mean().reset_index()
    df_prod2.loc[:,'cod'] = df_prod2['cod'].astype('str')

    if ('feijao' in prod) and ('milho' not in prod):
        dfp = df_prod2.loc[:,['cod','mun','feijao']].rename(columns={'feijao':'total'})
        reange_color = [0, 10000]

    elif ('feijao' not in prod) and ('milho' in prod):
        dfp = df_prod2.loc[:,['cod','mun','milho']].rename(columns={'milho':'total'})
        reange_color = [0, 20000]

    elif ('feijao' not in prod) and ('milho' not in prod):
        dfp = df_prod2.loc[:,['cod','mun','feijao','milho','total']]
        dfp.loc[:,'total'] = 0
        reange_color = [0, 20000]

    else:
        dfp = df_prod2.loc[:,['cod','mun','feijao','milho','total']]
        reange_color = [0, 20000]


    fig = px.choropleth_mapbox(
    dfp,                           # df com os dados que deseja plotar
    locations="cod",                    # Coluna do seu df com os códigos dos municípios
    color="total",                      # Coluna do df usada para colorir o mapa
    geojson=gdf,                        # GeoDataFrame com as geometrias dos municípios
    featureidkey="properties.id",       # Chave de identificação no GeoJSON
    mapbox_style="carto-darkmatter",      # Estilo do mapa
    center={"lat": -5.2, "lon": -39.6},
    zoom=6.5,
    opacity=0.8,
    labels={'total':'Total'},
    color_continuous_scale="Brwnyl",
    hover_name = 'mun',
    hover_data = {'total':True, "cod":False},
    range_color = reange_color
    )

    fig.update_layout(
        paper_bgcolor="#242424",
        mapbox_style="carto-darkmatter",
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        font=dict(color='white')
        )
    
    return fig

# ============================= Rodando o dash ========================= #
if __name__ == "__main__":
    app.run_server(debug=True, port=8053)