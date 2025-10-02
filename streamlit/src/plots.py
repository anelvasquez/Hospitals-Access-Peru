import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

def create_static_choropleth_map(gdf_districts_with_counts, title="Hospitales por Distrito"):
    """
    Crea un mapa coroplético estático con matplotlib/geopandas.
    
    Args:
        gdf_districts_with_counts: GeoDataFrame con geometrías de distritos y columna 'n_hospitales'
        title: Título del mapa
    
    Returns:
        fig: Figura de matplotlib
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # Mapa coroplético
    gdf_districts_with_counts.plot(
        column='n_hospitales',
        ax=ax,
        legend=True,
        cmap='Greens',
        edgecolor='black',
        linewidth=0.3,
        legend_kwds={
            'label': "Número de Hospitales",
            'orientation': "vertical",
            'shrink': 0.6
        }
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    
    plt.tight_layout()
    return fig

def create_static_map_with_points(gdf_districts, gdf_hospitals, title="Mapa de Hospitales"):
    """
    Crea un mapa estático con distritos y puntos de hospitales.
    
    Args:
        gdf_districts: GeoDataFrame con geometrías de distritos
        gdf_hospitals: GeoDataFrame con puntos de hospitales
        title: Título del mapa
    
    Returns:
        fig: Figura de matplotlib
    """
    fig, ax = plt.subplots(1, 1, figsize=(15, 12))
    
    # Dibujar distritos (fondo gris claro)
    gdf_districts.plot(
        ax=ax,
        color='lightgray',
        edgecolor='black',
        linewidth=0.3,
        alpha=0.5
    )
    
    # Dibujar hospitales (puntos verdes)
    gdf_hospitals.plot(
        ax=ax,
        color='green',
        markersize=20,
        alpha=0.7,
        label='Hospitales'
    )
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    # Leyenda
    green_patch = mpatches.Patch(color='green', label='Hospitales')
    ax.legend(handles=[green_patch], loc='lower right', fontsize=12)
    
    plt.tight_layout()
    return fig

def create_department_static_map(gdf_districts, gdf_hospitals, department_name):
    """
    Crea un mapa estático para un departamento específico.
    
    Args:
        gdf_districts: GeoDataFrame completo de distritos
        gdf_hospitals: GeoDataFrame completo de hospitales
        department_name: Nombre del departamento a filtrar
    
    Returns:
        fig: Figura de matplotlib
    """
    # Buscar columna de departamento en hospitales
    col_dept_hosp = None
    for c in gdf_hospitals.columns:
        if c.strip().lower() == "departamento":
            col_dept_hosp = c
            break
    
    # Filtrar hospitales del departamento
    if col_dept_hosp:
        gdf_hosp_dept = gdf_hospitals[gdf_hospitals[col_dept_hosp] == department_name]
    else:
        gdf_hosp_dept = gdf_hospitals
    
    # Buscar columna de departamento en distritos
    col_dept_dist = None
    for col in gdf_districts.columns:
        col_lower = col.lower()
        if 'depa' in col_lower or 'nombdepa' in col_lower:
            col_dept_dist = col
            break
    
    # Filtrar distritos del departamento
    if col_dept_dist:
        gdf_dist_dept = gdf_districts[gdf_districts[col_dept_dist].str.upper() == department_name.upper()]
    else:
        gdf_dist_dept = gdf_districts
    
    # Verificar que hay datos
    if len(gdf_dist_dept) == 0:
        print(f"No se encontraron distritos para {department_name}")
        return None
    
    # Calcular aspect ratio basado en los límites del departamento
    minx, miny, maxx, maxy = gdf_dist_dept.total_bounds
    width = maxx - minx
    height = maxy - miny
    aspect = width / height if height > 0 else 1
    
    # Ajustar figsize para mantener proporciones
    if aspect > 1:
        figsize = (14, 14/aspect)
    else:
        figsize = (14*aspect, 14)
    
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Dibujar distritos con paleta azul
    gdf_dist_dept.plot(
        ax=ax,
        color='#e3f2fd',
        edgecolor='#1976d2',
        linewidth=0.8,
        alpha=0.6
    )
    
    # Dibujar hospitales con puntos verdes
    if len(gdf_hosp_dept) > 0:
        gdf_hosp_dept.plot(
            ax=ax,
            color='#00a650',
            markersize=120,
            alpha=0.8,
            edgecolor='darkgreen',
            linewidth=1.5
        )
    
    # Título más prominente
    ax.set_title(f'Hospitales en {department_name}\n({len(gdf_hosp_dept)} hospitales)', 
                 fontsize=22, fontweight='bold', pad=25)
    
    # Remover ejes
    ax.set_axis_off()
    
    # Ajustar límites al departamento con margen
    margin = 0.05
    ax.set_xlim(minx - margin * width, maxx + margin * width)
    ax.set_ylim(miny - margin * height, maxy + margin * height)
    
    # Leyenda más visible
    green_patch = mpatches.Patch(color='#00a650', label=f'Hospitales ({len(gdf_hosp_dept)})')
    ax.legend(handles=[green_patch], loc='upper right', fontsize=16, frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig