import plotly.graph_objects as pgo

import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = [15.0, 4.0]
plt.rcParams["figure.dpi"] = 140

import os

if os.environ.get("PLOTMETHOD", None) == "matplotlib":
    OUTPUT_MODE = "matplotlib"
else:
    OUTPUT_MODE = "plotly"


class Plot:
    def __init__(self, fig):
        self.fig = fig

    def show(self):
        if OUTPUT_MODE == "matplotlib":
            plt.show()
        elif OUTPUT_MODE == "plotly":
            self.fig.show()

    def title(self, title):
        if OUTPUT_MODE == "matplotlib":
            plt.title(title)
        elif OUTPUT_MODE == "plotly":
            self.fig.update_layout(title=title)

    def xrange(self, left, right):
        if OUTPUT_MODE == "matplotlib":
            plt.xlim(left, right)
        elif OUTPUT_MODE == "plotly":
            self.fig.update_layout(xaxis_range=(left, right))

    def yrange(self, left, right):
        if OUTPUT_MODE == "matplotlib":
            plt.ylim(left, right)
        elif OUTPUT_MODE == "plotly":
            self.fig.update_layout(yaxis_range=(left, right))

    def xlabel(self, label):
        if OUTPUT_MODE == "matplotlib":
            plt.xlabel(label)
        elif OUTPUT_MODE == "plotly":
            self.fig.update_layout(xaxis_title=label)

    def ylabel(self, label):
        if OUTPUT_MODE == "matplotlib":
            plt.ylabel(label)
        elif OUTPUT_MODE == "plotly":
            self.fig.update_layout(yaxis_title=label)


def plot_lines(datas):
    """Plot lines.

    Assumes datas is a list of tuples (name, data).
    If data itself is a list of values assume these are y-coordinates.
    If data itself is a list of tuples assume these are (x, y)-coordinates
    """
    if not isinstance(datas[0], tuple):
        datas = [(f"data {i}", data) for i, data in enumerate(datas)]

    if OUTPUT_MODE == "matplotlib":
        fig = plt
        for name, data in datas:
            if isinstance(data[0], tuple):
                xs, ys = zip(*data)
                plt.plot(xs, ys, label=name)
            else:
                plt.plot(data, label=name)
        # NOTE: Number of entries in legend is limited to avoid too big plots
        plt.legend([name for name, _ in datas][:16])
    else:
        fig = pgo.Figure()
        for name, data in datas:
            if isinstance(data[0], tuple):
                xs, ys = zip(*data)
                fig.add_trace(pgo.Scatter(x=xs, y=ys, name=name))
            else:
                fig.add_trace(pgo.Scatter(y=data, name=name))
        fig["data"][0]["showlegend"] = True

    return Plot(fig)
