import plotly.express as px
import plotly.graph_objects as go

def create_hospital_map(gdf_hospitals, gdf_districts=None):
    """
    Crea mapa interactivo de hospitales
    """
    fig = px.scatter_mapbox(
        gdf_hospitals,
        lat=gdf_hospitals.geometry.y,
        lon=gdf_hospitals.geometry.x,
        hover_name='Nombre del establecimiento',
        hover_data=['Departamento', 'Provincia', 'Distrito', 'Categoria'],
        zoom=5,
        height=600
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": -9.19, "lon": -75.0152},
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    return fig

def create_department_bar(gdf_hospitals):
    """
    Gráfico de barras por departamento
    """
    dept_counts = gdf_hospitals['Departamento'].dropna().value_counts().head(10)
    
    fig = go.Figure(data=[
        go.Bar(x=dept_counts.values, 
               y=dept_counts.index, 
               orientation='h',
               marker_color='#2E86AB')
    ])
    
    fig.update_layout(
        title='Top 10 Departamentos con más hospitales',
        xaxis_title='Número de hospitales',
        yaxis_title='Departamento',
        height=400
    )
    
    return fig