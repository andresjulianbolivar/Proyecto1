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
app.title = "Alquileres de Vivienda"

# Layout del tablero
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("Alquileres de Vivienda"), width=12)
    ], style={"margin-top": "50px", "text-align": "center", "background-color": "#f0f0f0"}),
    
    # Mapa
    dbc.Row([
        dbc.Col(html.Div(
            style={
                "position": "relative",  # Permite superponer elementos
                "width": "100%",
                "height": "500px",
            },
            children=[
                # Mapa
                html.Iframe(
                    srcDoc=open("Tarea 5 - Tablero/mapa_precios.html", "r", encoding="utf-8").read(),
                    style={
                        "width": "100%",
                        "height": "100%",
                        "border": "none",
                    }
                ),
                # Leyenda con degradado
                html.Div(
                    style={
                        "position": "absolute",  
                        "top": "20px",  
                        "right": "20px", 
                        "background": "white", 
                        "padding": "15px", 
                        "border": "1px solid #ddd",
                        "border-radius": "10px", 
                        "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.2)", 
                        "z-index": "1000", 
                        "width": "180px",
                        "font-family": "Arial, sans-serif",  
                    },
                    children=[
                        # Cuadro degradado
                        html.Div(
                            style={
                                "background": "linear-gradient(to left, blue, green, yellow, red)",  # Degradado
                                "height": "20px",  # Alto del cuadro degradado
                                "border-radius": "5px",  # Bordes redondeados
                                "margin-bottom": "10px",  # Espacio debajo del cuadro
                            }
                        ),
                        # Etiquetas de precio
                        html.Div(
                            style={
                                "display": "flex",
                                "justify-content": "flex-end",  # Alinea el texto a la derecha
                            },
                            children=[
                                html.Div(
                                    "Mayor concentración de apartamentos",
                                    style={
                                        "font-size": "12px",
                                        "color": "red",
                                    }
                                ),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    "Puede acercar o alejar el mapa para ver la distribución de apartamentos en diferentes regiones.",
                    style={
                        "text-align": "left",
                        "font-size": "12px", 
                        "color": "#666",  
                        "margin-top": "2px" 
                    })
            ]
        ))
    ], style={"margin-top": "50px"}),

    # Filtros Globales
    dbc.Row(
        [
            dbc.Col(
                [
            # Dropdown para seleccionar el estado
            dbc.Row(
                
                dbc.Card(
                    dbc.CardBody([
                        dbc.Label("Seleccione un estado", className="font-weight-bold"),
                        dcc.Dropdown(
                            id="state-dropdown",
                            placeholder="Seleccione un estado",
                            options=[{"label": estado.replace("state_", ""), "value": estado} for estado in estados],
                            className="mb-3"  # Margen inferior
                        )
                    ]),
                    style={"border": "1px solid #ddd", "border-radius": "10px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
                ),
            ),
            # Input para el número de baños
            dbc.Row(
                dbc.Card(
                    dbc.CardBody([
                        dbc.Label("Número de baños", className="font-weight-bold"),
                        dbc.Input(
                            id="bathrooms-input",
                            type="number",
                            placeholder="Ej: 2",
                            min=1,
                            max=10,
                            className="mb-3"  # Margen inferior
                        )
                    ]),
                    style={"border": "1px solid #ddd", "border-radius": "10px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
                ),
            )
                ], width=4
            ),
            # Checklist para las amenities
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        dbc.Label("Seleccione los Amenities", className="font-weight-bold"),
                        dbc.Checklist(
                            id="amenities-checklist",
                            options=[{"label": amenity, "value": amenity} for amenity in amenities],
                            inline=True,
                            switch=True,
                            className="mb-10"
                        )
                    ]),
                    style={"border": "1px solid #ddd", "border-radius": "10px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
                ),
                width=6
            ),
        ],
        # Centrar horizontal y verticalmente
        justify="center",  # Centrar horizontalmente
        align="center",    # Centrar verticalmente
        className="h-100",  # Asegura que la fila ocupe toda la altura disponible
        style={"margin-top": "50px"}
    ),
    
    # Slider tamaño
    dbc.Row([
        dbc.Col([
            # RangeSlider para el tamaño del apartamento
            dcc.RangeSlider(
                id="square-feet-range",
                min=datos["square_feet"].min(),
                max=datos["square_feet"].max(),
                step=100,
                value=[datos["square_feet"].min(), datos["square_feet"].max()],
                marks={i: str(i) for i in range(datos["square_feet"].min(), datos["square_feet"].max() + 1, 500)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            # Título debajo del slider
            html.Div(
                "Seleccione el rango del tamaño del apartamento (sq ft)",
                style={
                    "text-align": "center",  # Centrar el texto
                    "margin-top": "10px",  # Espacio entre el slider y el título
                    "font-size": "14px",  # Tamaño de la fuente
                    "color": "#333",  # Color del texto
                }
            )
        ]),
        html.Div(
            "Puede modificar los valores en los filtros para observar el comportamiento de los indicadores abajo.",
            style={
                "text-align": "left",
                "font-size": "12px", 
                "color": "#666",  
                "margin-top": "2px" 
            })
    ], style={"margin-top": "20px"}),

    # KPIs
    # Fila para los KPIs
    dbc.Row([
        # KPI 1: Total de ciudades
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Total de Ciudades", className="card-title"),
                    html.P("Cargando...", id="total-cities-kpi", className="card-text"),
                ]),
                style={"border": "1px solid #ddd", "border-radius": "10px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
            ),
            width=3
        ),
        # KPI 2: Total de apartamentos
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Total de Apartamentos", className="card-title"),
                    html.P("Cargando...", id="total-apartments-kpi", className="card-text"),
                ]),
                style={"border": "1px solid #ddd", "border-radius": "10px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
            ),
            width=3
        ),
        # KPI 3: Precio promedio
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Precio Promedio", className="card-title"),
                    html.P("Cargando...", id="avg-price-kpi", className="card-text"),
                ]),
                style={"border": "1px solid #ddd", "border-radius": "10px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
            ),
            width=3
        ),
        # KPI 4: Longitud promedio de la descripción
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Longitud Descripción", className="card-title"),
                    html.P("Cargando...", id="avg-description-length-kpi", className="card-text"),
                ]),
                style={"border": "1px solid #ddd", "border-radius": "10px", "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
            ),
            width=3
        ),
    ], style={"margin-top": "50px"}),

    # Gráficos Descriptivos
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-plot"), width=6),
        dbc.Col([dcc.Graph(id="boxplot"),
                dcc.RadioItems(
                    id="boxplot-category",
                    options=[
                        {"label": "Tiene fotos", "value": "photos"},
                        {"label": "Permite mascotas", "value": "pets"}
                    ],
                    value="photos",
                    style={"text-align": "center"},
                    inline=True
            
                    ),
                html.Div(
                "Seleccione si desea observar la distribución de los precios por presencia de fotos o permisos de mascotas.",
                style={
                    "text-align": "left",
                    "font-size": "12px", 
                    "color": "#666",  
                    "margin-top": "2px" 
                    }
            )],
            width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="amenities-heatmap")),
        html.Div(
            "Una correlación cercana a -1 indica una relación inversa fuerte, cercana a 1 indica una relación directa fuerte, y cercana a 0 indica que no hay relación lineal entre la variable y el precio.",
            style={
                "text-align": "left",
                "font-size": "12px", 
                "color": "#666",  
                "margin-top": "2px" 
            })
    ], style={"margin-top": "20px"}),

    # Simulador de Precios
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H3("Simulador de Precios", className="text-center mb-4", style={"background-color":"#f0f0f0"}),  # Título centrado
                    
                    # Input para el número de baños
                    dbc.Label("Número de baños", className="font-weight-bold"),
                    dbc.Input(
                        id="sim-bathrooms",
                        type="number",
                        placeholder="Ej: 2",
                        min=1,
                        max=10,
                        className="mb-3"
                    ),
                    
                    # Input para el tamaño (sq ft)
                    dbc.Label("Tamaño (sq ft)", className="font-weight-bold"),
                    dbc.Input(
                        id="sim-square-feet",
                        type="number",
                        placeholder="Ej: 1000",
                        className="mb-3"
                    ),
                    
                    # Dropdown para la ciudad
                    dbc.Label("Ciudad", className="font-weight-bold"),
                    dcc.Dropdown(
                        id="sim-city",
                        placeholder="Seleccione una ciudad",
                        options=[{"label": city.replace("cityname_", ""), "value": city} for city in ciudades],
                        className="mb-3"
                    ),
                    
                    # Checklist para las amenities
                    dbc.Label("Amenities", className="font-weight-bold"),
                    dbc.Checklist(
                        id="sim-amenities",
                        options=[{"label": amenity, "value": amenity} for amenity in amenities],
                        inline=True,
                        switch=True,  # Hace que los checkboxes se vean como interruptores
                        className="mb-3"
                    ),
                    
                    # Resultado del simulador
                    html.H4(id="sim-output", className="text-center mt-4", 
                            style={
                            "font-weight": "bold",  
                            "padding": "10px",
                            "background-color": "#e9fff8",
                            "border-radius": "5px",
                            "border": "1px solid #ddd"
                        }), 
                ]),
                style={
                    "border": "1px solid #ddd",
                    "border-radius": "10px",
                    "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    "padding": "20px"
                }
            ),
            width=6
        )
    ], justify="center", className="mt-4")
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
    Output("pie-plot", "figure"),
    [Input("state-dropdown", "value"),
     Input("bathrooms-input", "value"),
     Input("square-feet-range", "value"),
     Input("amenities-checklist", "value")]
)
def update_pieplot(state, bathrooms, square_feet_range, amenities):
    # Filtrar los datos según los filtros
    filtered_data = datos.copy()
    
    if state:
        filtered_data = filtered_data[filtered_data[state] == 1]
    if bathrooms:
        filtered_data = filtered_data[filtered_data["bathrooms"] == bathrooms]
    if square_feet_range:
        filtered_data = filtered_data[
            (filtered_data["square_feet"] >= square_feet_range[0]) & 
            (filtered_data["square_feet"] <= square_feet_range[1])
        ]
    if amenities:
        for amenity in amenities:
            filtered_data = filtered_data[filtered_data[amenity] == 1]
    
    # Contar el número de dormitorios
    bedroom_counts = filtered_data["bedrooms"].value_counts().reset_index()
    bedroom_counts.columns = ["bedrooms", "count"]
    
    # Filtrar porcentajes muy pequeños (menos del 2%)
    total_count = bedroom_counts["count"].sum()
    bedroom_counts = bedroom_counts[bedroom_counts["count"] / total_count >= 0.02]  # Mantener solo valores >= 2%
    
    # Crear el gráfico de torta mejorado
    fig = px.pie(
        bedroom_counts,
        names="bedrooms",
        values="count",
        title="Distribución de Dormitorios",
        labels={"bedrooms": "Número de Dormitorios", "count": "Cantidad"},
        color_discrete_sequence=px.colors.qualitative.Pastel,  # Colores pastel
        hole=0.4,  # Agujero en el centro para un gráfico de dona
        hover_data=["count"],  # Muestra la cantidad al pasar el mouse
    )
    
    # Mejorar el diseño del gráfico
    fig.update_traces(
        marker=dict(line=dict(color="#FFFFFF", width=2)),  # Borde blanco en los sectores
        pull=[0.1 if i == bedroom_counts["count"].idxmax() else 0 for i in range(len(bedroom_counts))]  # Resaltar el sector más grande
    )
    
    fig.update_layout(
        title_x=0.5,  # Centrar el título
        legend_title_text="Dormitorios",  # Título de la leyenda
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),  # Leyenda horizontal en la parte inferior
        font=dict(size=14)  # Tamaño de la fuente
    )
    
    return fig

