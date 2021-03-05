import pandas as pd
import plotly.graph_objects as go
import plotly
from application_logging import logger


class data_visualization:

    def __init__(self):
        self.file_object = open("application_logs/applicationLog.txt", 'a+')
        self.log_writer = logger.Application_logger()


    def plot_3d_graph(self, test_data):
        df = pd.read_csv(test_data)
        self.log_writer.log(self.file_object, "Getting dataset from file to plot a graph")
        fig = go.Figure(
            data=[go.Mesh3d(x=df['ProductName'], y=df['OfferPrice'], z=df['Discount'])],
            layout_title_text="Visualise flipkart data through graph"
        )
        plotly.offline.plot(fig, filename='graph.html', auto_open=True)
        self.log_writer.log(self.file_object, 'Plotted 3D Graph')
