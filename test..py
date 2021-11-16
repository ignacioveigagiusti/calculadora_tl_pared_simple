import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from Calculadora_TL import Calculadora_TL

calculadora_tl = Calculadora_TL('TABLA MATERIALES TP1.xlsx')
data = calculadora_tl.data

available_indicators = data.material

material = available_indicators[13]

calculadora_tl = Calculadora_TL(data_path='TABLA MATERIALES TP1.xlsx',
                                    t=5,
                                    l1=3, l2=0.015)
resultados = calculadora_tl.calcular_r(material, ley1)
fcrit = calculadora_tl.fc(material)
fdens = calculadora_tl.fd(material)