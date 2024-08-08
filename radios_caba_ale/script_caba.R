library(tidyverse)
library(openxlsx)
library(sf)
library(sfheaders)
# Cargar base caba
caba <- read_sf("Codgeo_CABA_con_datos/cabaxrdatos.shp") %>% 
  st_transform(4326)

# mapear
ggplot(data= caba)+
  geom_sf()

# Cargar base renabap
renabap <- read_sf("renabapgeo.geojson")

unique(renabap$Provincia)

# Filtrar barrios caba
renabap_caba <- renabap %>% 
  filter(Provincia == "Ciudad Autónoma de Buenos Aires")

ggplot()+
  geom_sf(data= caba)+
  geom_sf(data =renabap_caba, fill= "blue")

#Seleccionar columnas con datos de radio censal
caba <- caba %>% 
  select(5:8)
#Crear radio censal
  caba <- caba %>%
  mutate(radio = paste0(PROV,DEPTO,FRAC,RADIO))

# Intersectar ambos mapas
barriospop_caba <- st_intersection(renabap_caba,caba)

# Seleccionar los radios censales presentes en la intersección

radios_bp <- unique(barriospop_caba$radio)

# Filtrar la base caba por los radios censales obtenidos de la intersección
caba_nuevo <- caba %>% 
  filter(radio %in% radios_bp)

# Visualizar
ggplot()+
  geom_sf(data= caba)+
  geom_sf(data =caba_nuevo, fill= "blue")

# Guardar mapa nuevo de barrios populares de caba
drop_geom <- function(x)
{
  if(inherits(x,"sf"))
    ret <- x[,setdiff(names(x),attr(x,'sf_column')),drop=T]
  else
    ret <- x
  
  class(ret) <- 'data.frame'
  return(ret)
}

caba_nuevo2 <-drop_geom(caba_nuevo)

#st_write(caba_nuevo, "barrios_populares_caba/barrios_populares_caba.shp", crs=4326)



write.csv(caba_nuevo2, "radios_bp_caba.csv")


