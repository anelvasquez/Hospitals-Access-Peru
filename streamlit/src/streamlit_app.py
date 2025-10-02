import streamlit as st
import os
from estimation import load_and_filter_ipress, get_data_summary, get_departments_list
from plots import create_hospital_map, create_department_bar
import matplotlib
matplotlib.use('Agg')  # Backend para Streamlit

# Configuración de página
st.set_page_config(
    page_title="Hospitales en Perús",
    page_icon="🏥",
    layout="wide"
)

# Título principal
st.title("🏥 Análisis de Hospitales Operativos en Perú")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["📂 Descripción de Datos", "📊 Análisis Estático", "🌍 Mapas Dinámicos"])

# TAB 1: Data Description (SIN CAMBIOS)
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

# TAB 2: Análisis Estático (3 MAPAS)
with tab2:
    st.header("🗺️ Mapas Estáticos y Análisis por Departamento")
    
    if 'gdf_hospitals' not in st.session_state:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción de Datos'**")
    else:
        try:
            # Cargar shapefile de distritos
            @st.cache_data
            def load_districts():
                # Buscar v_distritos_2023.shp
                shapefile_path = '../data/v_distritos_2023.shp'
                if not os.path.exists(shapefile_path):
                    shapefile_path = 'data/v_distritos_2023.shp'
                if not os.path.exists(shapefile_path):
                    raise FileNotFoundError("No se encontró v_distritos_2023.shp")
                
                from estimation import load_districts_shapefile, merge_hospitals_with_districts
                gdf_dist = load_districts_shapefile(shapefile_path)
                
                # Hacer merge con hospitales
                gdf_merged = merge_hospitals_with_districts(
                    st.session_state['gdf_hospitals'], 
                    gdf_dist
                )
                
                return gdf_dist, gdf_merged
            
            with st.spinner('📍 Cargando shapefile de distritos...'):
                gdf_districts, gdf_districts_merged = load_districts()
            
            st.success(f'✅ Shapefile cargado: {len(gdf_districts)} distritos')
            
            st.divider()
            
            # MAPA 1: Distribución Nacional de Hospitales por Distrito
            st.subheader("🗺️ Mapa 1: Distribución de Hospitales por Distrito")
            
            with st.spinner('Generando mapa nacional...'):
                from plots import create_static_choropleth_map
                
                fig_choropleth = create_static_choropleth_map(
                    gdf_districts_merged,
                    title="Distribución de Hospitales por Distrito en Perú"
                )
                
                st.pyplot(fig_choropleth)
            
            # Estadísticas del mapa 1
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_hosp = gdf_districts_merged['n_hospitales'].sum()
                st.metric("🏥 Total Hospitales", f"{int(total_hosp):,}")
            
            with col2:
                distritos_con_hosp = (gdf_districts_merged['n_hospitales'] > 0).sum()
                st.metric("🏘️ Distritos con Hospitales", f"{distritos_con_hosp:,}")
            
            with col3:
                distritos_sin_hosp = (gdf_districts_merged['n_hospitales'] == 0).sum()
                st.metric("❌ Distritos sin Hospitales", f"{distritos_sin_hosp:,}")
            
            st.divider()
            
            # MAPA 2: Distritos sin Hospitales
            st.subheader("🗺️ Mapa 2: Distritos sin Hospitales Públicos")
            
            with st.spinner('Generando mapa de distritos sin hospitales...'):
                from plots import create_zero_hospitals_map
                
                fig_zero = create_zero_hospitals_map(
                    gdf_districts_merged,
                    title="Distritos sin Hospitales Públicos"
                )
                
                st.pyplot(fig_zero)
            
            st.info(f"📊 **{distritos_sin_hosp} distritos** ({(distritos_sin_hosp/len(gdf_districts_merged)*100):.1f}% del total) no cuentan con hospitales públicos")
            
            st.divider()
            
            # MAPA 3: Top 10 Distritos con Más Hospitales
            st.subheader("🗺️ Mapa 3: Top 10 Distritos con Más Hospitales")
            
            with st.spinner('Generando mapa de top 10 distritos...'):
                from plots import create_top10_hospitals_map
                
                fig_top10 = create_top10_hospitals_map(
                    gdf_districts_merged,
                    title="Top 10 Distritos con Mayor Número de Hospitales"
                )
                
                st.pyplot(fig_top10)
            
            # Tabla del Top 10
            top10_data = gdf_districts_merged.nlargest(10, 'n_hospitales')[['DISTRITO_NORM', 'n_hospitales']].copy()
            top10_data.columns = ['Distrito', 'Número de Hospitales']
            top10_data = top10_data.reset_index(drop=True)
            top10_data.index = top10_data.index + 1
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**📋 Ranking de Distritos**")
                st.dataframe(
                    top10_data,
                    use_container_width=True,
                    height=400
                )
            
            with col2:
                st.markdown("**📈 Estadísticas Top 10**")
                st.metric("Total hospitales Top 10", f"{int(top10_data['Número de Hospitales'].sum()):,}")
                st.metric("Promedio por distrito", f"{top10_data['Número de Hospitales'].mean():.1f}")
                st.metric("Máximo", f"{int(top10_data['Número de Hospitales'].max()):,}")
            
            st.divider()
            
            # Gráfico de Barras por Departamento
            st.subheader("📊 Top 10 Departamentos con Más Hospitales")
            
            bar_chart = create_department_bar(st.session_state['gdf_hospitals'])
            st.plotly_chart(bar_chart, use_container_width=True)
            
        except FileNotFoundError as e:
            st.error("❌ No se encontró el archivo v_distritos_2023.shp")
            st.info("💡 Asegúrate de que el shapefile esté en la carpeta **data/** con sus archivos asociados (.shp, .shx, .dbf, .prj)")
            
            with st.expander("🔍 Debug: Archivos buscados"):
                st.write("Buscando en:")
                st.code("../data/v_distritos_2023.shp\ndata/v_distritos_2023.shp")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
            with st.expander("Ver error completo"):
                import traceback
                st.code(traceback.format_exc())

