1. Datos y mercado eléctrico
- Fuente: ENTSO-E Transparency Platform.
- Tipo de mercado: Day-Ahead Market (SDAC).
- Sequence 1: utilizar los precios de la subasta principal europea.
- Sequence 2: excluir los precios de la subasta EXAA para evitar mezclar mercados.
- Cambio de zona de precios (01/10/2018):
  - Antes: DE-AT-LU (Alemania, Austria y Luxemburgo).
  - Después: DE-LU (Alemania y Luxemburgo).
- Zona geográfica: mantener una serie coherente de precios alemanes durante 2016–2025.
2. Resolución temporal
- Antes del 01/10/2025: precios horarios (un precio repetido en cuatro intervalos de 15 minutos en algunos CSV).
- Desde el 01/10/2025: precios independientes cada 15 minutos.
- Modelo LP: utilizar intervalos de 15 minutos (\(\Delta t=0.25\) h), con precios horarios repetidos antes del cambio.
- Cambio estructural: considerar que el nuevo sistema permite oportunidades adicionales de arbitraje intrahorario.
- Prueba de robustez: comparar resultados de 2025 utilizando resolución horaria y cuarto-horaria.