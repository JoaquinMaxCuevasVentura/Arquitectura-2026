# Taxonomía visual de «Una arquitectura que se arma y se guarda»

32 imágenes de dominio público, ordenadas por lo que muestran (un material) y por lo que se hace con ese material (un gesto), y montadas en tres tableros. 26 de octubre de 2026. Siguen el sistema gráfico de los tableros de «Cosecha de piedras» (repositorio `Altiplano`) y las tres referencias que mandó el autor: el «Tree Diagram» de Kengo Kuma, el mapa de las vanguardias y «The Narrative – Doing a Duchamp».

## Qué hay

| Archivo | Qué es |
|---|---|
| `tablero_1_arbol.jpg` y `.pdf` | **El árbol.** 31 imágenes. Seis materiales arriba y siete gestos abajo, **en el orden del ciclo diario**: cargar, desplegar, armar, cubrir, apilar, ofrecer y guardar. Cada imagen está en la columna de su gesto; una línea del color de su material la ata a él. Sigue el «Tree Diagram» de Kuma |
| `tablero_2_fechas.jpg` y `.pdf` | **El mapa de fechas.** Las 32 imágenes por año, en una franja por categoría del Cuadro 1 del borrador (apoyo, cubierta, masa, boca, borde y guardado). Una línea discontinua une las imágenes de una misma obra. Escala partida: 1850-1920 se abre. Sigue el mapa de las vanguardias |
| `tablero_3_relato.jpg` y `.pdf` | **El relato.** El argumento del borrador como un collage. Un hilo rojo recorre siete pasos en el orden de sus secciones, del puesto a medias (2026) a la intervención. Un hilo azul ata cada una de las cinco hipótesis de `analisis/02` a los pasos que la ponen a prueba. Aparte va lo que el archivo casi no muestra. Sigue «Doing a Duchamp» |
| `catalogo.json` | La fuente de datos: la ficha de cada imagen, los materiales, los gestos, las categorías y el relato. Se edita a mano |
| `catalogo.md` | La misma ficha en una tabla legible. La escribe el generador: no se edita |
| `imagenes/` | Las 32 imágenes, reducidas a 900 px de lado como máximo |
| `generar_tableros.py` | Rehace los tableros y `catalogo.md`: `python3 "Una arquitectura que se arma y se guarda/taxonomia/generar_tableros.py"` (Pillow y Chromium) |

## Cómo se clasifica

- **El material** es lo que la imagen muestra trabajado: **tela** (aguayo, toldo, paraguas, nailon), **armazón** (palo, caballete, cajón, carro, andamio), **fibra** (canasta, costal, cuerda), **mercancía**, **ciudad** (muro, portal, plaza, vereda, depósito) y **cuerpo**. La ciudad cuenta como material porque el puesto la usa como apoyo prestado (hipótesis H4).
- **El gesto** es un verbo del vocabulario de `campo/protocolo.md`. Los siete van en el orden en que ocurren en un día: de la mañana a la noche.
- **La categoría** es la del Cuadro 1 del borrador. El tablero 2 la usa para ver si las seis categorías alcanzan (hipótesis H2).
- **Una casilla por imagen.** Muchas caben en dos; elegir obliga a decir qué se ve primero. Si una clasificación no convence, se cambia en `catalogo.json` y se regenera.
- **La regla de la analogía.** Las imágenes no ilustran los puestos de La Paz: son analogías. Se adopta la condición de Fuão para juntar figuras lejanas: «con la condición de que haya una referencia explícita» (Fuão, 2011: 53).
  - **Con referencia (9).** Llevan una cita comprobada hoy en su fuente: Marcoy (1875), Wright (1907), Wiener (1880), Semper (1863), Gilbreth (1911), o un vínculo con el borrador: la tesis provisional o una cita ya cotejada (Frampton, Cárcamo Pino).
  - **Sin referencia (23).** Todavía no la tienen: son candidatas.

## Lo que muestran los tableros

