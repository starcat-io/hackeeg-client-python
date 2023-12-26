#!/usr/bin/env python

from multiprocessing import Process, Queue
    
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, Dash, dcc, html
from dash.dependencies import Input, Output

GRAPH_SIZE_IN_ROWS = 100

class Plotter:
    def __init__(self, app=None, queue=None):
        self.app = app
        if self.app is None:
            self.app = Dash(__name__)
        self.callbacks(self.app)

        self.queue = queue
        if self.queue is None:
            raise Exception("No queue given.")

        self.cols = None
        self.df = None
    
    def callbacks(self, app):
        @app.callback(
            Output('graph', 'figure'),
            [Input('interval-component', "n_intervals")]
        )
        def streamFig(value):
            df0 = pd.DataFrame(np.array([self.get_datapoint()], dtype=float))
            df2 = np.sin(df0)

            self.df = pd.concat([self.df, df2], ignore_index=True) 
            df3 = self.df.copy()
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


    def main(self):
        pd.options.plotting.backend = "plotly"

        np.random.seed(4) 
        self.cols = list('a')

        X = pd.DataFrame(np.array([self.get_datapoint()], dtype=float))
        self.df=pd.DataFrame(X, columns=self.cols)
        self.df.iloc[0]=0;

        fig = self.df.plot(template = 'plotly_dark')

        self.app.layout = html.Div([
            html.H1("Streaming of random data"),
                    dcc.Interval(
                    id='interval-component',
                    interval=100, # milliseconds
                    n_intervals=0
                ),
            dcc.Graph(id='graph'),
        ])

        self.app.run(port = 8069, dev_tools_ui=True, #debug=True,
                dev_tools_hot_reload =True, threaded=True)
                

    def get_datapoint(self):
        datapoint = self.queue.get()
        return datapoint


def plotter_process(app, queue):
    print(app, queue)
    if queue is None:
        raise Exception("no q")
    Plotter(app=app, queue=queue).main()

counter = 0
def create_datapoint():
    global counter
    datapoint = counter/10.0
    counter += 1
    return datapoint

def hackeeg_process():
    queue = Queue()
    app = None
    p = Process(target=plotter_process, args=(app, queue))
    p.start()
    for i in range(0, 10000):
        queue.put(create_datapoint())
    p.join()


if __name__ == "__main__":
    hackeeg_process()