@app.callback(
    Output("boxplot", "figure"),
    [Input("state-dropdown", "value"),
     Input("bathrooms-input", "value"),
     Input("square-feet-range", "value"),
     Input("amenities-checklist", "value"),
     Input("boxplot-category", "value")]
)
def update_boxplot(state, bathrooms, square_feet_range, amenities, category):
    filtered_data = datos.copy()

    if state:
        filtered_data = filtered_data[filtered_data[state] == 1]
    if bathrooms:
        filtered_data = filtered_data[filtered_data["bathrooms"] == bathrooms]
    if square_feet_range:
        filtered_data = filtered_data[
            (filtered_data["square_feet"] >= square_feet_range[0]) & 
            (filtered_data["square_feet"] <= square_feet_range[1])
        ]
    if amenities:
        for amenity in amenities:
            filtered_data = filtered_data[filtered_data[amenity] == 1]

    # Definir la categoría seleccionada
    if category == "photos":
        # Identificar qué columna de fotos tiene un valor de 1 y asignarla a una nueva columna
        photo_columns = ["has_photo_No", "has_photo_Thumbnail", "has_photo_Yes"]
        filtered_data["photo_category"] = filtered_data[photo_columns].idxmax(axis=1)
        
        # Traducir las categorías al español
        filtered_data["photo_category"] = filtered_data["photo_category"].replace({
            "has_photo_No": "Sin Foto",
            "has_photo_Thumbnail": "Miniatura",
            "has_photo_Yes": "Con Foto"
        })
        
        x_axis = "photo_category"
        title = "Distribución de Precios por Presencia de Fotos"
    
    elif category == "pets":
        # Identificar qué columna de mascotas tiene un valor de 1 y asignarla a una nueva columna
        pet_columns = ["pets_allowed_Cats", "pets_allowed_Cats,Dogs", "pets_allowed_Dogs", "pets_allowed_No permitido"]
        filtered_data["pet_category"] = filtered_data[pet_columns].idxmax(axis=1)
        
        # Traducir las categorías al español
        filtered_data["pet_category"] = filtered_data["pet_category"].replace({
            "pets_allowed_Cats": "Gatos",
            "pets_allowed_Cats,Dogs": "Gatos y Perros",
            "pets_allowed_Dogs": "Perros",
            "pets_allowed_No permitido": "No Permitidas"
        })
        
        x_axis = "pet_category"
        title = "Distribución de Precios por Política de Mascotas"
    
    else:
        return px.box(title="Categoría no disponible en los datos")

    # Crear el boxplot con la categoría seleccionada
    fig = px.box(
        filtered_data,
        x=x_axis,
        y="price",
        points="all",
        title=title,
        labels={x_axis: "Categoría", "price": "Precio (USD)"}
    )
    
    fig.update_layout(
        title_x=0.5,  # Centrar el título
        title_font_size=20,  # Tamaño del título
        xaxis_title_font_size=16,  # Tamaño del título del eje x
        yaxis_title_font_size=16,  # Tamaño del título del eje y
        font=dict(family="Arial", size=14),  # Fuente y tamaño del texto
        plot_bgcolor="white",  # Fondo blanco
        xaxis=dict(showline=True, linewidth=2, linecolor="black"),  # Línea del eje x
        yaxis=dict(showline=True, linewidth=2, linecolor="black")  # Línea del eje y
    )

    fig.update_xaxes(
        tickfont=dict(size=14),  # Tamaño de las etiquetas del eje x
        categoryorder="total ascending"  # Ordenar categorías por precio ascendente
    )
    
    fig.update_yaxes(
        tickfont=dict(size=14)  # Tamaño de las etiquetas del eje y
    )

    return fig


