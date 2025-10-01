import streamlit as st
from estimation import load_and_filter_ipress, get_data_summary
from plots import create_hospital_map, create_department_bar

# Configuración de página
st.set_page_config(
    page_title="Hospitales en Perúxxxxx",
    page_icon="🏥",
    layout="wide"
)

# Título principal
st.title("🏥 Análisis de Hospitales Operativos en Perúxxxxxx")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["🗂️ Descripción de xxxxxDatos", "📊 Análisisxxxx", "🗺️ Mapa"])

# TAB 1: Descripción de Datos
with tab1:
    st.header("📋 Descripción de Datos")
    
    # Información general
    st.markdown("""
    ### Unidad de Análisis
    **Hospitales públicos operativos** en el Perú
    
    ### Fuentes de Datos
    - **MINSA - IPRESS**: Registro Nacional de Instituciones Prestadoras de Servicios de Salud
      - URL: [Datos Abiertos Perú - MINSA IPRESS](https://datosabiertos.gob.pe/dataset/minsa-ipress)
    - **INEI**: Centros Poblados del Perú
      - URL: [Datos Abiertos Perú - Centros Poblados](https://datosabiertos.gob.pe/dataset/dataset-centros-poblados)
    - **Distritos del Perú**: Shapefile de límites administrativos (EPSG:4326)
    
    ### Reglas de Filtrado
    ✅ Solo hospitales con estado **"ACTIVO"**  
    ✅ Solo registros con **coordenadas válidas** (NORTE y ESTE)  
    ✅ Exclusión de coordenadas (0, 0) o valores nulos
    """)
    
    st.divider()
    
    # Cargar datos (con cache para eficiencia)
    @st.cache_data
    def load_data():
        # Reemplaza con tu ruta de archivo
        hospitals = load_and_filter_ipress('data/ipress.csv')
        return hospitals
    
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

# TAB 2: Análisis (placeholder)
with tab2:
    st.header("📊 Análisis Estadístico")
    st.info("🚧 En construcción...")

# TAB 3: Mapa (placeholder)
with tab3:
    st.header("🗺️ Mapa Interactivo")
    st.info("🚧 En construcción...")