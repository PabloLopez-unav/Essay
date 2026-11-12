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

**Daily Electricity Price Spread Analysis (2016–2025)**

Developed a Python script using Pandas and Matplotlib to analyse the evolution of German day-ahead electricity prices. For each day, the script calculates the minimum price, maximum price, and daily spread (max − min), exporting the results to a CSV file.

Two graphs are generated:
1. **Historical evolution:** daily minimum, maximum, and spread across 2016–2025.
2. **Yearly comparison:** daily spreads for each year superimposed on a common January–December timeline to identify seasonal patterns and differences between years.

Leap days (February 29) are excluded only from the yearly comparison graph to ensure consistent alignment. Figures are exported as PNG (300 dpi) and vector PDF for LaTeX.

**Methodological consideration:** The introduction of 15-minute day-ahead pricing in October 2025 may affect the observed spreads and must be considered when interpreting the results.


También he hecho gráficas con moving average para que se vea más claro y no haya tanto picos, que si no no se entiende nada.
Por 3,5 y 7 días, con y sin log, yo creo que algunas de los 18 mil gráficas es muy interesante, sobre todo para poder entender la tendencia. Me hace gracias, que se parecen mucho a espectogramas.


**LP program**

Cómo funciona
Las variables están ordenadas de esta forma:
\[
x=
\begin{bmatrix}
P_1^{ch},\ldots,P_T^{ch},
P_1^{dis},\ldots,P_T^{dis},
E_1,\ldots,E_T
\end{bmatrix}^{\mathsf T}
\]

El programa maximiza:
\[
\max \sum_{t=1}^{T}\pi_t(P_t^{dis}-P_t^{ch})\Delta t
\]

Sujeto a:
\[
\begin{aligned}
E_t&=E_{t-1}+\eta P_t^{ch}\Delta t-\frac{P_t^{dis}\Delta t}{\eta}\\
0&\leq P_t^{ch},P_t^{dis}\leq1\\
0&\leq E_t\leq2\\
E_0&=E_T=0
\end{aligned}
\]

