import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import folium
from folium import plugins

def create_hospital_map(gdf_hospitals, gdf_districts=None):
    """Crea mapa interactivo de hospitales"""
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
    """Gráfico de barras por departamento"""
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
    """Crea un mapa coroplético estático con matplotlib/geopandas."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    gdf_districts_with_counts.plot(
        column='n_hospitales',
        ax=ax,
        legend=True,
        cmap='Greens',
        edgecolor='black',
        linewidth=0.3,
        legend_kwds={'label': "Número de Hospitales", 'orientation': "vertical", 'shrink': 0.6}
    )
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    plt.tight_layout()
    return fig

def create_zero_hospitals_map(gdf_districts_with_counts, title="Distritos sin Hospitales"):
    """Crea un mapa mostrando solo los distritos con cero hospitales en rojo."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    gdf_plot = gdf_districts_with_counts.copy()
    gdf_plot['color'] = gdf_plot['n_hospitales'].apply(lambda x: '#ff0000' if x == 0 else '#e0e0e0')
    gdf_plot.plot(ax=ax, color=gdf_plot['color'], edgecolor='black', linewidth=0.3, alpha=0.7)
    n_zero = (gdf_districts_with_counts['n_hospitales'] == 0).sum()
    ax.set_title(f'{title}\n({n_zero} distritos sin hospitales)', fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    red_patch = mpatches.Patch(color='#ff0000', label=f'Sin hospitales ({n_zero})')
    gray_patch = mpatches.Patch(color='#e0e0e0', label='Con hospitales')
    ax.legend(handles=[red_patch, gray_patch], loc='lower right', fontsize=11)
    plt.tight_layout()
    return fig

def create_top10_hospitals_map(gdf_districts_with_counts, title="Top 10 Distritos con Más Hospitales"):
    """Crea un mapa destacando los 10 distritos con más hospitales."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    gdf_plot = gdf_districts_with_counts.copy()
    top10_threshold = gdf_plot.nlargest(10, 'n_hospitales')['n_hospitales'].min()
    gdf_plot['is_top10'] = gdf_plot['n_hospitales'] >= top10_threshold
    gdf_not_top10 = gdf_plot[~gdf_plot['is_top10']]
    gdf_not_top10.plot(ax=ax, color='#e0e0e0', edgecolor='black', linewidth=0.3, alpha=0.5)
    gdf_top10 = gdf_plot[gdf_plot['is_top10']]
    if len(gdf_top10) > 0:
        gdf_top10.plot(column='n_hospitales', ax=ax, cmap='Greens', edgecolor='darkgreen', 
                      linewidth=0.8, alpha=0.9, legend=True,
                      legend_kwds={'label': "Número de Hospitales", 'orientation': "vertical", 'shrink': 0.6})
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    plt.tight_layout()
    return fig

def create_national_folium_choropleth(gdf_districts_with_counts, gdf_hospitals):
    """Crea un mapa Folium nacional con coropletas y marcadores de hospitales."""
    m = folium.Map(location=[-9.19, -75.0152], zoom_start=6, tiles='OpenStreetMap')
    
    geojson_data = gdf_districts_with_counts.__geo_interface__
    folium.Choropleth(
        geo_data=geojson_data,
        name='Hospitales por Distrito',
        data=gdf_districts_with_counts,
        columns=['UBIGEO_NORM', 'n_hospitales'],
        key_on='feature.properties.UBIGEO_NORM',
        fill_color='Greens',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Número de Hospitales',
        highlight=True
    ).add_to(m)
    
    marker_cluster = plugins.MarkerCluster(name='Hospitales').add_to(m)
    
    col_nombre = None
    col_dept = None
    col_dist = None
    for c in gdf_hospitals.columns:
        c_lower = c.strip().lower()
        if 'nombre' in c_lower and 'establecimiento' in c_lower:
            col_nombre = c
        elif c_lower == 'departamento':
            col_dept = c
        elif c_lower == 'distrito':
            col_dist = c
    
    for idx, row in gdf_hospitals.head(500).iterrows():
        nombre = row[col_nombre] if col_nombre else 'Hospital'
        dept = row[col_dept] if col_dept else ''
        dist = row[col_dist] if col_dist else ''
        popup_text = f"<b>{nombre}</b><br>Departamento: {dept}<br>Distrito: {dist}"
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            popup=folium.Popup(popup_text, max_width=300),
            color='green',
            fill=True,
            fillColor='green',
            fillOpacity=0.7
        ).add_to(marker_cluster)
    
    folium.LayerControl().add_to(m)
    return m

def create_proximity_map_lima(gdf_hospitals, gdf_districts):
    """Crea un mapa de proximidad para Lima (alta densidad)."""
    col_dept = None
    for c in gdf_hospitals.columns:
        if c.strip().lower() == 'departamento':
            col_dept = c
            break
    
    if col_dept:
        gdf_lima = gdf_hospitals[gdf_hospitals[col_dept] == 'LIMA']
    else:
        gdf_lima = gdf_hospitals
    
    if len(gdf_lima) == 0:
        return folium.Map(location=[-12.0464, -77.0428], zoom_start=10)
    
    center_lat = gdf_lima.geometry.y.mean()
    center_lon = gdf_lima.geometry.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='OpenStreetMap')
    
    col_nombre = None
    for c in gdf_lima.columns:
        if 'nombre' in c.strip().lower() and 'establecimiento' in c.strip().lower():
            col_nombre = c
            break
    
    for idx, row in gdf_lima.iterrows():
        nombre = row[col_nombre] if col_nombre else 'Hospital'
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=nombre,
            icon=folium.Icon(color='red', icon='plus', prefix='fa')
        ).add_to(m)
        folium.Circle(
            location=[row.geometry.y, row.geometry.x],
            radius=2500,
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.1,
            popup=f'Área de cobertura: {nombre}'
        ).add_to(m)
    
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 200px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Lima - Alta Densidad</b></p>
    <p><i class="fa fa-circle" style="color:red"></i> Radio: 2.5 km</p>
    <p>Total hospitales: {len(gdf_lima)}</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

def create_proximity_map_loreto(gdf_hospitals, gdf_districts):
    """Crea un mapa de proximidad para Loreto (baja densidad)."""
    col_dept = None
    for c in gdf_hospitals.columns:
        if c.strip().lower() == 'departamento':
            col_dept = c
            break
    
    if col_dept:
        gdf_loreto = gdf_hospitals[gdf_hospitals[col_dept] == 'LORETO']
    else:
        gdf_loreto = gdf_hospitals
    
    if len(gdf_loreto) == 0:
        return folium.Map(location=[-3.7437, -73.2516], zoom_start=7)
    
    center_lat = gdf_loreto.geometry.y.mean()
    center_lon = gdf_loreto.geometry.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles='OpenStreetMap')
    
    col_nombre = None
    for c in gdf_loreto.columns:
        if 'nombre' in c.strip().lower() and 'establecimiento' in c.strip().lower():
            col_nombre = c
            break
    
    for idx, row in gdf_loreto.iterrows():
        nombre = row[col_nombre] if col_nombre else 'Hospital'
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=nombre,
            icon=folium.Icon(color='blue', icon='plus', prefix='fa')
        ).add_to(m)
        folium.Circle(
            location=[row.geometry.y, row.geometry.x],
            radius=10000,
            color='blue',
            fill=True,
            fillColor='blue',
            fillOpacity=0.1,
            popup=f'Área de cobertura: {nombre}'
        ).add_to(m)
    
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 200px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Loreto - Baja Densidad</b></p>
    <p><i class="fa fa-circle" style="color:blue"></i> Radio: 10 km</p>
    <p>Total hospitales: {len(gdf_loreto)}</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return m