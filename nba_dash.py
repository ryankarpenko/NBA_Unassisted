# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 14:43:45 2020

@author: penko
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd


#p = pd.read_pickle("./stats-2013-2020.pkl")
p = pd.read_pickle("C://Users//penko//OneDrive//Documents//GitHub//NBA_Assisted//stats-2013-2020.pkl")

#teamcolors = pd.read_pickle("./teamcolors.pkl")
teamcolors = pd.read_pickle("C://Users//penko//OneDrive//Documents//GitHub//NBA_Assisted//teamcolors.pkl")

seasons = pd.DataFrame([{'label': '2013-14', 'value': 2013}, {'label': '2014-15', 'value': 2014}, {'label': '2015-16', 'value': 2015}, {'label': '2016-17', 'value': 2016}, {'label': '2017-18', 'value': 2017}, {'label': '2018-19', 'value': 2018}, {'label': '2019-20', 'value': 2019}])

# Python
#teamorder = ['None','ATL','BOS','BKN','CHA','CHI','CLE','DAL','DEN','DET','GSW','HOU','IND','LAC','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL','PHI','PHX','POR','SAC','SAS','TOR','UTA','WAS']

def flatten(first_item, second_item, list_item):
    return [val for sublist in [ first_item, second_item, list_item ] for val in sublist]

sizeref_total = 2. * max(p['fga_pg']) / (15 ** 2)

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
    html.Div([        
        html.Div([
            dcc.Dropdown(
                id='team_selection',
                options=[ {'label': t['FullTeam'], 'value': t['Team']} for i, t in teamcolors.iterrows() ],
                multi = True,
                value=[]
            )
        ],style={'width': '48%', 'display': 'inline-block'})
    ])
    ,

    dcc.Graph(id='ast_plot'),

    html.Div([
        html.Div([
            dcc.Slider(
                id='season_slider',
                min=seasons['value'].min(),
                max=seasons['value'].max(),
                value=seasons['value'].max(),
                marks={s['value']: {'label': s['label'], 'style': {'white-space':'nowrap'}} for i,s in seasons.iterrows()},
                step=None,
                included=False
            )
        ])
    ],style={'margin': '0 auto', 'display': 'block', 'width': '75%'})
])

@app.callback(
    Output('ast_plot', 'figure'),
    [Input('season_slider', 'value'),
     Input('team_selection', 'value')])

def update_graph(season_choice, team_choice):
    df = p[p['season_id'] == season_choice]

    opacity = [ (0.7 if t in team_choice else 0.5) for t in df['team'] ]
    df['opacity'] = opacity
    color = [ (player['hex.1'] if player['team'] in team_choice else 'lightgrey') for i,player in df.iterrows() ]
    df['mark_color'] = color
    priority_bits = [ (1 if c != 'lightgrey' else 0) for c in color]
    df['priority'] = priority_bits
    df.sort_values(by=['priority'], inplace=True)


    return {
        'data': [dict(
            x = df['pct_fgm_ast'],
            y = df['efg_pct'],
            title = 'Assisted Field Goals vs. Efficiency',
            text = df['player'],
            mode='markers',
            marker={
                'size': df['fga_pg'],
                'sizemode': 'area',
                'opacity': df['opacity'],
                'sizeref': sizeref_total,
                'color': df['mark_color'],
                'line': {'width': 0, 'color': 'white'}
            }
        )],
        'layout': dict(
            title={'text': 'Assisted Field Goals vs. Efficiency'},
            xaxis={
                'title': 'Percent of Field Goals Assisted',
                'type': 'linear',
                'range': [8,102]
            },
            yaxis={
                'title': 'Effective Field Goal Percentage',
                'type': 'linear',
                'range': [30,75]
            },
            #margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == '__main__':
    app.run_server(debug=False)