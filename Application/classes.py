class scatterPlotData(object):
    def __init__(self, df, name, color):
        # df is a pandas dataframe that contains columns named: x_rel, y_rel, z_rel
        # The idea of creating this class is to enable function plotTerrain to receive more than one dataset and plot it the same graph
        self.df = df
        self.name = name # name given to the plot series
        self.color = color # color strin given to the plot in the format: 'rgba(217, 217, 217, 0.14)'
