import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from Calculadora_TL import Calculadora_TL

app = dash.Dash(__name__)
app.title = 'Calculadora TL'
server = app.server
calculadora_tl = Calculadora_TL('TABLA MATERIALES TP1.xlsx')
data = calculadora_tl.data
available_indicators = data.material
available_indicators2 = data.rho
available_indicators3 = data.E
available_indicators4 = data.nint
available_indicators5 = data.sigma

app.layout = html.Div([

    html.Div([html.H1("TL - Pared Simple", style={
                'font-family': 'verdana', 'width':'50%','color':'white'})],
                style={'vertical-align': 'top'}),

        html.Div([
            html.P(children='Desarrollado por Nicolás Cavasso, Ignacio Veiga y Pedro Venezia',style={'color':'white'})
        ]),

        html.Div([
            html.P(id = 'text-material',children = 'Material',style={'color':'white'}),
            dcc.Dropdown(
                id='material',
                options=[{'label': i+"    "+'(Densidad: '+str(j)+'  E: '+str(k)+'  Pérdidas: '+str(l)+'  Poisson: '+str(m)+')', 'value': i} for i,j,k,l,m in zip(available_indicators,available_indicators2,available_indicators3,available_indicators4,available_indicators5)],
                value='Acero'
            ),
            html.Div([
                html.P(id = 'text-dimensiones',children = 'Dimensiones (m)',style={'color':'white'}),
                dcc.Input(
                    id='largo',
                    placeholder='Largo',
                    type='number',
                    value='Largo',
                    min='0.001'
                    ),
                dcc.Input(
                    id='alto',
                    placeholder='Alto',
                    type='number',
                    value='Alto',
                    min='0.001'),
                dcc.Input(
                    id='espesor',
                    placeholder='Espesor',
                    type='number',
                    value='Ancho',
                    min='0.001')
            ]),
            #html.P(id = 'frec_c',children = 'Frecuencia Crítica - Negro, Frecuencia de Densidad - Rosa'+str(),style={'color':'black'}),       
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
             html.Button('Exportar', id='boton_exportar'), dcc.Download(id="exportar"),
             dcc.Checklist(    
                 id='metodos',          
                options=[
                    {'label': 'Pared Simple', 'value': 'ley1'},
                    {'label': 'Modelo Sharp', 'value': 'sharp'},
                    {'label': 'ISO 12354-1', 'value': 'ISO'},
                    {'label': 'Modelo Davy', 'value': 'davy'}
                ],
                labelStyle={'display': 'block','color':'white'},
                style={'marginBottom': 150, 'marginTop': 25}),
        ],style={'width': '30%', 'float': 'right', 'display': 'inline-block'}),

        dcc.Graph(id='indicator-graphic'),

        html.Div([
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Log',
                labelStyle={'display': 'inline-block'})
        ],style={'display': 'none'})
],style={'backgroundColor': 'rgb(149,161,206)'})

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('material', 'value'),
    Input('alto', 'value'),
    Input('largo', 'value'),
    Input('espesor', 'value'),
    Input('metodos', 'value'),
    Input('xaxis-type', 'value'))
def update_graph(material,alto,largo,espesor,metodos, xaxis_type):

    calculadora_tl = Calculadora_TL(data_path='TABLA MATERIALES TP1.xlsx',
                                    t=espesor,
                                    l1=largo, l2=alto)
    resultados = calculadora_tl.calcular_r(material, metodos)
    fcrit = calculadora_tl.fc(material)
    fdens = calculadora_tl.fd(material)
    resultados['frecuencia'] = calculadora_tl.f
    colors = px.colors.qualitative.Plotly
    fig = go.Figure()
    # Edit the layout
    fig.update_layout(title='Aislamiento a ruido aéreo según distintos métodos',
                   xaxis_title='Frecuencia (Hz)',
                   yaxis_title='R (dB)')
    fig.update_xaxes(type='linear' if xaxis_type == 'Linear' else 'log')
    names = {'ley1':'pared simple', 'sharp':'modelo Sharp', 'ISO':'ISO 12354-1', 'davy': 'modelo Davy'}
    for i, x in enumerate(metodos):
        fig.add_traces(go.Scatter(x=resultados['frecuencia'], y = resultados[x],
                                  mode = 'lines+markers', line=dict(color=colors[i]),
                                  name=names[x]))
    #fig.add_vline(x=fcrit, line_width=1, line_dash='dash', line_color='black')
    #fig.add_vline(x=fdens, line_width=1, line_dash='dash', line_color='pink')
    fig.add_trace(go.Scatter(x=[fcrit,fcrit], y=[0,120],
                                mode='lines',line=dict(color='black', width=1, dash='dash'),
                                name='frecuencia critica'))
    fig.add_trace(go.Scatter(x=[fdens,fdens], y=[0,120],
                                mode='lines',line=dict(color='blue', width=1, dash='dash'),
                                name='frecuencia densidad'))                                  
    fig.show()
    return fig

@app.callback(
    Output("exportar", "data"),
    Input('boton_exportar', 'n_clicks'),
    Input('material', 'value'),
    Input('alto', 'value'),
    Input('largo', 'value'),
    Input('espesor', 'value'),
    Input('metodos', 'value'),
    prevent_initial_call=True,)
def download_func(boton_exportar, material, alto, largo, espesor, metodos):
    calculadora_tl = Calculadora_TL(data_path='TABLA MATERIALES TP1.xlsx',
                                    t=espesor,
                                    l1=largo, l2=alto)
    resultados = calculadora_tl.calcular_r(material, metodos)
    resultados['frecuencia'] = calculadora_tl.f
    resultados_df = pd.DataFrame(resultados)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'boton_exportar' in changed_id:
        return dcc.send_data_frame(resultados_df.to_excel, "resultados.xlsx", sheet_name="resultados")

if __name__ == '__main__':
    app.run_server(debug=True)