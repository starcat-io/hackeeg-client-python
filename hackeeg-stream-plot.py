#!/usr/bin/env python

import math

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, Dash, dcc, html
from dash.dependencies import Input, Output

GRAPH_SIZE_IN_ROWS = 100

def main():
    global app, cols, df, counter
    counter = 0

    # code and plot setup

    # settings
    pd.options.plotting.backend = "plotly"
    countdown = 20

    # sample dataframe of a wide format
    np.random.seed(4) 
    cols = list('a')
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
    
    global app, cols, df, counter
    counter += 1
    
    df0 = pd.DataFrame(np.array([counter/10.0], dtype=float))
    df2 = np.sin(df0)

    df = pd.concat([df, df2], ignore_index=True) 
    df3=df.copy()
    df3 = df3.cumsum()
    df3_number_of_rows = len(df3)
    if df3_number_of_rows < GRAPH_SIZE_IN_ROWS:
         number_of_rows_to_display = df3_number_of_rows
    else:
         number_of_rows_to_display = GRAPH_SIZE_IN_ROWS
    df4 = df3.iloc[-number_of_rows_to_display:]
    fig = df4.plot(template = 'plotly_dark')

    colors = px.colors.qualitative.Plotly
    for i, col in enumerate(df4.columns):
            fig.add_annotation(x=df4.index[-1], y=df4[col].iloc[-1],
                                   text = str(df4[col].iloc[-1])[:4],
                                   align="right",
                                   arrowcolor = 'rgba(0,0,0,0)',
                                   ax=25,
                                   ay=0,
                                   yanchor = 'middle',
                                   font = dict(color = colors[i]))
    return(fig)

if __name__ == "__main__":
    main()