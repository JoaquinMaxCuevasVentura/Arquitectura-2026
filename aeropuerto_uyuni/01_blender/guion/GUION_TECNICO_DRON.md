# Aeropuerto de Uyuni · Guion técnico de video dron

Borrador de dirección · 4 de octubre de 2026. **120 s / 24 fps / 2880 cuadros / 3840 × 2160.**

Producción retomada el 5 de octubre: revisión por tomas antes del render final. Las trayectorias se comprueban contra el volumen principal; falta completar acciones de personas y vehículos y revisar sus colisiones.

## Intención y montaje

La secuencia pasa del paisaje a la llegada, de la llegada a los detalles de la envolvente y de esos detalles al conjunto y al logotipo. Ritmo sereno, sin giros bruscos, transiciones llamativas ni ópticas que deformen la arquitectura. Las tomas se montan por cortes; no forman un único vuelo continuo.

La toma inicial del Salar se produce en una escena independiente o con footage comercialmente autorizado. Se enlaza con el aeropuerto por corte o disolución. La foto del HTML es referencia de atmósfera, no evidencia de un recorrido real entre ambos lugares.

La fachada Lado Tierra mira al NNE (31°). La mañana sirve para mostrar incidencia y sombras. El atardecer se reserva para el testero, luz rasante o contraluz; verificar la posición solar antes del render. El montaje hace explícito el cambio de estado de luz.

## Coordenadas y cámara

X longitudinal, +Y hacia Lado Aire, Z vertical en metros desde NPT. Puntos de cámara y objetivo propuestos, sujetos a ajuste por encuadre y colisiones. Referencia aproximada del volumen principal: X 0–82,51; Y 0–48,32; cumbrera del modelo actual ≈ +13,024. El guion no resuelve la discrepancia de cotas del DXF ni autoriza modificar la cubierta.

Sensor horizontal de 36 mm, lentes constantes por plano, sin zoom digital. Cámara mira con -Z y usa Y local hacia arriba; conservar horizonte horizontal. DOF mediante Empty de foco animado en el elemento, f/8 general, f/5,6 aproximación y f/4 detalle. En tomas generales se puede desactivar DOF para evitar ruido innecesario.

Motion blur de 180° a 24 fps: **0,5 cuadros, equivalente a 1/48 s**. Iniciar la prueba a 0,5; reducir a 0,35 solo si el calado pierde lectura. No sustituir geometría de celosía ni letras por desenfoque.

## Plano a plano

### 01 · Salar · 00:00–00:12

**Duración:** 12 s. **Cuadros de programa:** 1–288 (inclusivos).

**Imagen y acción:** Aéreo lento sobre una escena de contexto independiente o footage con licencia. El horizonte ocupa el tercio superior. La foto es referencia de atmósfera, no un fotograma de dron.

**Luz:** AMANECER_SALAR.

**Transición:** Corte o disolución de 12 cuadros al aeropuerto; no simular continuidad geográfica.

**Locución sugerida:** En Uyuni, el horizonte y su reflejo construyen una imagen del lugar.

**Cámara:** 24 mm / f/8; DOF desactivable en toma general.

**Posición:** `(-20, -100, 20)` → `(-12, -70, 18)`.

**Objetivo:** `(0, 30, 1)` → `(0, 50, 1)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 31.1 m; velocidad media 2.59 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 02 · Aproximación · 00:12–00:26

**Duración:** 14 s. **Cuadros de programa:** 289–624 (inclusivos).

**Imagen y acción:** Aproximación oblicua al Lado Tierra. Mantener el edificio completo antes de bajar. Una 4x4 avanza hacia la zona de descenso, sin ocultar el ingreso.

**Luz:** MANANA_NNE.

**Transición:** Corte por dirección de movimiento al plano 03.

**Locución sugerida:** La propuesta ordena la llegada y concentra la inversión en la envolvente.

**Cámara:** 28 mm / f/8; DOF desactivable en toma general.

**Posición:** `(-40, -90, 40)` → `(-10, -43, 18)`.

**Objetivo:** `(34, 12, 5)` → `(36, 5, 5)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 59.9 m; velocidad media 4.28 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 03 · Llegada · 00:26–00:40

