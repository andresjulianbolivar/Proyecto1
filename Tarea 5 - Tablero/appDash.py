# %% [markdown]
# ### Librerías y datos

# %%
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# %%
data_df = pd.read_csv('Modelamiento\datosPreparados.csv')
coef_df = pd.read_csv("Modelamiento\modeloFinal.csv")

# %% [markdown]
# ### Dash

# %%
# Inicializar app
app = dash.Dash(__name__)
app.title = "Alquileres de Vivienda"

# %%
# Layout
app.layout = html.Div([
    html.H1("Dashboard de Alquileres"),
    
    # Filtros
    html.Div([
        dcc.Dropdown(
            id='cityname-filter',
            options=[{'label': city, 'value': city} for city in data_df.columns if city.startswith('cityname_')],
            placeholder="Seleccione una ciudad"
        ),
        dcc.Dropdown(
            id='state-filter',
            options=[],  # Se debe cargar dinámicamente
            placeholder="Seleccione un estado"
        ),
        dcc.RangeSlider(
            id='price-filter',
            min=data_df['price'].min(),
            max=data_df['price'].max(),
            marks={i: f'${i}' for i in range(int(data_df['price'].min()), int(data_df['price'].max()), 500)},
            step=10,
            value=[data_df['price'].min(), data_df['price'].max()]
        ),
        dcc.Input(id='bathrooms-filter', type='number', placeholder="Número de baños"),
        dcc.Checklist(
            id='amenities-filter',
            options=[{'label': amenity, 'value': amenity} for amenity in ['Pool', 'Parking', 'Elevator']],
            inline=True
        )
    ]),
    
    # KPIs
    html.Div([
        html.H3("KPIs"),
        html.P(id='average-price'),
        html.P(id='amenities-impact'),
        html.P(id='top-cities')
    ]),
    
    # Visualizaciones
    dcc.Graph(id='price-heatmap'),
    dcc.Graph(id='coefficient-bar-chart'),
    dcc.Graph(id='boxplot-photos'),
    
    # Simulador de precios
    html.Div([
        html.H3("Simulador de Precios"),
        dcc.Input(id='sim-bathrooms', type='number', placeholder="Número de baños"),
        dcc.Input(id='sim-size', type='number', placeholder="Tamaño en pies cuadrados"),
        dcc.Dropdown(
            id='sim-city',
            options=[{'label': city, 'value': city} for city in data_df.columns if city.startswith('cityname_')],
            placeholder="Seleccione una ciudad"
        ),
        dcc.Checklist(
            id='sim-amenities',
            options=[{'label': amenity, 'value': amenity} for amenity in ['Pool', 'Parking', 'Elevator']],
            inline=True
        ),
        html.Button("Calcular Precio", id='calculate-price'),
        html.P(id='estimated-price')
    ])
])

# %%
# Callbacks
@app.callback(
    Output('average-price', 'children'),
    Input('cityname-filter', 'value')
)
def update_average_price(city):
    if city:
        filtered_df = data_df[data_df[city] == 1]
        avg_price = filtered_df['price'].mean()
        return f"Precio promedio en {city}: ${avg_price:.2f}"
    return "Seleccione una ciudad"

@app.callback(
    Output('price-heatmap', 'figure'),
    Input('cityname-filter', 'value')
)
def update_heatmap(city):
    fig = px.scatter_mapbox(data_df, lat="latitude", lon="longitude", color="price", zoom=3,
                            mapbox_style="carto-positron")
    return fig


# %%
if __name__ == '__main__':
    app.run_server(debug=True)


