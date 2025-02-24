import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Cargar datos
datos = pd.read_csv("Tarea 5 - Tablero/datosPreparados.csv")
coeficientes = pd.read_csv("Tarea 5 - Tablero/modeloFinal.csv")

# Obtener la lista de ciudades, estados, fuentes, mascotas y amenities
ciudades = [col for col in datos.columns if col.startswith("cityname_")]
estados = [col for col in datos.columns if col.startswith("state_")]
fuentes = [col for col in datos.columns if col.startswith("source_")]
mascotas = [col for col in datos.columns if col.startswith("pets_allowed_")]
fotos = [col for col in datos.columns if col.startswith("has_photo_")]
amenities = ["TV", "Dishwasher", "Wood Floors", "Elevator", "Clubhouse", "Doorman", "Parking", "Patio/Deck", "Luxury", "Storage", "View", "Refrigerator", "Playground", "Internet Access", "Tennis", "Gated", "Basketball", "Golf", "Garbage Disposal", "AC", "Gym", "Washer Dryer", "Pool", "Alarm", "Hot Tub", "Fireplace", "Cable or Satellite"]

# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Plataforma de Alquileres de Vivienda"

# Layout del tablero
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("Plataforma de Alquileres de Vivienda"), width=12)
    ]),
    
    # Mapa
    dbc.Row([
        dbc.Col(html.Iframe(
            srcDoc=open("Tarea 5 - Tablero/mapa_precios.html", "r", encoding="utf-8").read(),
            width="100%", height="500px", style={"border": "none"}
        ), width=12)
    ]),

    # Filtros Globales
    dbc.Row([
        dbc.Col(dcc.Dropdown(id="state-dropdown", placeholder="Seleccione un estado", options=[{"label": estado.replace("state_", ""), "value": estado} for estado in estados]), width=3),
        dbc.Col(dcc.Input(id="bathrooms-input", type="number", placeholder="Número de baños", min=1, max=10), width=2),
        dbc.Col(dcc.Checklist(id="amenities-checklist", options=[{"label": amenity, "value": amenity} for amenity in amenities], inline=True), width=5)
    ]),
    
    # Slider tamaño
    dbc.Row([
        dbc.Col(dcc.RangeSlider(
            id="square-feet-range",
            min=datos["square_feet"].min(),
            max=datos["square_feet"].max(),
            step=100,
            value=[datos["square_feet"].min(), datos["square_feet"].max()],
            marks={i: str(i) for i in range(datos["square_feet"].min(), datos["square_feet"].max() + 1, 500)},
            tooltip={"placement": "bottom", "always_visible": True}
        ))
    ]),

    # KPIs
    dbc.Row([
        dbc.Col(html.Div(id="total-cities-kpi"), width=3),
        dbc.Col(html.Div(id="total-apartments-kpi"), width=3),
        dbc.Col(html.Div(id="avg-price-kpi"), width=3),
        dbc.Col(html.Div(id="avg-description-length-kpi"), width=3)
    ]),

    # Gráficos Descriptivos
    dbc.Row([
        dbc.Col(dcc.Graph(id="heatmap"), width=6),
        dbc.Col(dcc.Graph(id="boxplot"), width=6),
        dbc.Col(dcc.RadioItems(
            id="boxplot-category",
            options=[
                {"label": "Tiene fotos", "value": "photos"},
                {"label": "Permite mascotas", "value": "pets"}
            ],
            value="photos",
            inline=True
        ), width=4)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="amenities-bar"))
    ]),

    # Simulador de Precios
    dbc.Row([
        dbc.Col([
            html.H4("Simulador de Precios"),
            dbc.Input(id="sim-bathrooms", type="number", placeholder="Baños", min=1, max=10),
            dbc.Input(id="sim-square-feet", type="number", placeholder="Tamaño (sq ft)"),
            dcc.Dropdown(id="sim-city", placeholder="Ciudad", options=[{"label": city.replace("cityname_", ""), "value": city} for city in ciudades]),
            dbc.Checklist(id="sim-amenities", options=[{"label": amenity, "value": amenity} for amenity in amenities]),
            html.H5(id="sim-output")
        ], width=6)
    ])
])

# Callbacks
@app.callback(
    [Output("total-cities-kpi", "children"),
     Output("total-apartments-kpi", "children"),
     Output("avg-price-kpi", "children"),
     Output("avg-description-length-kpi", "children")],
    [Input("state-dropdown", "value"),
     Input("bathrooms-input", "value"),
     Input("square-feet-range", "value"),
     Input("amenities-checklist", "value")]
)
def update_kpis(state, bathrooms, square_feet_range, amenities):
    filtered_data = datos.copy()
    if state:
        filtered_data = filtered_data[filtered_data[state] == 1]
    if bathrooms:
        filtered_data = filtered_data[filtered_data["bathrooms"] == bathrooms]
    if square_feet_range:
        filtered_data = filtered_data[(filtered_data["square_feet"] >= square_feet_range[0]) & (filtered_data["square_feet"] <= square_feet_range[1])]
    if amenities:
        for amenity in amenities:
            filtered_data = filtered_data[filtered_data[amenity] == 1]

    total_cities = filtered_data[[col for col in ciudades]].sum().sum()
    total_apartments = len(filtered_data)
    avg_price = filtered_data["price"].mean()
    avg_description_length = filtered_data["longitud_descripcion"].mean()

    return (f"Ciudades: {total_cities}", f"Apartamentos: {total_apartments}", f"Precio Promedio: ${avg_price:.2f}", f"Longitud Descripción: {avg_description_length:.2f}")

