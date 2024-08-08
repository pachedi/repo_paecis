# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 16:50:26 2024

@author: dpach
"""
import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#from datetime import datetime
from matplotlib.ticker import MaxNLocator
#from matplotlib import cm


os.chdir("C:/Users/dpach/OneDrive - sociales.UBA.ar/Facultad/PAECIS/TIF/")

# Leer datos
caba_bp = gpd.read_file("bases_demo/radios_caba_ale/barrios_populares_caba/barrios_populares_caba.shp")
radios_caba_bp = pd.read_csv("bases_demo/radios_caba_ale/radios_bp_caba.csv")
radios_caba_todo = gpd.read_file("bases_demo/radios_caba_ale/Codgeo_CABA_con_datos/cabaxrdatos.shp")
renabap = gpd.read_file("bases_demo/radios_caba_ale/renabapgeo.geojson")

# Filtrar renabap para CABA
renaba_caba = renabap[renabap['Provincia'] == "Ciudad Autónoma de Buenos Aires"]

renaba_caba = renaba_caba.set_geometry("geometry")

renaba_caba.plot()
plt.show()

# Graficar radios_caba_todo
radios_caba_todo.plot()
plt.show()

# Crear columna 'link'
radios_caba_todo['link'] = radios_caba_todo.apply(lambda x: f"{x['PROV']}{x['DEPTO']}{x['FRAC']}{x['RADIO']}", axis=1)

# Filtrar radios populares
radios_bp = radios_caba_bp['radio'].unique()
filtro_barrios_populares_radios = radios_caba_todo[radios_caba_todo['link'].isin(radios_bp)]

radios_caba_todo = radios_caba_todo.set_geometry("geometry")

barrios_caba = gpd.read_file("bases_demo/barrios_caba/barrios_wgs84.shp")
barrios_caba = barrios_caba.set_geometry("geometry")
rivadavia = gpd.read_file("https://cdn.buenosaires.gob.ar/datosabiertos/datasets/jefatura-de-gabinete-de-ministros/calles/avenida_rivadavia.geojson")

# Graficar filtro_barrios_populares_radios y renaba_caba

fig , ax= plt.subplots(figsize=(12,4))

barrios_caba.plot(ax = ax, color='blue', alpha=0.5, edgecolor="white")

#barrios_caba.plot()
renaba_caba.plot(ax = ax, color = "red", edgecolor="none")
rivadavia.plot(ax=ax, color = "red")
ax.grid(False)
#radios_caba_todo.plot(ax=ax, color='red')
# Personalizar el gráfico
ax.set_title("Barrios populares en la CABA", fontsize=12)
plt.figtext(0.5, 0.01, "Elaboración propia en base a datos abiertos del GCBA", ha='center', fontsize=10)
plt.show()


fig, ax = plt.subplots(figsize=(12, 4))  # Utilizamos plt.subplots() correctamente

barrios_caba.plot(ax=ax, color='blue', alpha=0.5, edgecolor='none')
renaba_caba.plot(ax=ax, color='red', edgecolor='none')
ax.grid(False)

# Personalizar el gráfico
ax.set_title("Barrios populares en la CABA", fontsize=12)
plt.figtext(0.5, 0.01, "Elaboración propia en base a datos abiertos del GCBA", ha='center', fontsize=10)

plt.show()


# 
rivadavia = gpd.read_file("https://cdn.buenosaires.gob.ar/datosabiertos/datasets/jefatura-de-gabinete-de-ministros/calles/avenida_rivadavia.geojson")
barrios_vulnerables = gpd.read_file("bases_demo/bpop/barrios_vulnerables.shp")
datos_censo = gpd.read_file("bases_demo/censal/informacion_censal_por_radio_2010_wgs84.geojson")
barrios_caba = gpd.read_file("bases_demo/barrios_caba/barrios_wgs84.shp")
casos_2020 = pd.read_csv("bases_demo/casos_covid19_2020.csv")

# Filtrar casos para CABA
casos_caba_2020 = casos_2020[casos_2020['provincia'] == "CABA"]

# Convertir fecha
casos_caba_2020['fecha'] = pd.to_datetime(casos_caba_2020['fecha_clasificacion'], format='%d%b%Y')

casos_caba_2020["fecha"].head()

# Agrupar casos por fecha y barrio
casos_agrupados = casos_caba_2020.groupby(['fecha', 'barrio']).size().reset_index(name='total')

# Graficar casos por fecha
fig, ax = plt.subplots()
casos_agrupados.groupby('fecha')['total'].sum().plot(ax=ax)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.show()


# Procesar datos del censo
datos_censo = datos_censo.apply(pd.to_numeric, errors='ignore')
datos_censo['porc_nbi'] = round(datos_censo['H_CON_NBI'] / datos_censo['T_HOGAR'] * 100, 2)

# Leer comunas
comunas_caba = gpd.read_file("bases_demo/comunas/comunas_wgs84.shp")


# Convertir a GeoDataFrame
comunas_caba = gpd.GeoDataFrame(comunas_caba, geometry='geometry')


# Validar geometrías
comunas_caba_valid = comunas_caba.is_valid

comunas_caba = comunas_caba.set_crs("EPSG:4326")
comunas_caba = comunas_caba.to_crs("EPSG:4326")

radios_centroides = datos_censo.copy()
#radios_centroides = radios_centroides.to_crs("EPSG:4326")
radios_centroides = radios_centroides.set_crs("EPSG:4326")
radios_centroides.geometry = radios_centroides.geometry.centroid
#radios_centroides_valid = radios_centroides.is_valid

# Hacer válidas las geometrías no válidas
#comunas_caba = comunas_caba.buffer(0)
#radios_centroides = radios_centroides.buffer(0)


# Verificar y convertir a GeoDataFrame si es necesario
if not isinstance(comunas_caba, gpd.GeoDataFrame):
    comunas_caba = gpd.GeoDataFrame(comunas_caba)

if not isinstance(radios_centroides, gpd.GeoDataFrame):
    radios_centroides = gpd.GeoDataFrame(radios_centroides)

# Asegurarse de que ambos GeoDataFrame tengan el mismo CRS
if comunas_caba.crs != radios_centroides.crs:
    radios_centroides = radios_centroides.to_crs(comunas_caba.crs)

# Realizar la interseccion
comunas_radios_inter = gpd.overlay(comunas_caba, radios_centroides, how='intersection')

print(comunas_radios_inter)



# Leer datos de NBI
nbi_comuna = pd.read_excel("bases_demo/NBI-por-comuna.xlsx").iloc[:15]
nbi_comuna['COMUNAS'] = nbi_comuna['Comuna'].astype(int)
#nbi_comuna = nbi_comuna.rename(columns={'Comuna': 'COMUNAS'})

# Unir datos de NBI con comunas
nbi_comuna_join = comunas_caba.merge(nbi_comuna, on='COMUNAS')
nbi_comuna_join['lon'] = nbi_comuna_join.geometry.centroid.x
nbi_comuna_join['lat'] = nbi_comuna_join.geometry.centroid.y

# Graficar NBI por comuna
fig, ax = plt.subplots(figsize=(12,8))
nbi_comuna_join.plot(ax=ax, column='Hogares con NBI', legend=True)
for idx, row in nbi_comuna_join.iterrows():
    ax.text(row['lon'], row['lat'], row['COMUNAS'], fontsize=10)
ax.set_title("CABA", fontsize=14)
fig.text(0.5, 0.92, '% de hogares con NBI por Comuna', ha='center', fontsize=16)
fig.text(0.5, 0.01,  "Fuente: Elaboración propia en base a datos abiertos CABA", ha ="center",
         fontsize=10)
plt.savefig("./graficos_tablas/NBI2.png", dpi=300, bbox_inches="tight")
plt.show()



# Leer datos de hacinamiento
hacinamiento = pd.read_excel("bases_demo/hacinamiento-personas-por-cuarto-por-comuna.xlsx")
hacinamiento['COMUNAS'] = hacinamiento['COMUNAS'].astype(int)
hacinamiento_join = comunas_caba.merge(hacinamiento, on='COMUNAS')
hacinamiento_join['lon'] = hacinamiento_join.geometry.centroid.x
hacinamiento_join['lat'] = hacinamiento_join.geometry.centroid.y

hacinamiento_join.rename(columns= {"Hacinamiento crítico (más de 3 personas por cuarto)":"hacinamiento_critico"},
                         inplace=True)


# Graficar hacinamiento por comuna
fig, ax = plt.subplots(figsize=(12,8))
hacinamiento_join.plot(ax=ax, column='hacinamiento_critico', legend=True)
for idx, row in hacinamiento_join.iterrows():
    ax.text(row['lon'], row['lat'], row['COMUNAS'], fontsize=10)
fig.text(0.5, 0.92, '% de hogares con hacinamiento crítico por Comuna', ha='center', fontsize=16)
fig.text(0.5, 0.01,  "Fuente: Elaboración propia en base a datos abiertos CABA", ha ="center",
         fontsize=10)
plt.savefig("./graficos_tablas/hacinamiento.png", dpi=300, bbox_inches="tight")
plt.show()

# Leer datos de pirámides poblacionales
comuna_13 = pd.read_excel("bases_demo/piramides.xlsx", sheet_name="comuna_13")
comuna_8 = pd.read_excel("bases_demo/piramides.xlsx", sheet_name="comuna_8")


# Seleccionar filas cada 6 pasos
comuna_slice = comuna_8.iloc[::6, :]

# Calcular los totales
total_m = comuna_slice['Mujer'].sum()
total_v = comuna_slice['Varon'].sum()

# Calcular los porcentajes
comuna_slice['porc_m'] = round(comuna_slice['Mujer'] / total_m * 100, 2)
comuna_slice['porc_v'] = round(comuna_slice['Varon'] / total_v * 100, 2)

# Transformar los datos a formato largo
comuna_slice_p = comuna_slice.melt(id_vars=['Edad'], value_vars=['porc_m', 'porc_v'], 
                                   var_name='Sexo', value_name='Poblacion')

# Convertir la columna 'Edad' a string
comuna_slice_p['Edad'] = comuna_slice_p['Edad'].astype(str)

# Definir los niveles para el eje x
levels = comuna_slice_p['Edad'].unique()

comuna_slice_p = comuna_slice.melt(id_vars=['Edad'], value_vars=['porc_m', 'porc_v'], 
                                   var_name='Sexo', value_name='Poblacion')

# Convertir la columna 'Edad' a string
comuna_slice_p['Edad'] = comuna_slice_p['Edad'].astype(str)

# Invertir valores de 'porc_v' para que los varones estén a la izquierda del eje vertical
comuna_slice_p.loc[comuna_slice_p['Sexo'] == 'porc_v', 'Poblacion'] *= -1


comuna_slice["Female_Left"] = 0
comuna_slice["Female_Width"] = comuna_slice["porc_m"]

population_df = comuna_slice.copy()

population_df["Male_Left"] = -population_df["porc_v"]
population_df["Male_Width"] = population_df["porc_v"]

population_df["Varones"] = population_df["porc_v"]
population_df["Mujeres"] = population_df["porc_m"]

population_df = population_df[["Edad", "Female_Left", "Female_Width",
                               "Male_Left", "Male_Width", "Varones", "Mujeres"]]


population_df = population_df.reset_index(drop=True)

#########################
#########################
#########################
#########################


female_color = "#ee7a87"
male_color = "#4682b4"

fig = plt.figure(figsize=(15,10))

plt.barh(y=population_df["Edad"], width=population_df["Female_Width"], color="#ee7a87", label="Mujeres");
plt.barh(y=population_df["Edad"], width=population_df["Male_Width"], left=population_df["Male_Left"],
         color="#4682b4", label="Varones");

plt.text(-5, 17, "Varones", fontsize=25, fontweight="bold");
plt.text(4, 17, "Mujeres", fontsize=25, fontweight="bold");

for idx in range(len(population_df)):
    plt.text(x=population_df["Male_Left"][idx]-0.1, y=idx, s="{} %".format(population_df["Varones"][idx]),
             ha="right", va="center",
             fontsize=15, color="#4682b4");
    plt.text(x=population_df["Female_Width"][idx]+0.1, y=idx, s="{} %".format(population_df["Mujeres"][idx]),
             ha="left", va="center",
             fontsize=15, color="#ee7a87");

plt.xlim(-7,7);
plt.xticks(range(-10,9), ["{} %".format(i) for i in range(-10,9)]);

plt.legend(loc="best");

plt.xlabel("Porcentaje (%)", fontsize=16, fontweight="bold")
plt.ylabel("Rango etario", fontsize=16, fontweight="bold")
plt.title("Piramide poblacional Comuna 8", loc="left", pad=20, fontsize=25, fontweight="bold");
plt.savefig("./graficos_tablas/piramide_C8.png", dpi=300, bbox_inches="tight")

#########################
#########################
#########################
################################################## 13
#########################
#########################
#########################



# Seleccionar filas cada 6 pasos
comuna_slice = comuna_13.iloc[::6, :]

# Calcular los totales
total_m = comuna_slice['Mujer'].sum()
total_v = comuna_slice['Varon'].sum()

# Calcular los porcentajes
comuna_slice['porc_m'] = round(comuna_slice['Mujer'] / total_m * 100, 2)
comuna_slice['porc_v'] = round(comuna_slice['Varon'] / total_v * 100, 2)

# Transformar los datos a formato largo
comuna_slice_p = comuna_slice.melt(id_vars=['Edad'], value_vars=['porc_m', 'porc_v'], 
                                   var_name='Sexo', value_name='Poblacion')

# Convertir la columna 'Edad' a string
comuna_slice_p['Edad'] = comuna_slice_p['Edad'].astype(str)

# Definir los niveles para el eje x
levels = comuna_slice_p['Edad'].unique()

comuna_slice_p = comuna_slice.melt(id_vars=['Edad'], value_vars=['porc_m', 'porc_v'], 
                                   var_name='Sexo', value_name='Poblacion')

# Convertir la columna 'Edad' a string
comuna_slice_p['Edad'] = comuna_slice_p['Edad'].astype(str)

# Invertir valores de 'porc_v' para que los varones estén a la izquierda del eje vertical
comuna_slice_p.loc[comuna_slice_p['Sexo'] == 'porc_v', 'Poblacion'] *= -1


comuna_slice["Female_Left"] = 0
comuna_slice["Female_Width"] = comuna_slice["porc_m"]

population_df = comuna_slice.copy()

population_df["Male_Left"] = -population_df["porc_v"]
population_df["Male_Width"] = population_df["porc_v"]

population_df["Varones"] = population_df["porc_v"]
population_df["Mujeres"] = population_df["porc_m"]

population_df = population_df[["Edad", "Female_Left", "Female_Width",
                               "Male_Left", "Male_Width", "Varones", "Mujeres"]]


population_df = population_df.reset_index(drop=True)

#########################
#########################
#########################
#########################


female_color = "#ee7a87"
male_color = "#4682b4"

fig = plt.figure(figsize=(15,10))

plt.barh(y=population_df["Edad"], width=population_df["Female_Width"], color="#ee7a87", label="Mujeres");
plt.barh(y=population_df["Edad"], width=population_df["Male_Width"], left=population_df["Male_Left"],
         color="#4682b4", label="Varones");

plt.text(-5, 17, "Varones", fontsize=25, fontweight="bold");
plt.text(4, 17, "Mujeres", fontsize=25, fontweight="bold");

for idx in range(len(population_df)):
    plt.text(x=population_df["Male_Left"][idx]-0.1, y=idx, s="{} %".format(population_df["Varones"][idx]),
             ha="right", va="center",
             fontsize=15, color="#4682b4");
    plt.text(x=population_df["Female_Width"][idx]+0.1, y=idx, s="{} %".format(population_df["Mujeres"][idx]),
             ha="left", va="center",
             fontsize=15, color="#ee7a87");

plt.xlim(-7,7);
plt.xticks(range(-10,9), ["{} %".format(i) for i in range(-10,9)]);

plt.legend(loc="best");

plt.xlabel("Porcentaje (%)", fontsize=16, fontweight="bold")
plt.ylabel("Rango etario", fontsize=16, fontweight="bold")
plt.title("Piramide poblacional Comuna 13", loc="left", pad=20, fontsize=25, fontweight="bold");
plt.savefig("./graficos_tablas/piramide_C13.png", dpi=300, bbox_inches="tight")




#########################
#########################
#########################
##################################################
#########################
#########################
#########################


# Leer datos de contagios
contagios_2020 = pd.read_csv("bases_demo/casos_covid19_2020.csv")
contagios_2020['fecha_clasificacion_f'] = pd.to_datetime(contagios_2020['fecha_clasificacion'], format='%d%b%Y')
contagios_2020 = contagios_2020[(contagios_2020['fecha_clasificacion_f'] >= '2020-03-11') & (contagios_2020['fecha_clasificacion_f'] <= '2021-03-11')]
contagios_2020_caba = contagios_2020[contagios_2020['provincia'] == "CABA"]

######################################### Fallecidos

contagios_2020["fallecido"].unique()

fallecidos_2020 = contagios_2020.loc[contagios_2020["fallecido"] == "si"]

fallecidos_2020_813 = fallecidos_2020[fallecidos_2020["comuna"].isin([8,13])]

fallecidos_2020_813["comuna"].unique()

fallecidos_total = fallecidos_2020_813.groupby("comuna").size().reset_index(name="total")

fallecidos_total["total_pob"] =  204367
fallecidos_total["total_pob"][1] =  264385

fallecidos_total["cada_100_mil"] = round(fallecidos_total["total"] / fallecidos_total["total_pob"] *100000,2)
fallecidos_total

plt.figure(figsize=(10, 6))
sns.barplot(data=fallecidos_total,
             x='comuna', y='cada_100_mil', hue="comuna" , dodge=False,palette={8: 'red', 13: 'blue'})
plt.xticks()
plt.xlabel("Comunas")
plt.ylabel("Cantidad de fallecidos por comuna")
plt.title("Cantidad de fallecidos cada 100mil/hab en comunas 8 y 13")
plt.legend(title="Comunas:")
plt.grid(False)
plt.tight_layout()
plt.show()

fallecidos_total.to_excel("./graficos_tablas/fallecidos_100.xlsx", index=False)

# 172
# 201

#########################################
# Agrupar contagios por día
por_dia = contagios_2020[contagios_2020['clasificacion'] == 'confirmado'].groupby('fecha_clasificacion_f').size().reset_index(name='total')


por_dia_comuna = (contagios_2020
                  .query('clasificacion == "confirmado" and fecha_clasificacion_f <= "2020-11-29"')
                  .groupby(['fecha_clasificacion_f', 'comuna'])
                  .size()
                  .reset_index(name='total')
                  .assign(comuna=lambda x: x['comuna'].astype(str)))

por_dia_2020 = por_dia_comuna.query('fecha_clasificacion_f <= "2020-11-29"')
                                                                               

por_dia_2020["comuna"] = por_dia_2020["comuna"].astype(str)


# Convertir fecha a datetime
por_dia_2020['fecha_clasificacion_f'] = pd.to_datetime(por_dia_2020['fecha_clasificacion_f'])
por_dia_comuna['fecha_clasificacion_f'] = pd.to_datetime(por_dia_comuna['fecha_clasificacion_f'])


por_dia_comuna["comuna"] = por_dia_comuna["comuna"].astype(str)

por_dia_comuna["comuna"].dtype


por_dia_comuna["comuna"][0]

comunas_elegidas = por_dia_comuna[por_dia_comuna["comuna"].isin(["8.0","13.0"])] 

comuna_8_filtro = comunas_elegidas.loc[comunas_elegidas["comuna"] == "8.0"]

comuna_8_filtro["cada_100_mil"] = round(comuna_8_filtro["total"] / 204367 *100000,4)

comuna_13_filtro = comunas_elegidas.loc[comunas_elegidas["comuna"] == "13.0"]

comuna_13_filtro["cada_100_mil"] = round(comuna_13_filtro["total"] / 264385 *100000,4)

comunas_100 = pd.concat([comuna_8_filtro, comuna_13_filtro], ignore_index =True)

# contagios cada 100

plt.figure(figsize=(10, 6))
sns.lineplot(data=comunas_100,
             x='fecha_clasificacion_f', y='cada_100_mil', hue="comuna" ,palette={"8.0": 'red', "13.0": 'blue'})
plt.xticks(rotation=45)
plt.xlabel("Fecha")
plt.ylabel("Cantidad de contagios cada 100 mil habitantes")
plt.title("Cantidad de contagios por día")
plt.legend(title="Comunas:")
plt.grid(True)
plt.show()


# Graficar 
plt.figure(figsize=(10, 6))
sns.lineplot(data=comunas_elegidas,
             x='fecha_clasificacion_f', y='total', hue="comuna" ,palette={"8.0": 'red', "13.0": 'blue'})
plt.xticks(rotation=45)
plt.xlabel("Fecha")
plt.ylabel("Cantidad de contagios")
plt.title("Cantidad de contagios por día")
plt.legend(title="Comunas:")
plt.grid(True)
plt.show()
                  

# Graficar comunas 8 y 13
por_tipo_comuna = (contagios_2020_caba
                   .query('clasificacion == "confirmado" and comuna in [8.0, 13.0]')
                   .groupby(['comuna', 'tipo_contagio'])
                   .size()
                   .reset_index(name='total')
                   .query('tipo_contagio != ""'))
                                                                                     

                                                                                     
# contagios 2020

# Convertir la columna de fechas a datetime si aún no lo está
contagios_2020_caba['fecha_clasificacion_f'] = pd.to_datetime(contagios_2020_caba['fecha_clasificacion_f'])

# Filtrar y agrupar por fecha <= 2020-05-16
por_tipo_comuna_fechas = (contagios_2020_caba
                          .query('clasificacion == "confirmado" and comuna in [8.0, 13.0] and fecha_clasificacion_f <= "2020-05-16"')
                          .groupby(['comuna', 'tipo_contagio'])
                          .size()
                          .reset_index(name='total')
                          .query('tipo_contagio != ""'))

# Filtrar y agrupar por fechas entre 2020-05-16 y 2020-08-01
por_tipo_comuna_fechas_2 = (contagios_2020_caba
                           .query('clasificacion == "confirmado" and comuna in [8.0, 13.0] and fecha_clasificacion_f >= "2020-05-16" and fecha_clasificacion_f <= "2020-08-01"')
                           .groupby(['comuna', 'tipo_contagio'])
                           .size()
                           .reset_index(name='total')
                           .query('tipo_contagio != ""'))

por_tipo_comuna_fechas_3 = (contagios_2020_caba
                           .query('clasificacion == "confirmado" and comuna in [8.0, 13.0] and fecha_clasificacion_f >= "2020-12-01" and fecha_clasificacion_f <= "2021-01-01"')
                           .groupby(['comuna', 'tipo_contagio'])
                           .size()
                           .reset_index(name='total')
                           .query('tipo_contagio != ""'))       

                                                                              
# Guardar en Excel
por_tipo_comuna_fechas_2.to_excel("bases_demo/contagios_tipo_comuna_segmento2.xlsx", index=False)
por_tipo_comuna_fechas.to_excel("bases_demo/contagios_tipo_comuna_segmento1.xlsx", index=False)
por_tipo_comuna_fechas_3.to_excel("bases_demo/contagios_tipo_comuna_segmento3.xlsx", index=False)


########################



# Calcular total_c13_3 y total_c8_3
total_c13_3 = por_tipo_comuna_fechas_3[por_tipo_comuna_fechas_3['comuna'] == 13.0]['total'].sum()
total_c8_3 = por_tipo_comuna_fechas_3[por_tipo_comuna_fechas_3['comuna'] == 8.0]['total'].sum()

# Calcular proporción
por_tipo_comuna_fechas_3['proporcion'] = round(por_tipo_comuna_fechas_3['total'] / total_c8_3 * 100, 2)

# Actualizar proporción para las filas 6 a 10
por_tipo_comuna_fechas_3.loc[5:10, 'proporcion'] = round(por_tipo_comuna_fechas_3.loc[5:9, 'total'] / total_c13_3 * 100, 2)

# Filtrar para comuna 8 y comuna 13
tipo_comuna_8 = por_tipo_comuna[por_tipo_comuna['comuna'] == 8.0].copy()
tipo_comuna_8['porcentaje'] = round(tipo_comuna_8['total'] / tipo_comuna_8['total'].sum() * 100, 2)

tipo_comuna_13 = por_tipo_comuna[por_tipo_comuna['comuna'] == 13.0].copy()
tipo_comuna_13['porcentaje'] = round(tipo_comuna_13['total'] / tipo_comuna_13['total'].sum() * 100, 2)

# Combinar los dos DataFrames
tipo_comuna_13_8 = pd.concat([tipo_comuna_13, tipo_comuna_8])

# Escribir en archivo Excel
tipo_comuna_13_8.to_excel("bases_demo/tipo_contagio_8_13.xlsx", index=False)


###################### servicios



servicios = pd.read_csv("bases_demo/calidad-conexion-servicios-basicos-por-comuna (1).csv", sep=";")
servicios = servicios.drop(15)  # Eliminar la fila 16 (índice 15)
servicios['comuna'] = pd.to_numeric(servicios['comuna'])


servicios_comuna_join = comunas_caba.merge(servicios, left_on="COMUNAS", right_on="comuna", how="left")


servicios_comuna_join = comunas_caba.merge(servicios, left_on="COMUNAS", 
                                           right_on="comuna", how = "left")


servicios_comuna_join['lon'] = servicios_comuna_join.geometry.centroid.x
servicios_comuna_join['lat'] = servicios_comuna_join.geometry.centroid.y



fig, ax = plt.subplots(figsize=(10, 10))

# Geopandas para plotear datos de la comuna
servicios_comuna_join.plot(column='Calidad Insuficiente', ax=ax, legend=True,
                           cmap='viridis', edgecolor='k', linewidth=0.2)

# Añadir geometría adicional (supongamos que rivadavia es otro GeoDataFrame)
rivadavia.plot(ax=ax, color='red', edgecolor='k')

# Añadir etiquetas
for idx, row in servicios_comuna_join.iterrows():
    ax.text(row['lon'], row['lat'], row['COMUNAS'], fontsize=10, ha='right')

# Personalizar el gráfico
ax.set_title("Porcentaje de hogares con calidad de servicios \ninsuficiente", fontsize=16)
ax.set_xlabel("Longitud")
ax.set_ylabel("Latitud")
ax.grid(False)
plt.tight_layout()
plt.figtext(0.5, 0.01, "Elaboración propia en base a datos abiertos del GCBA", ha='center', fontsize=10)

plt.show()


################################################




# Configuración de la paleta de colores
cmap_viridis = plt.get_cmap('viridis')


# Configuración de la paleta de colores
cmap_viridis = plt.get_cmap('viridis')

# Función para crear los gráficos
def create_plot(data, fill_column, title, subtitle, color_map, breaks):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    data.plot(column=fill_column, cmap=color_map, ax=ax, legend=True,
              legend_kwds={'label': "", 'orientation': "horizontal", 'ticks': breaks})
    rivadavia.plot(ax=ax, edgecolor='red', linewidth=1)
    for x, y, label in zip(data.geometry.centroid.x, data.geometry.centroid.y, data['COMUNAS']):
        ax.text(x, y, label, fontsize=9, ha='center', color='black')
    ax.set_title(title, fontsize=15)
    ax.text(0.5, 0.95, subtitle, horizontalalignment='center', verticalalignment='top', 
            transform=ax.transAxes, fontsize=12, style='italic')
    ax.text(0.5, -0.05, 'Elaboración propia en base a datos abiertos del GCBA', 
            horizontalalignment='center', verticalalignment='center', 
            transform=ax.transAxes, fontsize=10)
    ax.set_axis_off()
    #ctx.add_basemap(ax, crs=data.crs.to_string())
    return fig

# Crear los gráficos



plt.subplot(1,3,1)
plot1 = create_plot(nbi_comuna_join, 'Hogares con NBI', 
                    'Porcentaje de hogares con NBI', 'CABA', cmap_viridis, list(range(0, 19, 2)))
plt.subplot(1,3,2)
plot2 = create_plot(hacinamiento_join, 'hacinamiento_critico', 
                    'Porcentaje de hacinamiento crítico', 'CABA', 
                    cmap_viridis, list(range(0, 6, 1)))
plt.subplot(1,3,3)
plot3 = create_plot(servicios_comuna_join, 'Calidad Insuficiente', 
                    'Porcentaje de hogares con calidad de servicios insuficiente', 
                    'CABA', cmap_viridis, list(range(5, 11, 1)))

#########################################################################################3

nbi_comuna_join["COMUNAS"] = nbi_comuna_join["COMUNAS"].astype(int)

servicios_comuna_join["COMUNAS"] = servicios_comuna_join["COMUNAS"].astype(int)

hacinamiento_join["COMUNAS"] = hacinamiento_join["COMUNAS"].astype(int)


##########################################################################################

##########################


fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True, figsize= (18,6))

servicios_comuna_join.plot(column='Calidad Insuficiente', ax=ax1, legend=True,
                           cmap='viridis', edgecolor='k', linewidth=0.2)

# Añadir geometría adicional (supongamos que rivadavia es otro GeoDataFrame)
rivadavia.plot(ax=ax, color='red', edgecolor='k')

# Añadir etiquetas
for idx, row in servicios_comuna_join.iterrows():
    ax1.text(row['lon'], row['lat'], row['COMUNAS'], fontsize=10, ha='right',fontweight='bold',color='white')

#  gráfico
ax1.set_title("Porcentaje de hogares con calidad \nde servicios \ninsuficiente", fontsize=12)
ax1.set_xlabel("Longitud")
ax1.set_ylabel("Latitud")
ax1.grid(False)
plt.tight_layout()
plt.figtext(0.5, 0.01, "Elaboración propia en base a datos abiertos del GCBA", ha='center', fontsize=10)


################################


nbi_comuna_join.plot(ax=ax2, column='Hogares con NBI', legend=True, cmap='viridis', edgecolor='k', linewidth=0.2)
for idx, row in nbi_comuna_join.iterrows():
    ax2.text(row['lon'], row['lat'], row['COMUNAS'], fontsize=10, fontweight='bold',color='white')
ax2.set_title('% de hogares \ncon NBI por Comuna', ha='center', fontsize=12)
ax2.grid(False)
#fig.text(0.5, 0.92, '% de hogares con NBI por Comuna', ha='center', fontsize=16)



##############################

hacinamiento_join.plot(ax=ax3, column='hacinamiento_critico', legend=True, cmap='viridis', edgecolor='k', linewidth=0.2)
for idx, row in hacinamiento_join.iterrows():
    ax3.text(row['lon'], row['lat'], row['COMUNAS'], fontsize=10,fontweight='bold',color='white')
ax3.set_title( '% de hogares con hacinamiento \ncrítico por Comuna', ha='center', fontsize=12)

ax3.grid(False)
plt.tight_layout()
plt.savefig("./graficos_tablas/tresjuntos.png", dpi=300, bbox_inches="tight")
plt.show()















                                                                       

                                                                                     

                                                                                     

                                                                                     
