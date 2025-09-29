import pandas as pd
import geopandas as gpd

def load_and_filter_ipress(filepath):
    """
    Carga y filtra hospitales operativos con coordenadas válidas
    """
    # Cargar datos
    df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
    
    # Filtrar hospitales operativos (Estado = ACTIVO)
    df_operational = df[df['Estado'].str.upper() == 'ACTIVO'].copy()
    
    # Filtrar solo registros con coordenadas válidas
    df_operational = df_operational.dropna(subset=['NORTE', 'ESTE'])
    df_operational = df_operational[
        (df_operational['NORTE'] != 0) & 
        (df_operational['ESTE'] != 0)
    ]
    
    # Convertir UTM a lat/lon (asumiendo zona 18S para Perú)
    # NORTE = latitud UTM, ESTE = longitud UTM
    gdf = gpd.GeoDataFrame(
        df_operational,
        geometry=gpd.points_from_xy(df_operational['ESTE'], 
                                     df_operational['NORTE']),
        crs='EPSG:32718'  # UTM Zona 18S
    )
    
    # Convertir a coordenadas geográficas
    gdf = gdf.to_crs('EPSG:4326')
    
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
        'departments': gdf_hospitals['Departamento'].nunique(),
        'provinces': gdf_hospitals['Provincia'].nunique(),
        'districts': gdf_hospitals['Distrito'].nunique()
    }
    return summary