import streamlit as st
import os
from estimation import load_and_filter_ipress, get_data_summary
from plots import create_hospital_map, create_department_bar

# Configuración de página
st.set_page_config(
    page_title="Hospitales en Perúxxxx",
    page_icon="🏥",
    layout="wide"
)

# Título principal
st.title("🏥 Análisis de Hospitales Operativos en Perú")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["🗂️ Descripción de Datosxxxxx", "📊 Análisis", "🗺️ Mapa"])

# TAB 1: Descripción de Datos
with tab1:
    st.header("📋 Descripción de Datos")
    
    # Información general
    st.markdown("""
    ### Unidad de Análisis
    *Hospitales públicos operativos* en el Perú
    
    ### Fuentes de Datos
    - *MINSA - IPRESS*: Registro Nacional de Instituciones Prestadoras de Servicios de Salud  
      - URL: [Datos Abiertos Perú - MINSA IPRESS](https://datosabiertos.gob.pe/dataset/minsa-ipress)  
    - *INEI*: Centros Poblados del Perú  
      - URL: [Datos Abiertos Perú - Centros Poblados](https://datosabiertos.gob.pe/dataset/dataset-centros-poblados)  
    - *Distritos del Perú*: Shapefile de límites administrativos (EPSG:4326)
    
    ### Reglas de Filtrado
    ✅ Solo hospitales con estado *"ACTIVO"*  
    ✅ Solo registros con *coordenadas válidas* (NORTE y ESTE)  
    ✅ Exclusión de coordenadas (0, 0) o valores nulos
    """)
    
    st.divider()
    
    # DEBUG: Mostrar rutas disponibles
    with st.expander("🔍 Debug: Verificar archivos"):
        st.write("**Directorio actual:**", os.getcwd())
        
        # Buscar archivo IPRESS
        possible_paths = [
            '../data/IPRESS.csv',
            'data/IPRESS.csv',
            './IPRESS.csv',
            'IPRESS.csv'
        ]
        
        st.write("**Buscando archivo IPRESS.csv:**")
        for path in possible_paths:
            exists = os.path.exists(path)
            st.write(f"- `{path}`: {'✅ Existe' if exists else '❌ No encontrado'}")
        
        # Mostrar archivos en carpeta data
        if os.path.exists('../data'):
            st.write("**Archivos en ../data/:**")
            st.write(os.listdir('../data'))
        if os.path.exists('data'):
            st.write("**Archivos en data/:**")
            st.write(os.listdir('data'))
    
    # Cargar datos (con cache para eficiencia)
    @st.cache_data
    def load_data():
        # Intentar diferentes rutas
        for path in ['../data/IPRESS.csv', 'data/IPRESS.csv', 'IPRESS.csv']:
            if os.path.exists(path):
                st.info(f"📂 Cargando desde: {path}")
                return load_and_filter_ipress(path)
        raise FileNotFoundError("No se encontró IPRESS.csv en ninguna ubicación conocida")
    
    try:
        with st.spinner('Cargando datos...'):
            gdf_hospitals = load_data()
            summary = get_data_summary(gdf_hospitals)
        
        st.success('✅ Datos cargados exitosamente')
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏥 Total Hospitales", summary['total_hospitals'])
        with col2:
            st.metric("📍 Departamentos", summary['departments'])
        with col3:
            st.metric("🗺️ Provincias", summary['provinces'])
        with col4:
            st.metric("🏘️ Distritos", summary['districts'])
        
        # Muestra de datos
        st.subheader("Vista previa de datos")
        st.dataframe(
            gdf_hospitals[['Nombre del establecimiento', 'Departamento', 
                          'Provincia', 'Distrito', 'Categoria', 'Estado']].head(10),
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        st.info("💡 Asegúrate de que el archivo CSV esté en la carpeta correcta")
        
        # Mostrar traceback completo
        import traceback
        with st.expander("Ver error completo"):
            st.code(traceback.format_exc())

# TAB 2: Análisis
with tab2:
    st.header("📊 Análisis Estadístico")
    try:
        if 'gdf_hospitals' in locals():
            bar_chart = create_department_bar(gdf_hospitals)
            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.warning("⚠️ Primero carga los datos en la pestaña 'Descripción de Datos'")
    except Exception as e:
        st.error(f"Error: {e}")

# TAB 3: Mapa
with tab3:
    st.header("🗺️ Mapa Interactivo")
    try:
        if 'gdf_hospitals' in locals():
            map_fig = create_hospital_map(gdf_hospitals)
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.warning("⚠️ Primero carga los datos en la pestaña 'Descripción de Datos'")
    except Exception as e:
        st.error(f"Error: {e}")