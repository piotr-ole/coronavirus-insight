# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from coronavirus import Coronavirus
from functions import calc_log
import os


app = dash.Dash(__name__)
app.title = 'Coronavirus insight'
app.head = [
    html.Link(
          rel="stylesheet",
          href="https://fonts.googleapis.com/css?family=Tangerine"
    )]

server = app.server

covid = Coronavirus()

app.layout = html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    'Coronavirus insight'
                                ],
                                id='title'
                            ),
                            html.Div(
                                [
                                    html.Img(
                                        id='logo-image',
                                        src=app.get_asset_url('logo.png'),
                                    )
                                ],
                                id = 'logo'
                            )
                        ],
                        id = 'top-block'
                    ),
                    html.Div([], style = {'clear' : 'both'}), # empty div to clear floating formatting
                    html.Div(
                        ['"I have no idea what\'s awaiting me, or what will happen when this all ends. For the moment I know this: there are sick people and they need curing."'
                        ],
                        id='inspiring-quote'
                            ),
                    html.Div(
                        ["Albert Camus, The Plague"
                        ],
                        id='quote-author'
                            ),
                    html.Div(
                        [
                            dcc.Markdown(f'''
                                "Coronaviruses (CoV) are a large family of viruses that cause illness ranging from the common cold to more severe
                                 diseases such as Middle East Respiratory Syndrome (MERS-CoV) and Severe Acute Respiratory Syndrome (SARS-CoV). 
                                 Coronavirus disease (COVID-19) is a new strain that was discovered in 2019 and has not been previously identified in humans.
                                 Coronaviruses are zoonotic, meaning they are transmitted between animals and people.  Detailed investigations found that SARS-CoV was transmitted
                                 from civet cats to humans and MERS-CoV from dromedary camels to humans. Several known coronaviruses are circulating in animals
                                 that have not yet infected humans.Common signs of infection include respiratory symptoms, fever, cough, shortness of breath and breathing difficulties. In more severe cases,
                                 infection can cause pneumonia, severe acute respiratory syndrome, kidney failure and even death. "
 

                                Source: [WHO](https://www.who.int/health-topics/coronavirus)

                                More from WHO: [Myths about coronavirus](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters)
                            ''', id='info-text')
                        ], 
                        id='info'
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id='map',
                                figure=covid.prepare_map_data()
                            )
                        ],
                        id='map-container'
                    ),
                    html.Div([], style = {'clear' : 'both'}), # empty div to clear floating formatting
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='country-choose-main',
                                options=covid.countries,
                                value='China'
                            ),
                            dcc.Graph(
                                id='country-summary-graph'
                            )
                        ],
                        className='tile', id='country-timeseries'
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='country-choose-stats',
                                options=covid.countries,
                                value='China'
                            ),
                            dcc.Graph(
                                id='overall-stats'
                            )
                        ],
                        className='tile',
                        id = 'country-summary'
                    ),
                    html.Div(
                        [                        
                            dcc.Dropdown(
                                id='country-choose-rate',
                                options=covid.countries,
                                value='China'
                            ),
                            dcc.Graph(
                                id='country-rate-graph'
                            )
                        ],
                        className='tile',
                        id='rate-graph'
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='type-choose-comparison',
                                options=[{'label': v, 'value': v} for v in covid.types],
                                value='deaths'
                            ),
                            html.Div(
                                [
                                    dcc.Graph(
                                        id='type-comparison'
                                    )
                                ]
                            ),
                            html.H4('Range of people:'),
                            dcc.RangeSlider(
                                id= 'slider',
                                step=1,
                                allowCross=False,
                            )
                        ],
                        className='tile',
                        id='world-comparison-graph'
                    ),
                    html.Div([], style={'clear' : 'both'}), # empty div to clear floating formatting
                    html.Div(
                        [
                            html.H4('Information', style = {'margin' : '0px'}),
                            dcc.Markdown(
                                '''* This application provides information and statistics about COVID-19. Data is gathered from
                                    **[source](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)**
                                    (it's updated once a day).
                                ''',
                                style = {'line-height' : '0.2'}
                            ),
                            dcc.Markdown(
                                '''* Application was developed with Python [Dash](https://dash.plot.ly/) framework and custom CSS.''',
                                style = {'line-height' : '0.2'}
                            ),
                            html.P(
                                'Piotr Olesiejuk (c) 2020',
                                style={'line-height' : '2', 'margin-bottom' : '0px', 'padding-bottom' : '0px'}
                            )
                        ],
                        id='footer',
                        className='tile'),
                        html.Div(children=[covid.to_json()], id='data-json', style={'display': 'none'})
                ],
                id ='main-container'
            )

def font():
    return  {
                'family' : "Open Sans",
                'size' : 14,
                'color' : "#000000"
            }

@app.callback(
    Output('country-summary-graph','figure'),
    [Input('country-choose-main', 'value'),
    Input('data-json', 'children')])
def update_country_summary_data(country, children):
    covid = Coronavirus(json=children[0], from_json=True)
    return {
            'data': covid.get_country_data(country),
            'layout': {
                'title': f'People infected in {country}',
                'font' : font()
            }
        }

@app.callback(
    Output('country-rate-graph','figure'),
    [Input('country-choose-rate', 'value'),
    Input('data-json', 'children')]
)
def update_growing_rate_data(country, children):
    covid = Coronavirus(json=children[0], from_json=True)
    return {
        'data' : covid.get_country_rate_data(country),
        'layout' : {
            'title' : f'Increase in number infected comparing to previuos day in {country}',
            'font' : font()
        }
    }

@app.callback(
    Output('overall-stats', 'figure'),
    [Input('country-choose-stats', 'value'),
    Input('data-json', 'children')]
)
def update_overall_stats(country, children):
    covid = Coronavirus(json=children[0], from_json=True)
    return {
        'data' : covid.overall_stats(country),
        'layout' : {
            'title' : f'Summary statistics for {country}',
            'font' : font(),
            'showlegend' : False
        }
    }

@app.callback(
    Output('type-comparison', 'figure'),
    [Input('type-choose-comparison', 'value'),
    Input('slider', 'value'),
    Input('data-json', 'children')]
)
def update_comparison(type_, range_val, children):
    covid = Coronavirus(json=children[0], from_json=True)
    if not range_val:
        raise dash.exceptions.PreventUpdate
    range_val = [10**val if val >= 0 else 0 for val in range_val ]
    return {
        'data' : covid.comparison_bars(type_, range_val),
        'layout' : {
            'title' : f'Countries comparison over {type_} people',
            'font' : font(),
            'showlegend' : False
        }
    }

@app.callback(
    [Output('slider', 'min'), Output('slider', 'max'),
    Output('slider', 'value'), Output('slider', 'marks')],
    [Input('type-choose-comparison', 'value'),
    Input('data-json', 'children')]
)
def update_slider(type_, children):
    covid = Coronavirus(json=children[0], from_json=True)
    max_ = covid.data.loc[(covid.data['Country'] == 'World') & (covid.data['type'] == type_)].iloc[:, -1]
    log_max = calc_log(int(max_))
    marks = {i: {'label' : str(10**i) } for i in range(0, log_max + 1)} # + 1 because we want to include biggest value
    marks[-1] = {'label' : '0'}
    return [-1, log_max, (-1, log_max), marks]

if __name__ == '__main__':
    app.run_server(debug=True)