import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

def plotHist(t, x, y, filename):
    ax =  t.hist()
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    fig = ax.get_figure()
    fig.savefig(filename)