Son observaciones sobre esta selección, no sobre la historia de los mercados. Cada una termina en algo que el campo puede responder.

1. **El archivo ve el puesto armado, no el gesto de guardarlo.**
   - «Cargar» es la columna más llena (6) y «guardar», la más pobre (3). Ninguna de las tres de «guardar» muestra a alguien guardando: un depósito inca, puertas cerradas, una calle vacía.
   - Viajeros y fotógrafos llegaban a la hora de la venta. **El desmontaje es el dato que solo el trabajo de campo puede dar.**
2. **La misma tela carga, cubre y se despliega.**
   - La tela aparece en tres gestos: carga la cosecha y a la criatura (n.os 1 y 6), cubre la plaza (16, 17, 19) y es la mercancía misma (10).
   - Pregunta de campo: **¿la tela que trae la mercancía por la mañana es la misma que se tiende como puesto?**
3. **El puesto mínimo tiene una descripción de 1875.**
   - Marcoy describe en la plaza del Cuzco un puesto que es «a simple cloth spread on the ground, and held down by four stones» (Marcoy, 1875, I: 260).
   - En 2026, en El Alto, otro puesto «se redujo a un nailon de color azul tendido en el suelo» (La Prensa, 2026).
   - Entre las dos, Wright (1907: 148) ve en La Paz a los vendedores sentados al borde de la acera con la mercancía «spread in front of them on the ground». El gesto de desplegar atraviesa siglo y medio. Es una continuidad visible, **no una prueba de que la secuencia sea antigua**: para eso harían falta otras fuentes (`analisis/02`, «Lo que no se va a afirmar»).
4. **La secuencia prescrita frente a la aprendida.**
   - La única secuencia escrita del conjunto es la de Gilbreth (n.os 14 y 23): un andamio que pone el ladrillo a la altura de la mano y numera «the correct sequence [...] for the fewest, shortest, and most economical motions» (Gilbreth, 1911: 12).
   - Todas las demás secuencias se aprendieron sin escribirse. Es el contraste de H1 y la advertencia de la sección 7 del borrador: intervenir el soporte, no el gesto.
5. **La Paz casi no está en el archivo de dominio público.**
   - De 32 imágenes, solo dos son de La Paz: la chichera de Wiener (26) y la calle del Comercio de Wright (31). Hay otras cinco de Bolivia, todas de Wright (Potosí, Sucre, Cochabamba y la del bebé), y la Chuquiyabo de Guaman Poma (32) es la ciudad, no el mercado.
   - Las fotos del campo, con consentimiento, serán la fuente principal. Un archivo para consultar: el fotográfico de Julio Cordero, en La Paz [por verificar: acceso y derechos].
6. **La mirada es la del viajero.**
   - Marcoy, Squier, Wiener y Wright retratan «tipos», no personas, y a veces con desprecio: en la misma página del puesto de la tela y las cuatro piedras, Marcoy llama a esos comerciantes «revoltingly filthy» (1875, I: 260).
   - Si alguna de estas imágenes entra al artículo, tiene que entrar con esa crítica, como en *Altiplano* entró Squier: el viajero vuelve paisaje a quien trabaja.
7. **El mapa tiene un hueco entre 1920 y 1973, y otro hasta 2026.** Es efecto de los derechos de autor, no de la historia.

## Fuentes y derechos

