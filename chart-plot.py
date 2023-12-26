#!/usr/bin/env python

# from https://stackoverflow.com/a/63677698/431222

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, Dash, dcc, html
from dash.dependencies import Input, Output

def main():
    global app, cols, df

    # code and plot setup

    # settings
    pd.options.plotting.backend = "plotly"
    countdown = 20

    # sample dataframe of a wide format
    np.random.seed(4); cols = list('abc')
    X = np.random.randn(50,len(cols))  
    df=pd.DataFrame(X, columns=cols)
    df.iloc[0]=0;

    # plotly figure
    fig = df.plot(template = 'plotly_dark')

    app = Dash(__name__)
    app.layout = html.Div([
        html.H1("Streaming of random data"),
                dcc.Interval(
                id='interval-component',
                interval=200, # in milliseconds
                n_intervals=0
            ),
        dcc.Graph(id='graph'),
    ])

    app.run(port = 8069, dev_tools_ui=True, #debug=True,
            dev_tools_hot_reload =True, threaded=True)


# Define callback to update graph
@callback(
    Output('graph', 'figure'),
    [Input('interval-component', "n_intervals")]
)
def streamFig(value):
    
    global app, cols, df
    
    Y = np.random.randn(1,len(cols))  
    df2 = pd.DataFrame(Y, columns = cols)
    df = pd.concat([df, df2], ignore_index=True) 
    df.tail()
    df3=df.copy()
    df3 = df3.cumsum()
    fig = df3.plot(template = 'plotly_dark')
    return(fig)

if __name__ == "__main__":
    main()