@app.callback(
    Output("amenities-heatmap", "figure"),
    [Input("state-dropdown", "value"),
     Input("bathrooms-input", "value"),
     Input("square-feet-range", "value"),
     Input("amenities-checklist", "value")]
)
def update_amenities_heatmap(state, bathrooms, square_feet_range, amenities):
    filtered_data = datos.copy()
    
    # Filtrar por estado
    if state:
        filtered_data = filtered_data[filtered_data[state] == 1]
    
    # Filtrar por número de baños
    if bathrooms:
        filtered_data = filtered_data[filtered_data["bathrooms"] == bathrooms]
    
    # Filtrar por rango de tamaño
    if square_feet_range:
        filtered_data = filtered_data[
            (filtered_data["square_feet"] >= square_feet_range[0]) & 
            (filtered_data["square_feet"] <= square_feet_range[1])
        ]
    
    # Si no se selecciona ninguna amenidad, usar todas
    if amenities is None or len(amenities) == 0:
        amenities = [col for col in datos.columns if col.startswith("has_") or col in ["TV", "Dishwasher", "Wood Floors", "Elevator", "Clubhouse", "Doorman", "Parking", "Patio/Deck", "Luxury", "Storage", "View", "Refrigerator", "Playground", "Internet Access", "Tennis", "Gated", "Basketball", "Golf", "Garbage Disposal", "AC", "Gym", "Washer Dryer", "Pool", "Alarm", "Hot Tub", "Fireplace", "Cable or Satellite"]]
    
    # Seleccionar solo las columnas de amenities y el precio
    columns_to_include = amenities + ["price"]
    filtered_data = filtered_data[columns_to_include]
    
    # Calcular la correlación entre amenities y precio
    correlation = filtered_data.corr()
    
    # Filtrar la correlación para mostrar solo la fila del precio
    correlation_with_price = correlation[["price"]].drop("price")
    
    # Crear el gráfico de calor
    fig = px.imshow(
        correlation_with_price.T,  # Transponer para que las amenities estén en el eje x
        text_auto=".2f",  # Mostrar valores con 2 decimales
        title="Correlación entre Amenities y Precio",
        labels=dict(x="Amenidad", y="Correlación con Precio", color="Correlación"),
        color_continuous_scale="Viridis",
        aspect="auto"  # Ajustar el aspecto para que las etiquetas se vean mejor
    )
    
    # Personalizar el texto dentro del heatmap
    fig.update_traces(
        texttemplate="%{text}",  # Mostrar el texto tal como está
        textfont=dict(size=12, color="black"),  # Personalizar la fuente
    )
    
    # Ajustar el layout del gráfico
    fig.update_layout(
        xaxis_title="Amenidades",
        yaxis_title="Correlación con Precio",
        coloraxis_colorbar=dict(title="Correlación"),
        xaxis=dict(tickangle=-45)  # Rotar las etiquetas del eje x para mejor legibilidad
    )
    
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