| Fuente | Imágenes | Derechos |
|---|---|---|
| Det Kgl. Bibliotek, Copenhague: Guaman Poma, *Nueva corónica y buen gobierno*, 1615 (GKS 2232 4º) | 1, 29, 32 | Marca de dominio público 1.0. Títulos y páginas de la transcripción de la biblioteca. Resolución baja (550 px de alto): sirve para tableros, no para imprimir |
| Internet Archive: Marcoy, *Travels in South America*, t. 1 (1875; U. de Toronto) | 2, 7 | `NOT_IN_COPYRIGHT` |
| Internet Archive: Squier, *Peru* (1877; Getty) | 16 | `NOT_IN_COPYRIGHT` |
| Internet Archive: Wiener, *Pérou et Bolivie* (1880; U. de Carolina del Norte) | 26 | Publicado en 1880; el autor murió en 1913 |
| Internet Archive: Semper, *Der Stil*, t. 2 (1863; Getty) | 13 | `NOT_IN_COPYRIGHT` |
| Internet Archive: Wright, *Bolivia, the Central Highway of South America* (1907; Getty) | 5, 6, 8, 17, 21, 31 | Publicado en 1907; fotografías sin autor identificado |
| Internet Archive: Gilbreth, *Motion Study* (1911; Prelinger Library) | 14, 23 | `NOT_IN_COPYRIGHT` |
| Public Domain Image Archive (Library of Congress, Metropolitan Museum, Rijksmuseum, Musée Albert-Kahn, U.S. National Archives, U. de Toronto) | 9, 10, 12, 15, 19, 20, 22, 24, 27, 28, 30 | Dominio público y «sin derechos añadidos» en la ficha de cada imagen. Las de la Library of Congress (9, 15, 19, 30) dicen «Public Domain U.S.» y «no known restrictions» |
| Cleveland Museum of Art | 3, 4, 11, 18, 25 | CC0 |

**Recortes.** Las ilustraciones de libros se recortaron de la página escaneada (detección automática de la mancha de la imagen, revisada a ojo; Semper y Marcoy n.º 2, a mano). De las estereoscopías se tomó la mitad izquierda.

## Lo que se descartó, y por qué

- **Las manos de Bulwer, *Chirologia* (1644).** El Public Domain Image Archive las publica con derechos digitales CC BY-SA: habría obligado a compartir los tableros con esa licencia. Es el mismo criterio que dejó fuera a Zubler en *Altiplano*. Las reemplaza la tabla de manos de Stebbins (n.º 27).
- **Las fotos de Ruth Kellogg** sobre posturas «correctas» para el trabajo doméstico (años veinte). Servían para la advertencia de la sección 7, pero sus derechos figuran como «no conocidos».
- **Una lámina de Muybridge** que el archivo titula como mujer que camina con una faja ortopédica (*back brace*): a primera vista parecía una canasta. La reemplaza *Emptying a Bucket of Water* (n.º 4).
- **El cargador maltratado de Guaman Poma** (dibujo 215). Habla de la carga forzada, pero es una escena de violencia; se dejó fuera, con el mismo criterio que *Altiplano* («ninguna imagen de violencia»).
- **Las fotos de Walle, *Bolivia* (1914).** Falta confirmar la fecha de muerte del autor. Su texto sí sirve: «temporary markets are established on the pavements. Amid piles of multi-coloured fruits...» (Walle, 1914: 63) [por cotejar en el impreso].
- **Una foto de cargadores de coliflores** (hacia 1910), por un daño en el escaneo.
- **No respondieron desde el entorno de trabajo:** la Library of Congress (verificación de Cloudflare), Wikimedia Commons (error 429, «demasiadas solicitudes», como en *Altiplano*) y las API del Metropolitan Museum y del Art Institute of Chicago. No se forzaron. La Library of Congress se consultó a través del Public Domain Image Archive.

## Lo que decides tú

1. **Las clasificaciones.** Son una primera lectura; cámbialas en `catalogo.json`.
2. **Si alguna imagen entra al artículo.** Regla de *Altiplano*: solo si un pasaje la pide, con su fuente y su dominio público comprobados, y nunca como ilustración de La Paz.
3. **La fecha de Vernet (n.º 18).** La ficha del museo da 1780-1836, las fechas de vida del autor; se ubicó hacia 1820 por el sello del litógrafo Delpech. Es una inferencia.
4. **La cita de Wright va con una foto de Sucre (n.º 8):** la cita describe La Paz. El pie lo dice; si molesta, se mueve.
