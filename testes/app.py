import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def agg_data (df):
    df2 = df.copy()
    df2 = df2.groupby(['sex', 'smoker'])['total_bill'].sum().reset_index()
    df3 = df2.pivot_table(index='sex', columns = 'smoker', values = 'total_bill')
    df3.columns = [str(df3.columns.name) + '_' + str(df3.columns[ind]) for ind in range(len(df3.columns))]
    df4 = df3.reset_index().round(2)
    print(df4)
    return df4

def draw_barplot_stacked_horizontal (df, 
    nome_cols_plot = ['Abaixo', 'Dentro', 'Acima'], 
    nomes_legenda = ['Abaixo', 'Dentro', 'Acima'],
    colors = ['rgba(190, 192, 213, 1)', 'rgba(122, 120, 168, 0.8)', 'rgba(38, 24, 74, 0.8)'],
    titulo_legenda = 'Scores',
    nome_eixo_x = 'Tipos',
    ylim = [0,1]):

    fig = go.Figure()
    
    for i in range(len(nome_cols_plot)):
        print(i)
        fig.add_trace(
            go.Bar(y=df[nome_eixo_x], 
            name = nomes_legenda[i], 
            x=df[nome_cols_plot[i]], 
            text = ['{:,.0f}%'.format(i2*100) for i2 in df[nome_cols_plot[i]].values.tolist()], 
            textposition='inside',  
            textfont_size=16,
            orientation='h',
            marker=dict(
                color=colors[i],
                line=dict(color='rgb(248, 248, 249)', width=2)
            ))
        )
    
    fig.update_layout(barmode='stack',
        title_text="Grafico 2",
        plot_bgcolor='white',
        legend_title=titulo_legenda,
        xaxis=dict(
            #title='Ggrafico1',
            #titlefont_size=25
            tickfont_size=18,
        ),
        transition_duration=100
    )
    #fig['layout']['yaxis1'].update(showticklabels=False,range = ylim,autorange=False)
    fig['layout']['xaxis'].update(showticklabels=False,range = ylim,autorange=False)

    return fig

def draw_barplot (df, 
    nome_cols_plot = ['smoker_No', 'smoker_Yes'], 
    nomes_legenda = ['No', 'Yes'],
    colors = ['rgba(190, 192, 213, 1)',  'rgba(38, 24, 74, 0.8)'],
    titulo_legenda = 'Smoker',
    nome_eixo_x = 'sex',
    ylim = [0,2500]):

    fig = go.Figure()
    for i in range(len(nome_cols_plot)):
        #print(i)
        fig.add_trace(
            go.Bar(x=df[nome_eixo_x], 
            name = nomes_legenda[i], 
            y=df[nome_cols_plot[i]], 
            text = df[nome_cols_plot[i]].values.tolist(), 
            textposition='outside',  
            textfont_size=16,
            marker=dict(
                color=colors[i],
                line=dict(color='rgb(248, 248, 249)', width=1.5)
            ))
        )
    
    
    fig.update_layout(barmode='group',
        title_text="Grafico 1",
        plot_bgcolor='white',
        legend_title=titulo_legenda,
        xaxis=dict(
            #title='Ggrafico1',
            #titlefont_size=25
            tickfont_size=18,
        ),
        transition_duration=100
    )
    fig['layout']['yaxis1'].update(showticklabels=False,range = ylim,autorange=False)
    
    return fig

###############################################################################
df = px.data.tips()

df_teste = pd.DataFrame({'Tipos' : ['Verm', 'Ama', 'Verde'],
                   'Abaixo' : [0.5, 0.2, 0.2],
                    'Dentro' : [0.3,0.3,0.2],
                    'Acima' :[0.2, 0.5, 0.6]
                   })
fig_horizontal = draw_barplot_stacked_horizontal(df_teste)
################################################################################

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    # html.Div([
    #     html.Section('Seção 1'),
    #     html.H4(children='Explica gráfico 1'),
    # ]),
    # html.Div(children='''
    #     *Dash: A web application framework for Python.*
    # '''),
    html.H4(children='Explica gráfico 1'),

    html.Label('Selecione o dia:  '),
    dcc.Dropdown(
        id = 'change_day',
        options=[
            {'label' : str(i), 'value': str(i)} for i in df['day'].unique()
        ],
        multi=True
        #value='MTL'
    ),

    html.Label('Selecione a refeição:  '),
    dcc.Checklist(
        id = 'change_time',
        options=[
            {'label': 'Lunch', 'value': 'Lunch'},
            {'label': 'Dinner', 'value': 'Dinner'}
        ],
        value=['Lunch', 'Dinner'],
        labelStyle={'display': 'inline-block'}
    ),
    
    html.Label('Selecione o tamanho:  '),
    dcc.RangeSlider(
    id='my-range-slider',
    min=df['size'].min(),
    max=df['size'].max(),
    step=1,
    value=[1, 6],
    marks = {i : str(i) for i in df['size'].unique().tolist()}
    ),
    
    html.Br(),

    dcc.Graph(
        id='example-graph',
        #figure=fig
    ),

    html.Br(),
    html.H4(children='Explica gráfico 2'),

    dcc.Graph(
        figure=fig_horizontal
    )
])

@app.callback(
    Output('example-graph', 'figure'),
    [Input('change_time', 'value'),
    Input('my-range-slider', 'value'),
    Input('change_day', 'value')])

def update_figure(lista_change_time, lista_change_size, lista_change_day):    
    print(lista_change_day)
    df2 = df[(df['time'].isin(lista_change_time)) & (df['size'] >= lista_change_size[0]) & (df['size'] <= lista_change_size[1])]
    if ((lista_change_day != None) & (lista_change_day != [])):
        df2 = df2[(df2['day'].isin(lista_change_day))]
    
    #else:
    #fig.update_layout(barmode='group', transition_duration=100)
    df3 = agg_data(df2)
    fig = draw_barplot(df3)

    #string2 = "You have selected {}".format(lista_change_size)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