# TAB 3: Mapas Dinámicos
with tab3:
    st.header("🌍 Mapas Dinámicos con Folium")
    
    if 'gdf_hospitals' not in st.session_state:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción de Datos'**")
    else:
        try:
            # Cargar shapefile si no está cargado
            if 'gdf_districts_merged' not in locals():
                @st.cache_data
                def load_districts_tab3():
                    shapefile_path = '../data/v_distritos_2023.shp'
                    if not os.path.exists(shapefile_path):
                        shapefile_path = 'data/v_distritos_2023.shp'
                    if not os.path.exists(shapefile_path):
                        raise FileNotFoundError("No se encontró v_distritos_2023.shp")
                    
                    from estimation import load_districts_shapefile, merge_hospitals_with_districts
                    gdf_dist = load_districts_shapefile(shapefile_path)
                    gdf_merged = merge_hospitals_with_districts(
                        st.session_state['gdf_hospitals'], 
                        gdf_dist
                    )
                    return gdf_dist, gdf_merged
                
                gdf_districts, gdf_districts_merged = load_districts_tab3()
            
            # MAPA 1: Coropleta Nacional con Marcadores
            st.subheader("🗺️ Mapa Nacional: Coropleta + Marcadores de Hospitales")
            st.markdown("Mapa interactivo que muestra la densidad de hospitales por distrito (coropleta en verde) y la ubicación exacta de cada hospital (marcadores agrupados).")
            
            with st.spinner('Generando mapa nacional interactivo...'):
                from plots import create_national_folium_choropleth
                from streamlit_folium import folium_static
                
                map_national = create_national_folium_choropleth(
                    gdf_districts_merged,
                    st.session_state['gdf_hospitals']
                )
                
                folium_static(map_national, width=1200, height=600)
            
            st.info("💡 Haz clic en los clusters verdes para expandir y ver hospitales individuales. Puedes hacer zoom y navegar por todo el país.")
            
            st.divider()
            
            # MAPAS DE PROXIMIDAD
            st.subheader("📍 Mapas de Proximidad por Región")
            st.markdown("Los círculos de proximidad muestran el área de cobertura estimada de cada hospital. El radio varía según la densidad poblacional de la región.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔴 Lima - Alta Densidad")
                st.markdown("**Radio de cobertura: 2.5 km**")
                st.markdown("Lima tiene alta concentración de hospitales debido a la densidad poblacional.")
                
                with st.spinner('Generando mapa de Lima...'):
                    from plots import create_proximity_map_lima
                    
                    map_lima = create_proximity_map_lima(
                        st.session_state['gdf_hospitals'],
                        gdf_districts
                    )
                    
                    folium_static(map_lima, width=550, height=500)
            
            with col2:
                st.markdown("### 🔵 Loreto - Baja Densidad")
                st.markdown("**Radio de cobertura: 10 km**")
                st.markdown("Loreto tiene menor densidad de hospitales por la dispersión geográfica y poblacional.")
                
                with st.spinner('Generando mapa de Loreto...'):
                    from plots import create_proximity_map_loreto
                    
                    map_loreto = create_proximity_map_loreto(
                        st.session_state['gdf_hospitals'],
                        gdf_districts
                    )
                    
                    folium_static(map_loreto, width=550, height=500)
            
            st.divider()
            
            # Comparación de densidades
            st.subheader("📊 Comparación de Densidad")
            
            # Calcular estadísticas
            col_dept = None
            for c in st.session_state['gdf_hospitals'].columns:
                if c.strip().lower() == 'departamento':
                    col_dept = c
                    break
            
            if col_dept:
                lima_count = len(st.session_state['gdf_hospitals'][
                    st.session_state['gdf_hospitals'][col_dept] == 'LIMA'
                ])
                loreto_count = len(st.session_state['gdf_hospitals'][
                    st.session_state['gdf_hospitals'][col_dept] == 'LORETO'
                ])
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🏥 Hospitales Lima", lima_count)
                
                with col2:
                    st.metric("📍 Radio Lima", "2.5 km")
                
                with col3:
                    st.metric("🏥 Hospitales Loreto", loreto_count)
                
                with col4:
                    st.metric("📍 Radio Loreto", "10 km")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
            with st.expander("Ver error completos"):
                import traceback
                st.code(traceback.format_exc())