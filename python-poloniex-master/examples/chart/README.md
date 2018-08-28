chart.py - saves chart data in a mongodb collection and returns a pandas dataframe with basic indicators

Requires:
```
pandas
numpy
pymongo
```

bokehPlotter.py - same as chart.py with an added `graph` method that plots the data (with indicators) using bokeh

Requires:
```
pandas
numpy
pymongo
bokeh
```

Bot para consola:
cd U:\python-poloniex-master\Projecto git\test01\python-poloniex-master
u:

set PYTHONPATH=.

python examples\chart\chart.py
python examples\chart\chartDummy.py