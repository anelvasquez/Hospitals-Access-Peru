import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd

def load_and_filter_ipress(filepath):
    """
    Carga y filtra hospitales operativos con coordenadas válidas
    """
    # Cargar datos
    df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
    
    # Filtrar hospitales operativos
    # Ajusta el nombre de la columna según tu dataset
    df_operational = df[df['estado'].str.upper() == 'ACTIVO'].copy()
    
    # Filtrar solo registros con coordenadas válidas
    df_operational = df_operational.dropna(subset=['latitud', 'longitud'])
    df_operational = df_operational[
        (df_operational['latitud'] != 0) & 
        (df_operational['longitud'] != 0)
    ]
    
    # Convertir a GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df_operational,
        geometry=gpd.points_from_xy(df_operational['longitud'], 
                                     df_operational['latitud']),
        crs='EPSG:4326'
    )
    
    return gdf

def load_population_centers(filepath):
    """
    Carga centros poblados
    """
    gdf = gpd.read_file(filepath)
    gdf = gdf.to_crs('EPSG:4326')
    return gdf

def load_districts(filepath):
    """
    Carga distritos del Perú
    """
    gdf = gpd.read_file(filepath)
    gdf = gdf.to_crs('EPSG:4326')
    return gdf

def get_data_summary(gdf_hospitals):
    """
    Genera resumen de datos para el Tab 1
    """
    summary = {
        'total_hospitals': len(gdf_hospitals),
        'departments': gdf_hospitals['departamento'].nunique(),
        'provinces': gdf_hospitals['provincia'].nunique(),
        'districts': gdf_hospitals['distrito'].nunique()
    }
    return summary