**Duración:** 14 s. **Cuadros de programa:** 625–960 (inclusivos).

**Imagen y acción:** Dolly oblicuo de fachada. Una pareja con equipaje camina hacia el acceso principal, fuera del eje óptico del rótulo. Mostrar mamparas y continuidad del alero.

**Luz:** MANANA_NNE.

**Transición:** Corte a detalle de materia.

**Locución sugerida:** El alero protege el acceso. Las mamparas y el fondo continuo hacen legible la fachada.

**Cámara:** 28 mm / f/5.6; DOF en el objetivo.

**Posición:** `(95, -28, 4.5)` → `(91, -23, 3.2)`.

**Objetivo:** `(38, 0, 4.4)` → `(42, 0, 4.4)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 6.5 m; velocidad media 0.47 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 04 · Alero y celosía · 00:40–00:52

**Duración:** 12 s. **Cuadros de programa:** 961–1248 (inclusivos).

**Imagen y acción:** Vuelo lateral a nivel del cielo del alero. La mañana permite leer las sombras sobre la fachada NNE. Mantener la cámara fuera del alero y del plano de la celosía. Vehículos secundarios al fondo.

**Luz:** MANANA_NNE.

**Transición:** Corte por textura a un detalle con otro estado de luz.

**Locución sugerida:** La celosía aporta profundidad, tamiza la luz y proyecta una geometría reconocible.

**Cámara:** 35 mm / f/5.6; DOF en el objetivo.

**Posición:** `(62, -8, 6.7)` → `(76, -6.5, 6.7)`.

**Objetivo:** `(73, -0.5, 4.7)` → `(81, -0.5, 4.7)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 14.1 m; velocidad media 1.17 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 05 · Luz en el Corten · 00:52–01:04

**Duración:** 12 s. **Cuadros de programa:** 1249–1536 (inclusivos).

**Imagen y acción:** Detalle de celosía del testero Este con luz rasante o contraluz. Verificar sol y orientación en previs. La imagen del rótulo es una referencia de material, no el encuadre final. Puede sustituirse por un detalle de rótulo en contraluz si la celosía no recibe sol.

**Luz:** ATARDECER_LATERAL.

**Transición:** Corte por línea del metal a cubierta; cambio explícito a mañana.

**Locución sugerida:** Los montículos facetados y la copia espejada trasladan al metal la idea del Salar como espejo.

**Cámara:** 50 mm / f/4; DOF en el objetivo.

**Posición:** `(89, 7, 4.2)` → `(89, 11, 4.4)`.

**Objetivo:** `(82.5, 4, 3.4)` → `(82.5, 8, 3.4)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 4.0 m; velocidad media 0.33 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 06 · Cubierta y nieve · 01:04–01:18

**Duración:** 14 s. **Cuadros de programa:** 1537–1872 (inclusivos).

**Imagen y acción:** Ascenso fuera del testero Este. Plano próximo de juntas engrapadas y doble barra de retención. La posición del foco del retenedor deberá sustituirse por la del objeto validado. No tocar geometría para conseguir el encuadre.

**Luz:** MANANA_NNE.

**Transición:** Corte al lado operativo desde altura compatible.

**Locución sugerida:** La revisión incorpora retención de nieve y un recorrido de drenaje que debe verificarse con cálculo.

**Cámara:** 35 mm / f/8; DOF desactivable en toma general.

**Posición:** `(90, -10, 14)` → `(95, 15, 19)`.

**Objetivo:** `(78, 2, 9.4)` → `(74, 10, 10.5)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 26.0 m; velocidad media 1.86 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 07 · Lado Aire · 01:18–01:32

**Duración:** 14 s. **Cuadros de programa:** 1873–2208 (inclusivos).

**Imagen y acción:** Recorrido fuera del perímetro construido. Mostrar la fachada Lado Aire y las dos mangas. Si se incorporan aeronaves, una aeronave estática, sin movimiento de turbinas ni maniobra simulada. La implantación actual es preliminar.

**Luz:** MANANA_NNE.

**Transición:** Corte a nueva posición aérea; evitar un retorno rápido en vuelo continuo.

