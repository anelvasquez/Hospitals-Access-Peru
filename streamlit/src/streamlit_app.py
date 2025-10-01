import streamlit as st
import os
import geopandas as gpd
from estimation import load_and_filter_ipress, get_data_summary, get_departments_list
from plots import create_hospital_map, create_department_bar

# Configuración de página
st.set_page_config(
    page_title="Hospitales en Perú",
    page_icon="🏥",
    layout="wide"
)

# Título principal
st.title("🏥 Análisis de Hospitales Operativos en Perú")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["📂 Descripción de Datos", "📊 Análisis Estático", "🌐 Mapas Dinámicos"])

# TAB 1: Data Description
with tab1:
    st.header("📋 Descripción de Datos")
    
    # Unidad de Análisis
    st.subheader("Unidad de Análisis")
    st.markdown("**Hospitales públicos operativos** en el Perú")
    
    st.divider()
    
    # Fuentes de Datos
    st.subheader("Fuentes de Datos")
    
    st.markdown("""
    - **MINSA – IPRESS** (operational subset): Registro Nacional de Instituciones Prestadoras de Servicios de Salud
      - 🔗 URL: [Datos Abiertos Perú - MINSA IPRESS](https://datosabiertos.gob.pe/dataset/minsa-ipress)
    
    - **INEI**: Centros Poblados del Perú (Population Centers)
      - 🔗 URL: [Datos Abiertos Perú - Centros Poblados](https://datosabiertos.gob.pe/dataset/dataset-centros-poblados)
    
    - **Distritos del Perú**: Shapefile de límites administrativos (EPSG:4326)
    """)
    
    st.divider()
    
    # Reglas de Filtrado
    st.subheader("Reglas de Filtrado")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("✅ **Estado**")
        st.markdown("✅ **Coordenadas válidas**")
        st.markdown("✅ **Exclusión de nulos**")
    
    with col2:
        st.info("Solo hospitales con estado **'ACTIVO'**")
        st.info("Solo registros con coordenadas válidas (NORTE y ESTE)")
        st.info("Exclusión de coordenadas (0, 0) o valores nulos")
    
    st.divider()
    
    # Cargar datos
    @st.cache_data
    def load_data():
        # Buscar archivo Excel en data/
        excel_path = '../data/IPRESS.xlsx'
        if not os.path.exists(excel_path):
            excel_path = 'data/IPRESS.xlsx'
        if not os.path.exists(excel_path):
            raise FileNotFoundError("No se encontró IPRESS.xlsx en la carpeta data/")
        return load_and_filter_ipress(excel_path)
    
    try:
        with st.spinner('⏳ Cargando y procesando datos desde Excel...'):
            gdf_hospitals = load_data()
            
            # Verificar si hay datos
            if len(gdf_hospitals) == 0:
                st.error("❌ No se encontraron datos después del filtrado")
                st.info("🔍 Revisa la terminal/consola para ver los mensajes de debug")
                st.stop()
            
            summary = get_data_summary(gdf_hospitals)
        
        st.success(f'✅ Datos cargados: {len(gdf_hospitals)} hospitales con coordenadas válidas')
        
        # Métricas principales en 3 columnas
        st.subheader("📊 Resumen de Datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🏥 Total de Hospitales",
                value=f"{summary['total_hospitals']:,}",
                help="Total de hospitales con coordenadas válidas"
            )
        
        with col2:
            st.metric(
                label="📍 Departamentos",
                value=summary['departments'],
                help="Número de departamentos cubiertos"
            )
        
        with col3:
            st.metric(
                label="🏘️ Distritos",
                value=summary['districts'],
                help="Número de distritos con hospitales"
            )
        
        st.divider()
        
        # Gráfico de distribución por departamento
        st.subheader("📊 Distribución por Distrito")
        
        # Obtener conteo por departamento
        col_dept = None
        for c in gdf_hospitals.columns:
            if c.strip().lower() == "departamento":
                col_dept = c
                break
        
        if col_dept:
            dept_counts = gdf_hospitals[col_dept].value_counts().sort_values(ascending=False)
            
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Bar(
                    x=dept_counts.index,
                    y=dept_counts.values,
                    marker=dict(
                        color='#60a5fa',
                        line=dict(color='#2563eb', width=1)
                    ),
                    text=dept_counts.values,
                    textposition='outside',
                    textfont=dict(size=12, color='white')
                )
            ])
            
            fig.update_layout(
                height=500,
                margin=dict(l=40, r=40, t=40, b=120),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title="",
                    showgrid=False,
                    showline=False,
                    tickfont=dict(color='white', size=11),
                    tickangle=-45
                ),
                yaxis=dict(
                    title="",
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)',
                    showline=False,
                    tickfont=dict(color='white', size=11)
                ),
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Filtro por Departamento
        st.subheader("🔎 Filtrar por Departamento")
        
        departments = get_departments_list(gdf_hospitals)
        selected_dept = st.selectbox(
            "Selecciona un departamento:",
            options=["Todos"] + departments,
            index=0
        )
        
        # Aplicar filtro
        if selected_dept != "Todos":
            # Buscar columna Departamento
            col_dept = None
            for c in gdf_hospitals.columns:
                if c.strip().lower() == "departamento":
                    col_dept = c
                    break
            
            if col_dept:
                gdf_filtered = gdf_hospitals[gdf_hospitals[col_dept] == selected_dept]
                st.info(f"Mostrando {len(gdf_filtered)} hospitales en **{selected_dept}**")
            else:
                gdf_filtered = gdf_hospitals
        else:
            gdf_filtered = gdf_hospitals
        
        st.divider()
        
        # Vista previa de datos
        st.subheader("🔍 Vista Previa de Datos")
        
        # Columnas clave para mostrar
        display_columns = [
            'Institución',
            'Nombre del establecimiento',
            'Departamento',
            'Provincia',
            'Distrito',
            'Categoria',
            'Estado',
            'NORTE',
            'ESTE'
        ]
        
        # Filtrar solo las columnas que existen
        available_columns = [col for col in display_columns if col in gdf_filtered.columns]
        
        if len(available_columns) > 0:
            st.dataframe(
                gdf_filtered[available_columns].head(20),
                use_container_width=True,
                height=400
            )
        else:
            st.warning("⚠️ No se encontraron las columnas esperadas")
            st.write("Columnas disponibles:", gdf_filtered.columns.tolist())
        
        # Información adicional
        with st.expander("ℹ️ Información del Dataset"):
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown("**Dimensiones del dataset:**")
                st.write(f"- Filas totales: {len(gdf_hospitals):,}")
                st.write(f"- Filas mostradas: {len(gdf_filtered):,}")
                st.write(f"- Columnas: {len(gdf_hospitals.columns)}")
            
            with col_info2:
                st.markdown("**Sistema de coordenadas:**")
                st.write(f"- Original: UTM 18S (EPSG:32718)")
                st.write(f"- Convertido a: WGS84 (EPSG:4326)")
        
        # Guardar en session_state para otros tabs
        st.session_state['gdf_hospitals'] = gdf_hospitals
        st.session_state['gdf_filtered'] = gdf_filtered
        
    except FileNotFoundError as e:
        st.error("❌ No se encontró el archivo IPRESS.xlsx")
        st.info("💡 Asegúrate de que el archivo esté en la carpeta **data/** y se llame **IPRESS.xlsx**")
        
        with st.expander("🔍 Debug: Rutas verificadas"):
            st.write("Directorio actual:", os.getcwd())
            st.write("Buscando en:")
            st.code("../data/IPRESS.xlsx\ndata/IPRESS.xlsx")
        
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        
        with st.expander("Ver error completo"):
            import traceback
            st.code(traceback.format_exc())

