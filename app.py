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

covid = Coronavirus()

#country = 'Poland'
#dat = covid.get_country_data(country)

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
                        [
                            f'''
                                Coronavirus disease 2019 (COVID-19) is an infectious disease caused by the severe acute respiratory
                                syndrome coronavirus 2 (SARS-CoV-2).[9] The disease has spread globally since 2019, resulting in the 2019–20 coronavirus pandemic.[10][11] 
                                Common symptoms include fever, cough and shortness of breath. Muscle pain, sputum production and sore throat are less 
                                common symptoms.[6][12] While the majority of cases result in mild symptoms,[13] some progress to pneumonia and multi-organ failure.[10][14] 
                                The deaths per number of diagnosed cases is estimated at between 1% and 5% but varies by age and other health conditions.[15][16]

                                Source: Wikipedia
                            '''
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
                            html.H4('Range of people shown'),
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
                                '''* This application provides information and statistics about COVID-19. Data is being gathered from
                                    **[source](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)**
                                    (it's being updated once a day).
                                ''',
                                style = {'line-height' : '0.2'}
                            ),
                            dcc.Markdown(
                                '''* Application was written with Python [Dash](https://dash.plot.ly/) framework and custom CSS.''',
                                style = {'line-height' : '0.2'}
                            ),
                            html.P(
                                'Piotr Olesiejuk (c) 2020',
                                style={'line-height' : '2', 'margin-bottom' : '0px', 'padding-bottom' : '0px'}
                            )
                        ],
                        id='footer',
                        className='tile')
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
    [Input('country-choose-main', 'value')])
def update_country_summary_data(value):
    global covid
    return {
            'data': covid.get_country_data(value),
            'layout': {
                'title': f'People infected in {value}',
                'font' : font()
            }
        }

@app.callback(
    Output('country-rate-graph','figure'),
    [Input('country-choose-rate', 'value')]
)
def update_growing_rate_data(value):
    global covid
    return {
        'data' : covid.get_country_rate_data(value),
        'layout' : {
            'title' : f'Increase in number infected comparing to previuos day in {value}',
            'font' : font()
        }
    }

@app.callback(
    Output('overall-stats', 'figure'),
    [Input('country-choose-stats', 'value')]
)
def update_overall_stats(value):
    global covid
    return {
        'data' : covid.overall_stats(value),
        'layout' : {
            'title' : f'Summary statistics for {value}',
            'font' : font()
        }
    }

@app.callback(
    Output('type-comparison', 'figure'),
    [Input('type-choose-comparison', 'value'),
    Input('slider', 'value')]
)
def update_comparison(type_, range_val):
    global covid
    range_val = [10**val for val in range_val]
    return {
        'data' : covid.comparison_bars(type_, range_val),
        'layout' : {
            'title' : f'Countries comparison over {type_} people',
            'font' : font(),
            'showlegend' : False
        }
    }

@app.callback(
    Output('slider', 'max'), 
    [Input('type-choose-comparison', 'value')]
)
def update_slider_max(type_):
    global covid
    max_ = covid.data.loc[(covid.data['Country/Region'] == 'World') & (covid.data['type'] == type_)].iloc[:, -1]
    return calc_log(int(max_))

@app.callback(
    Output('slider', 'min'), 
    [Input('type-choose-comparison', 'value')]
)
def update_slider_min(value):
    return 0

@app.callback(
    Output('slider', 'value'),
    [Input('type-choose-comparison', 'value')]
)
def update_slider_values(type_):
    global covid
    max_ = covid.data.loc[(covid.data['Country/Region'] == 'World') & (covid.data['type'] == type_)].iloc[:, -1]
    return (0, calc_log(int(max_)))

@app.callback(
    Output('slider', 'marks'),
    [Input('type-choose-comparison', 'value')]
)
def update_slider_marks(type_):
    global covid
    max_ = int(covid.data.loc[(covid.data['Country/Region'] == 'World') & (covid.data['type'] == type_)].iloc[:, -1])
    marks = {i: {'label' : str(10**i) } for i in range(0, max_,)}
    return marks

# @app.callback(
#     Output('map', 'figure'),
#     [Input('map-dropdown', 'value')]
# )
# def update_map(value):
#     global covid
#     return covid.prepare_map_data(value)

if __name__ == '__main__':
    app.run_server(debug=True)