**Locución sugerida:** Hacia el Lado Aire, el conjunto se integra con los accesos y la plataforma.

**Cámara:** 24 mm / f/8; DOF desactivable en toma general.

**Posición:** `(115, 46, 34)` → `(86, 128, 43)`.

**Objetivo:** `(42, 62, 5)` → `(42, 65, 4)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 87.4 m; velocidad media 6.25 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 08 · Elevación del conjunto · 01:32–01:46

**Duración:** 14 s. **Cuadros de programa:** 2209–2544 (inclusivos).

**Imagen y acción:** Nueva posición exterior por montaje. Deriva horizontal y descenso moderado; cubierta visible sin entrar en ella. Mantener la cámara por encima de la cumbrera con margen. La calle y los turistas dan escala.

**Luz:** MANANA_NNE.

**Transición:** Corte por composición al rótulo centrado.

**Locución sugerida:** Una arquitectura sobria: protección climática y un acceso principal reconocible.

**Cámara:** 28 mm / f/8; DOF desactivable en toma general.

**Posición:** `(20, -75, 48)` → `(55, -65, 35)`.

**Objetivo:** `(40, 13, 6)` → `(52, 5, 7)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 38.7 m; velocidad media 2.76 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 09 · Ingreso UYUNI · 01:46–01:54

**Duración:** 8 s. **Cuadros de programa:** 2545–2736 (inclusivos).

**Imagen y acción:** Push de 2 m hacia el logotipo existente en hora azul, aprobado por el cliente el 5 de octubre. Conservar el nombre completo y su grafismo invertido. Heredar el neón atenuado de 4000 K, emisión 2,5, y la luz interior cálida de 3500 K de la escena nocturna corregida. Ajustar distancia por encuadre, sin cambiar proporciones del rótulo.

**Luz:** HORA_AZUL, con el mismo cielo, exposición, luces de alero y celosías de la escena nocturna validada. El cambio de luz se realiza por corte desde la toma 08.

**Transición:** Match cut del horizonte a las capas del cierre gráfico.

**Locución sugerida:** Aeropuerto de Uyuni.

**Cámara:** 50 mm / f/5.6; DOF en el objetivo.

**Posición:** `(55.64, -18, 8.25)` → `(55.64, -16, 8.25)`.

**Objetivo:** `(55.64, -1.85, 8.1)` → `(55.64, -1.85, 8.1)`.

**Movimiento:** smootherstep por plano. Recorrido recto inicial 2.0 m; velocidad media 0.25 m/s. La curva llega a una velocidad máxima de 1,875 veces la media en el tramo recto. Ajustar el recorrido si invade geometría; volver a comprobar velocidades si se curva.

### 10 · Cierre de identidad · 01:54–02:00

**Duración:** 6 s. **Cuadros de programa:** 2737–2880 (inclusivos).

**Imagen y acción:** Cierre gráfico de 6 segundos con las capas del logotipo desarrollado. Fondo limpio, proporciones originales, entrada discreta y permanencia final de 1,3 s. La prueba HTML es un animatic con proyección vectorial del rótulo guardado.

**Luz:** GRAPHIC_FLAT.

**Transición:** Final exacto en 02:00. La salida de música ocurre dentro de la permanencia, sin agregar cola.

**Locución sugerida:** Sin locución. Dejar respirar el logotipo.

## Curvas de animación

Para cada plano, `t=(f-f_inicio)/(f_fin-f_inicio)`, limitado a 0–1. Usar `s=6t^5-15t^4+10t^3`. Para un tramo recto: `P=(1-s)*P0+s*P1`. Aplicar la misma curva al objetivo y orientar la cámara por Track To. La primera y segunda derivadas se anulan en los extremos: Ease In / Ease Out suave.

Muestrear cada cuadro y dejar interpolación LINEAR en esas muestras. Una curva BEZIER automática sobre pocos keyframes puede sobrepasar el alero o introducir cambios de velocidad. Para órbitas, definir una curva 3D sin auto-intersecciones, parametrizar por longitud de arco y aplicar el mismo easing a la distancia recorrida.

Los planos se cortan: no interpolar desde la última posición de un plano a la primera del siguiente. Crear una cámara por plano y usar marcadores de cámara o escenas independientes. Si hay disolución, producir handles y hacer el solapado dentro de la duración de programa.

