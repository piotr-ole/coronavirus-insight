import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from functions import calc_log
import math

class Coronavirus:
    
    def __init__(self, json = {}, from_json=False):
        if from_json:
            self.data = pd.read_json(json)
        else:
            self.data = self.get_all_data()
            self.data = self.add_world()
        self.types = ['confirmed', 'recovered', 'deaths']
        self.colors = dict(zip(self.types, ['#3182bd', '#31a354', '#de2d26']))
        self.countries = self.get_all_countries()

    def add_world(self):
        world = self.data.loc[:, 'type': ].groupby(['type'], as_index=False).sum()
        #world.insert(loc=0, column='Long', value='0')
        #world.insert(loc=0, column='Lat', value='0')
        world.insert(loc=0, column='Country', value='World')
        world.insert(loc=0, column='State', value='World')
        return pd.concat([self.data, world]).reset_index().drop(columns=['index']) # lat and long for world can be NaN

    def rename_columns(self, df):
        df.rename(columns={'Province/State':'State', 
                           'Country/Region':'Country'}, inplace=True)
        dates = df.columns.values[5:]
        new_dates = pd.to_datetime(dates).strftime('%d/%m').tolist()
        df.rename(columns=dict(zip(dates, new_dates)), inplace=True)
        return df

    def get_all_data(self):
        data_sources=pd.read_csv('data_sources.csv')
        dfs = [pd.read_csv(url) for url in data_sources['url']]
        for df, type_ in zip(dfs, data_sources['type']):
            df.insert(loc=4, column='type', value=type_) 
        df = pd.concat(dfs)
        #removing errors from datasource (negative values)
        errors_positions = df.loc[df.iloc[:, -1] < 0, ['Province/State', 'Country/Region']]
        keys = list(errors_positions.columns.values)
        index1 = df.set_index(keys).index
        index2 = errors_positions.set_index(keys).index
        df = df[~index1.isin(index2)]
        ###
        df = self.rename_columns(df)
        return df

    def remove_source_errors(self, df):
        errors = df.loc[df.iloc[:, -1] < 0, ['Province/State', 'Country/Region']]


    def to_json(self):
        return self.data.to_json()

    def get_country_summary(self, country, state = None):
        df = self.data.loc[self.data['Country'] == country]
        if state:
            df = df.loc[df['State'] == state]
        df = (df.loc[:, 'type' : ].groupby(['type'])
              .sum()
              .transpose()
             )
        df.index.name = 'date'
        df.reset_index(inplace=True)
        return df
        

    def get_all_countries(self):
        countries = self.data['Country'].unique().tolist()
        countries.sort()
        return [{'label' : country, 'value' : country} for country in countries]

    def plotly_graph_data(self, pandas_df, *, x_var, y_var, plot_type, legend_var,
                          marker_color, convert_args_to_list=False):
        def transform_data(arg, convert_args_to_list):
            if convert_args_to_list:
                return [arg]
            return arg
        flag = convert_args_to_list
        return {
                    'x' : transform_data(pandas_df[x_var], flag),
                    'y' : transform_data(pandas_df[y_var], flag),
                    'name' : legend_var,
                    'type' : plot_type,
                    'marker' : {'color' : marker_color}
               }

    def get_country_data(self, country):
        df = self.get_country_summary(country)
        return [ self.plotly_graph_data(df, x_var='date', y_var=type_, 
                                        plot_type='line', legend_var = type_,
                                        marker_color=self.colors[type_])
                for type_ in self.types ] # each line is a different chart in a sense of plotly
        
    def get_country_rate_data(self, country): 
        # as a difference between next days confirms (in people)
        df = self.get_country_summary(country)
        df['prev'] = df.shift(periods=1, fill_value=df['confirmed'][0])['confirmed']
        df['rate'] = df['confirmed'] - df['prev']
        return [ self.plotly_graph_data(df, x_var='date', y_var='rate', 
                                        plot_type='line', legend_var='rate',
                                        marker_color=self.colors['confirmed'])
                ] # even if its one line, you have to return a list

    def overall_stats(self, country):
        df = (self.data.loc[self.data['Country'] == country]
             .loc[:, ['type', self.data.columns[-1]]] # last column 
             .groupby(['type'], as_index=False)
             .sum()
            )
        df.columns = ['type', 'summary']
        df.sort_values('summary', inplace=True)
        plot = []
        for i, row in df.iterrows():
            plot.append(
                self.plotly_graph_data(row, x_var='type', y_var='summary',
                                       plot_type='bar', legend_var=row['type'],
                                       marker_color=self.colors[row['type']],
                                       convert_args_to_list=True)
            )
        return plot

    def comparison_bars(self, type_, range_val):
        df = (self.data.loc[self.data['type'] == type_]
             .groupby(['Country'], as_index=False)
             .sum()
        )
        df = df.loc[: , ['Country', df.columns[-1]]]
        df.columns.values[-1] = 'summary'
        df.sort_values('summary', inplace=True)
        df = df.loc[(df['summary'] <= range_val[1]) & (df['summary'] >= range_val[0]), :]
        plot = []
        countries_colors = sns.color_palette(n_colors=len(self.countries)).as_hex()
        for i, row in df.iterrows():
            plot.append(
                self.plotly_graph_data(row, x_var='Country', y_var='summary',
                                       plot_type='bar', legend_var=row['Country'],
                                       marker_color=countries_colors[i],
                                       convert_args_to_list=True)
            )
        return plot

    def prepare_map_data(self):
        
        def make_label(row):
            label = []
            label.append(row['Country'])
            if not pd.isna(row['State']):
                label.append(row['State'])
            label.append(row['type'] + ': ' + str(row['size']))
            return ', '.join(label)

        def scale_size(df):
            max_size = df.loc[:, 'size'].max()
            df['size'] = df.apply(lambda x : math.pow(x['size'], 1/3.5), axis = 1)
            return df
        
        df = self.data.loc[(self.data['type'] == 'confirmed') & (self.data['Country'] != 'World')]

        df.insert(loc=0, column='size', value=df.iloc[:, -1])
        df.insert(loc=0, column='text', value=df.apply(make_label, axis=1))
        df = df.loc[:, : 'type']

        df = scale_size(df)
        df = df.loc[df['size'] > 0]
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
            autosize=True,
            hovermode='closest',
            margin=dict(t=0, b=0, l=0, r=0),
            geo_scope='world',
            geo_showcoastlines = True,
            geo_coastlinecolor = '#252525',
            geo_landcolor = "#c7e9c0",
            geo_showcountries = True,
            geo_showocean=True,
            geo_oceancolor='#deebf7',
            geo_countrywidth=0.2,
            geo_countrycolor='#737373'
        )
        return fig