@app.callback(
    Output("heatmap", "figure"),
    [Input("state-dropdown", "value"),
     Input("bathrooms-input", "value"),
     Input("square-feet-range", "value"),
     Input("amenities-checklist", "value")]
)
def update_heatmap(state, bathrooms, square_feet_range, amenities):
    filtered_data = datos.copy()
    if state:
        filtered_data = filtered_data[filtered_data[state] == 1]
    if bathrooms:
        filtered_data = filtered_data[filtered_data["bathrooms"] == bathrooms]
    if square_feet_range:
        filtered_data = filtered_data[(filtered_data["square_feet"] >= square_feet_range[0]) & (filtered_data["square_feet"] <= square_feet_range[1])]
    if amenities:
        for amenity in amenities:
            filtered_data = filtered_data[filtered_data[amenity] == 1]

    fig = px.density_map(filtered_data, lat="latitude", lon="longitude", z="price", radius=10, center=dict(lat=37.76, lon=-122.4), zoom=10)
    return fig

@app.callback(
    Output("boxplot", "figure"),
    [Input("state-dropdown", "value"),
     Input("bathrooms-input", "value"),
     Input("square-feet-range", "value"),
     Input("amenities-checklist", "value"),
     Input("boxplot-category", "value")]  # Nuevo input para elegir categoría
)
def update_boxplot(state, bathrooms, square_feet_range, amenities, category):
    filtered_data = datos.copy()

    if state:
        filtered_data = filtered_data[filtered_data[state] == 1]
    if bathrooms:
        filtered_data = filtered_data[filtered_data["bathrooms"] == bathrooms]
    if square_feet_range:
        filtered_data = filtered_data[(filtered_data["square_feet"] >= square_feet_range[0]) & (filtered_data["square_feet"] <= square_feet_range[1])]
    if amenities:
        for amenity in amenities:
            filtered_data = filtered_data[filtered_data[amenity] == 1]

    # Definir la categoría seleccionada
    if category == "photos":
        # Identificar qué columna de fotos tiene un valor de 1 y asignarla a una nueva columna
        photo_columns = ["has_photo_No", "has_photo_Thumbnail", "has_photo_Yes"]
        filtered_data["photo_category"] = filtered_data[photo_columns].idxmax(axis=1)
        x_axis = "photo_category"
        title = "Boxplot de Precios por Presencia de Fotos"
    
    elif category == "pets":
        # Identificar qué columna de mascotas tiene un valor de 1 y asignarla a una nueva columna
        pet_columns = ["pets_allowed_Cats", "pets_allowed_Cats,Dogs", "pets_allowed_Dogs", "pets_allowed_No permitido"]
        filtered_data["pet_category"] = filtered_data[pet_columns].idxmax(axis=1)
        x_axis = "pet_category"
        title = "Boxplot de Precios por Permiso de Mascotas"
    
    else:
        return px.box(title="Categoría no disponible en los datos")

    # Crear el boxplot con la categoría seleccionada
    fig = px.box(filtered_data, x=x_axis, y="price", points="all", title=title)

    return fig


@app.callback(
    Output("amenities-bar", "figure"),
    [Input("state-dropdown", "value"),
     Input("bathrooms-input", "value"),
     Input("square-feet-range", "value"),
     Input("amenities-checklist", "value")]
)
def update_amenities_bar(state, bathrooms, square_feet_range, amenities):
    filtered_data = datos.copy()
    if state:
        filtered_data = filtered_data[filtered_data[state] == 1]
    if bathrooms:
        filtered_data = filtered_data[filtered_data["bathrooms"] == bathrooms]
    if square_feet_range:
        filtered_data = filtered_data[(filtered_data["square_feet"] >= square_feet_range[0]) & (filtered_data["square_feet"] <= square_feet_range[1])]
    if amenities:
        for amenity in amenities:
            filtered_data = filtered_data[filtered_data[amenity] == 1]

    fig = px.bar(filtered_data, x=amenities, y="price", title="Precio Promedio por Amenities")
    return fig


@app.callback(
    Output("sim-output", "children"),
    [Input("sim-bathrooms", "value"),
     Input("sim-square-feet", "value"),
     Input("sim-city", "value"),
     Input("sim-amenities", "value")]
)
def update_simulator(bathrooms, square_feet, city, amenities):
    if not all([bathrooms, square_feet, city]):
        return "Ingrese todos los valores para obtener una estimación."
    df_ciudades = coeficientes[coeficientes["Variables"].str.startswith("cityname_")]
    price = (bathrooms * 297) + (square_feet * 0.63)
    
    for index, row in df_ciudades.iterrows():
        if city == row["Variables"]:
            price += row["Coeficientes"]
    if amenities:
        if "Elevator" in amenities:
            price += 251.1930144710353
        if "Parking" in amenities:
            price += 160.13931935370934
        if "Clubhouse" in amenities:
            price += 50.78495715235734
        if "Playground" in amenities:
            price -= 87.51470430284112
        if "Internet Access" in amenities:
            price += 86.6327185048433
        if "Garbage Disposal" in amenities:
            price -= 91.06921202021972
        if "Pool" in amenities:
            price += 87.19850857859029

    return f"Precio Estimado: ${price:.2f}"

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)