## Cierre motion graphics · 01:54–02:00

Reutilizar el logotipo desarrollado: línea del horizonte, montículos 3D facetados, letras UYUNI y copia espejada. Conservar proporciones, espaciamiento y asimetría. No reemplazarlo por una fuente de sistema ni un reflejo generado de manera genérica.

| Tiempo | Cuadros de programa aprox. | Capa | Movimiento |
|---|---|---|---|
| 01:54–01:55 | 2737–2760 | Horizonte | Trazo de izquierda a derecha; ease-out suave. |
| 01:55–01:56,3 | 2761–2791 | Montículos facetados | Aparición escalonada 0,08 s entre caras; desplazamiento vertical máximo 6 px en 4K. |
| 01:56,3–01:57,5 | 2792–2820 | Nombre | Revelado de máscara con entrada de opacidad; evitar giro o extrusión nueva. |
| 01:57,5–01:58,7 | 2821–2849 | Copia espejada | Revelado bajo el horizonte; mantener la geometría anamórfica existente. |
| 01:58,7–02:00 | 2850–2880 | Conjunto | Permanencia final de 1,3 s; música sale dentro del plano. |

Los límites de fases con decimales se redondean al cuadro más próximo. Exportar el arte por capas con fondo transparente (PNG 4K o SVG exacto desde el arte original). Componer sobre un fondo salar claro o grafito según el acabado elegido. La previsualización HTML usa una proyección vectorial de la geometría guardada del rótulo y permite revisar ritmo; el arte completo se incluye como SVG por capas.

## Sonido y locución

0–12 s: ambiente de viento suave, sin saturar graves. A partir del acercamiento, música instrumental discreta de 72–80 BPM, con licencia comercial. Mantener continuidad sonora al cambiar de luz; sonido de neumáticos y pasos solo en planos de llegada. Evitar convertir turistas y operación en espectáculo. La locución sugerida es opcional; debe dejar silencios en los detalles y antes del cierre.

El cierre no agrega seis segundos después de los dos minutos: ocupa 01:54–02:00. Una cortinilla o silencio adicional debe sustituir tiempo de programa, no extenderlo.

## Producción y entrega

1. Crear una copia de trabajo del .blend validado y una escena/colección específica para el video.
2. Completar Lado Aire, resolver retenedor y sustituir proxies con assets autorizados antes de aprobación de encuadres.
3. Pasada de cámara en viewport a 1280 × 720 sin DOF ni motion blur; verificar colisiones y legibilidad del rótulo.
4. Pruebas de inicio/medio/final de cada plano; aprobar orientación solar y continuidad de vehículos.
5. Render por secuencia de imágenes, color gestionado de forma consistente y sin clamping que altere luz entre planos.
6. Ensamblar el corte de 2880 cuadros, sonido y gráfico. Exportar master 4K y copia de revisión 1080p.
7. Entregar créditos de fotografía, footage, modelos, texturas y música junto al video.

## Fuentes y límites del argumento

- Documentos de proyecto: DXF, auditoría, acuerdos del cliente y renders del 4 de octubre.
- Alcantarí: [Correo del Sur, 06.12.2016](https://correodelsur.com/local/20161206/goteras-de-alcantari-se-vuelven-chorreras.html) y [28.06.2017](https://correodelsur.com/local/20170628/cambiaran-tres-cubiertas-en-bloques-de-alcantari.html): daños y filtraciones por granizo; no se presenta como colapso por nieve.
- Retención: [guía de cálculo y fijaciones de S-5!](https://blog.s-5.com/blog/how-do-you-design-a-reliable-snow-guard-system-for-your-metal-roof). Requiere carga local, geometría y resistencia de anclajes; no acredita un sistema de Uyuni.
- Foto de referencia: [Diego Delso, delso.photo / Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Salar_de_Uyuni,_Bolivia,_2016-02-04,_DD_10-12_HDR.JPG), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); resolución reducida y recorte de composición.
- Costos y acústica: el borrador no inventa montos, porcentaje de ahorro, Rw, STC ni prestaciones sin ensayo.
