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
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
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

def create_zero_hospitals_map(gdf_districts_with_counts, title="Distritos sin Hospitales"):
    """
    Crea un mapa mostrando solo los distritos con cero hospitales en rojo.
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    gdf_plot = gdf_districts_with_counts.copy()
    
    gdf_plot['color'] = gdf_plot['n_hospitales'].apply(
        lambda x: '#ff0000' if x == 0 else '#e0e0e0'
    )
    
    gdf_plot.plot(
        ax=ax,
        color=gdf_plot['color'],
        edgecolor='black',
        linewidth=0.3,
        alpha=0.7
    )
    
    n_zero = (gdf_districts_with_counts['n_hospitales'] == 0).sum()
    
    ax.set_title(f'{title}\n({n_zero} distritos sin hospitales)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    
    red_patch = mpatches.Patch(color='#ff0000', label=f'Sin hospitales ({n_zero})')
    gray_patch = mpatches.Patch(color='#e0e0e0', label='Con hospitales')
    ax.legend(handles=[red_patch, gray_patch], loc='lower right', fontsize=11)
    
    plt.tight_layout()
    return fig

def create_top10_hospitals_map(gdf_districts_with_counts, title="Top 10 Distritos con Más Hospitales"):
    """
    Crea un mapa destacando los 10 distritos con más hospitales.
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    gdf_plot = gdf_districts_with_counts.copy()
    
    top10_threshold = gdf_plot.nlargest(10, 'n_hospitales')['n_hospitales'].min()
    gdf_plot['is_top10'] = gdf_plot['n_hospitales'] >= top10_threshold
    
    gdf_not_top10 = gdf_plot[~gdf_plot['is_top10']]
    gdf_not_top10.plot(
        ax=ax,
        color='#e0e0e0',
        edgecolor='black',
        linewidth=0.3,
        alpha=0.5
    )
    
    gdf_top10 = gdf_plot[gdf_plot['is_top10']]
    if len(gdf_top10) > 0:
        gdf_top10.plot(
            column='n_hospitales',
            ax=ax,
            cmap='Greens',
            edgecolor='darkgreen',
            linewidth=0.8,
            alpha=0.9,
            legend=True,
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