import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from functions import calc_log
import math

class Coronavirus:
    
    def __init__(self):
        self.data = self.get_all_data()
        self.data = self.add_world()
        self.types = ['confirmed', 'recovered', 'deaths']
        self.colors = dict(zip(self.types, ['#3182bd', '#31a354', '#de2d26']))
        self.countries = self.get_all_countries()

    def add_world(self):
        world = self.data.loc[:, 'type': ].groupby(['type'], as_index=False).sum()
        world.insert(loc=0, column='Country/Region', value='World')
        world.insert(loc=0, column='Province/State', value='World')
        return pd.concat([self.data, world]).reset_index().drop(columns=['index'])


    def get_all_data(self):
        confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')
        deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv')
        recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv')
        confirmed.insert(loc=4, column='type', value='confirmed')
        deaths.insert(loc=4, column='type', value='deaths')
        recovered.insert(loc=4, column='type', value='recovered')
        return pd.concat([confirmed, recovered, deaths])

    def get_country_summary(self, country, province = None):
        df = self.data.loc[self.data['Country/Region'] == country]
        if province:
            df = df.loc[df['Province/State'] == province]
        df = df.loc[:, 'type' : ].groupby(['type']).sum()
        df = df.transpose()
        df.index.name = 'date'
        df.reset_index(inplace=True)
        df['date']  = df['date'].apply(self.format_date)
        return df
        
    def format_date(self, date):
        parts = date.split('/')
        parts[0], parts[1] = parts[1], parts[0]
        return '/'.join(parts)

    def get_all_countries(self):
        countries = self.data['Country/Region'].unique().tolist()
        countries.sort()
        return [{'label' : country, 'value' : country} for country in countries]

    def get_country_data(self, country):
        df = self.get_country_summary(country)
        return [dict(
                    x = df.date,
                    y = df[type_],
                    name = type_,
                    marker = dict(color = self.colors[type_])) for type_ in self.types]
        
    def get_country_rate_data(self, country): # as a difference between next days confirms (in people)
        df = self.get_country_summary(country)
        df['prev'] = df.shift(periods=1, fill_value=df['confirmed'][0])['confirmed']
        df['rate'] = df['confirmed'] - df['prev']
        return [dict(
                    x = df.date,
                    y = df['rate'],
                    name = 'rate',
                    marker = dict(color = self.colors['confirmed']))]

    def overall_stats(self, country):
        df = self.data.loc[self.data['Country/Region'] == country, ['type', self.data.columns[-1]]]
        df = df.groupby(['type'], as_index=False).sum()
        df.columns = ['type', 'summary']
        df.sort_values('summary', inplace=True)
        plot = []
        for i, row in df.iterrows():
            plot.append(
                dict(
                    x = [row['type']],
                    y = [row['summary']],
                    type = 'bar',
                    name = row['type'],
                    marker = dict(color = self.colors[row['type']])
                    ))
        return plot

    def comparison_bars(self, type_, range_val):
        #breakpoint()
        df = self.data.loc[self.data['type'] == type_].groupby(['Country/Region'], as_index=False).sum()
        df = df.loc[: , ['Country/Region', df.columns[-1]]]
        df.columns.values[-1] = 'summary'
        df.sort_values('summary', inplace=True)
        df = df.loc[(df['summary'] <= range_val[1]) & (df['summary'] >= range_val[0]), :]
        plot = []
        countries_colors = sns.color_palette(n_colors=len(self.countries)).as_hex()
        for i, row in df.iterrows():
            plot.append(
                dict(
                    x = [row['Country/Region']],
                    y = [row['summary']],
                    type = 'bar',
                    name = row['Country/Region'],
                    marker = dict(color = countries_colors[i]),
                    ))
        return plot

    def prepare_map_data(self):
        df = self.data.loc[(self.data['type'] == 'confirmed') & (self.data['Country/Region'] != 'World')]
        
        def make_label(row):
            label = []
            label.append(row['Country/Region'])
            if not pd.isna(row['Province/State']):
                label.append(row['Province/State'])
            label.append(row['type'] + ': ' + str(row['size']))
            return ', '.join(label)

        df.insert(loc=0, column='size', value=df.iloc[:, -1])
        df.insert(loc=0, column='text', value=df.apply(make_label, axis=1))
        df = df.loc[:, : 'type']
        #breakpoint()
        def scale_size(df):
            max_size = df.loc[:, 'size'].max()
            df['size'] = df.apply(lambda x : math.pow(x['size'], 1/3), axis = 1)
            return df

        df = scale_size(df)
        #breakpoint()
        fig = go.Figure(data=go.Scattergeo(
            lon = df['Long'],
            lat = df['Lat'],
            text = df['text'],
            mode = 'markers',
            marker = dict(
                size = df['size'],
                color='#ef3b2c'
            )
        ))
        fig.update_layout(
            #title = f'Virus spreading in the world',
            autosize=True,
            hovermode='closest',
            margin=dict(t=0, b=0, l=0, r=0),
            geo_scope='world',
        )
        return fig