# TAB 2: Análisis Estático
with tab2:
    st.header("📊 Análisis Estático de Mapas y Departamentos")
    
    if 'gdf_hospitals' not in st.session_state:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción de Datos'**")
    else:
        gdf_hospitals = st.session_state['gdf_hospitals']
        
        # Importar funciones necesarias
        from estimation import count_hospitals_by_district
        import matplotlib.pyplot as plt
        
        # Cargar shapefile de distritos
        @st.cache_data
        def load_districts_shapefile():
            shp_path = '../data/distritos.shp'
            if not os.path.exists(shp_path):
                shp_path = 'data/distritos.shp'
            if not os.path.exists(shp_path):
                raise FileNotFoundError("No se encontró el shapefile distritos.shp")
            return gpd.read_file(shp_path)
        
        try:
            with st.spinner('Cargando shapefile de distritos...'):
                gdf_districts = load_districts_shapefile()
            
            st.success(f"✅ Shapefile cargado: {len(gdf_districts)} distritos")
            
            # Contar hospitales por distrito
            hospitals_by_district = count_hospitals_by_district(gdf_hospitals)
            
            st.subheader("📋 Tabla Resumen por Departamento")
            
            # Tabla agrupada por departamento
            col_dept = None
            for c in gdf_hospitals.columns:
                if c.strip().lower() == "departamento":
                    col_dept = c
                    break
            
            if col_dept:
                dept_summary = gdf_hospitals.groupby(col_dept).size().reset_index(name='Número de Hospitales')
                dept_summary = dept_summary.sort_values('Número de Hospitales', ascending=False)
                
                # Mostrar en dos columnas: tabla y gráfico
                col_table, col_chart = st.columns([1, 1])
                
                with col_table:
                    st.dataframe(
                        dept_summary,
                        use_container_width=True,
                        height=400,
                        hide_index=True
                    )
                
                with col_chart:
                    # Gráfico de barras horizontales (top 10)
                    top10 = dept_summary.head(10)
                    
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[
                        go.Bar(
                            y=top10[col_dept],
                            x=top10['Número de Hospitales'],
                            orientation='h',
                            marker=dict(color='#f97316')
                        )
                    ])
                    
                    fig.update_layout(
                        title="Top 10 Departamentos",
                        height=400,
                        margin=dict(l=10, r=10, t=40, b=10),
                        yaxis=dict(autorange="reversed"),
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Mapa estático
            st.subheader("🗺️ Mapa de Distribución por Distrito")
            
            # Preparar datos para el merge
            # Necesitamos identificar la columna clave en el shapefile
            st.info(f"Columnas en shapefile: {', '.join(gdf_districts.columns[:10].tolist())}")
            
            # Buscar columna UBIGEO o similar
            ubigeo_col = None
            for col in gdf_districts.columns:
                if 'UBIGEO' in col.upper() or 'CODIGO' in col.upper():
                    ubigeo_col = col
                    break
            
            if ubigeo_col and 'UBIGEO' in hospitals_by_district.columns:
                # Merge por UBIGEO
                gdf_merged = gdf_districts.merge(
                    hospitals_by_district[['UBIGEO', 'n_hospitales']],
                    left_on=ubigeo_col,
                    right_on='UBIGEO',
                    how='left'
                )
                gdf_merged['n_hospitales'] = gdf_merged['n_hospitales'].fillna(0)
                
                # Crear mapa con matplotlib
                fig, ax = plt.subplots(1, 1, figsize=(12, 14))
                
                gdf_merged.plot(
                    column='n_hospitales',
                    cmap='YlOrRd',
                    linewidth=0.5,
                    edgecolor='white',
                    legend=True,
                    ax=ax,
                    legend_kwds={
                        'label': "Número de Hospitales",
                        'orientation': "vertical",
                        'shrink': 0.8
                    }
                )
                
                ax.set_title('Distribución de Hospitales por Distrito', fontsize=16, pad=20)
                ax.axis('off')
                
                st.pyplot(fig)
                
            else:
                st.warning("⚠️ No se pudo hacer el merge. Revisa las columnas del shapefile.")
                st.write("Columnas del shapefile:", gdf_districts.columns.tolist())
                st.write("Columnas de hospitales:", hospitals_by_district.columns.tolist())
            
        except FileNotFoundError as e:
            st.error(f"❌ {str(e)}")
            st.info("💡 Asegúrate de que el archivo distritos.shp esté en la carpeta data/")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Ver error completo"):
                st.code(traceback.format_exc())

# TAB 3: Mapas Dinámicos
with tab3:
    st.header("🌐 Mapas Dinámicos")
    
    st.markdown("""
    - **National Folium choropleth + markers**: Mapa nacional con coropletas y marcadores
    - **Folium proximity maps for Lima & Loreto**: Mapas de proximidad para Lima y Loreto
    """)
    
    if 'gdf_filtered' in st.session_state:
        try:
            st.info("🚧 Mapas interactivos con Folium (próximamente)")
            
            # Mapa básico
            map_fig = create_hospital_map(st.session_state['gdf_filtered'])
            st.plotly_chart(map_fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción de Datos'**")