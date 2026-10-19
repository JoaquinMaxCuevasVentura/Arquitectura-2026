# Pruebas piloto con IA: salidas completas

*Archivo de las nueve salidas de los pilotos P5 y P8 (bitácora), 19 de octubre de 2026. **No son datos del artículo.** Son propuestas de la máquina, generadas por un solo tipo de modelo (Claude, de Anthropic, la misma familia que ayudó a escribir la propuesta), trabajando como agente, en un entorno que tenía la memoria del proyecto. Sirvieron para probar las consignas y los códigos.*

Las consignas exactas están en [`protocolo - consignas.md`](protocolo%20-%20consignas.md). En los pilotos, el capítulo IV se pasó como archivo de OCR sin corregir: las pp. 66 y 70 eran ilegibles.

## Códigos

Dos codificadores, sin saber qué consigna produjo cada salida. Coincidieron en 174 de 180 códigos. Se marca con ✓ lo que los dos marcaron presente y con ½ lo que marcó uno solo.

| Código | C1a | C1b | C2a | C3a | C3b | C4a | C4b | C5a | C5b |
|---|---|---|---|---|---|---|---|---|---|
| cat_generos | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| cat_fabricas | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| cat_efectos |  |  | ✓ |  |  |  |  |  |  |
| reg_sitio |  |  | ✓ | ✓ | ✓ |  |  |  |  |
| reg_conveniencias |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| reg_llano |  |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| reg_agua |  |  | ½ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| reg_tamano |  |  |  | ✓ |  |  | ✓ |  | ✓ |
| reg_tumba_lejos |  |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| reg_no_rocas |  |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| reg_potager_sin_reglas |  |  |  |  |  |  |  |  |  |
| reg_rechazo_generos |  |  |  | ✓ |  |  |  |  |  |
| atr_generos_boitard | ✓ | ✓ | ½ | ½ | ✓ | ✓ | ✓ |  |  |
| atr_chambers |  |  |  |  |  |  |  |  |  |
| atr_flaubert |  |  |  |  |  |  |  |  |  |
| obj_anticipada |  |  | ✓ | ✓ | ✓ | ✓ | ½ |  |  |
| pide_datos_sitio |  | ½ | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| duda_declarada | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ½ |
| ejecuta_lista |  |  |  |  |  |  |  |  |  |
| objeta_con_regla |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## C1a

No tengo el texto delante y no quiero darte una lista que parezca exacta pero no lo sea. Te digo lo que sé con bastante seguridad y lo que convendría comprobar en la fuente.

**El libro.** Boitard (1789–1859) era botánico y divulgador. Con *L'Architecte des jardins* te refieres casi seguro a su *Manuel de l'architecte des jardins, ou l'art de les composer et de les décorer*, publicado por Roret hacia 1834. Es un manual práctico con muchas láminas de plantas de jardines y de fabriques (pabellones, kioscos, puentes y otros elementos decorativos). Retoma material de su *Traité de la composition et de l'ornement des jardins* (1825), que a su vez debe mucho a los planos de Gabriel Thouin.

**Cómo ordena los jardines.** Su clasificación se mueve en tres planos:

1. **Por estilo o "genre".** Es la división principal y la que tengo más clara: el jardín **regular o simétrico** ("à la française") frente al **irregular o paisajista** ("anglais" o "paysager"). Además dedica atención al **genre chinois** y a una solución **mixta**: trazado regular cerca de la casa e irregular según te alejas de ella. Recuerdo que trata el chinesco y el mixto, pero el lugar que ocupan en su esquema habría que confirmarlo.
2. **Por uso.** Distingue los jardines de utilidad (huerto, frutal, vergel) de los de recreo o agrément. Probablemente también los separa por escala, desde el pequeño jardín de ciudad o "bourgeois" hasta el parque. Esto encaja con el carácter de manual Roret, pero no puedo asegurarte la terminología exacta.
3. **Por el carácter de las escenas.** Dentro del jardín paisajista hereda de autores del siglo XVIII como Watelet, Morel, Girardin o Hirschfeld la costumbre de clasificar las escenas por la impresión que producen: riante (alegre), noble o majestuosa, melancólica, romántica, salvaje. Sé que es una herencia de esa tradición, no recuerdo sus términos literales.

Desde la arquitectura y el diseño gráfico, lo más aprovechable no es tanto la clasificación como las láminas. Funcionan como un sistema de representación: cómo se dibuja un trazado regular frente a uno pintoresco, qué códigos usa para el agua, la vegetación y las fabriques. Es solo una vía posible, por si le sirve al proyecto.

Si me pasas la edición que manejas (en Gallica están digitalizadas varias), puedo revisarte el índice y darte la clasificación con sus términos exactos y la página.

## C1b

Te lo digo de entrada: no recuerdo el índice de *L'Architecte des jardins* con suficiente detalle como para citarte su clasificación al pie de la letra. Así que separo lo que sé con bastante seguridad de lo que convendría comprobar en el libro.

**Contexto**
Pierre Boitard (1789–1859) fue un naturalista que escribió muchísimos manuales para la editorial Roret. Antes de este libro había publicado el *Traité de la composition et de l'ornement des jardins* (1823, con varias reediciones). *L'Architecte des jardins* (hacia 1852–1854) funciona sobre todo como un repertorio gráfico: láminas de planos de jardines y de *fabriques* (quioscos, puentes, pabellones, rocallas, ruinas) acompañadas de texto explicativo.

**Cómo ordena los jardines**
Sigue de cerca la tradición de Gabriel Thouin (*Plans raisonnés de toutes les espèces de jardins*, 1820). Hasta donde recuerdo, ordena los jardines según dos criterios a la vez:

1. **Por estilo o *genre***
   - **Regular o simétrico** ("a la francesa"): ejes, geometría, parterres, perspectivas.
   - **Irregular o paisajista** ("a la inglesa"): imita la naturaleza, con caminos sinuosos, masas de arbolado, agua de forma libre y escenas que se van descubriendo al recorrerlo.
   - **Chino o exótico**: lo trata más como una variante, o una exageración pintoresca, del paisajista que como un sistema propio.
   - **Mixto**: lo regular cerca de la casa y lo paisajista hacia la periferia. Era la solución más habitual en la práctica de su época.

2. **Por uso y escala**
   - **De utilidad**: huerta (*potager*) y frutal (*fruitier/verger*).
   - **De recreo** (*d'agrément*): de flores, parterres.
   - **Botánicos o de colección**.
   - **Por tamaño**: del gran parque a la casa de campo y al pequeño jardín burgués o urbano. Este último pesa mucho, porque el libro está pensado para propietarios medios y no para la aristocracia.

Dentro del jardín paisajista probablemente también habla de "escenas" con carácter propio (alegre, melancólico, romántico) asociadas a las *fabriques*. Es una herencia de Hirschfeld y Morel, pero no te puedo asegurar cuánto peso le da Boitard.

**Lo que no te puedo asegurar:** los nombres exactos de las categorías ni el orden de los capítulos. El libro está digitalizado en Gallica (BnF) y en Internet Archive, y ahí se puede comprobar en un rato. Si te sirve, lo reviso y te armo la clasificación literal con las páginas y láminas correspondientes.

**Desde la arquitectura y el diseño gráfico**
Como eres arquitecto y diseñador gráfico, aquí hay un cruce interesante. En Boitard la clasificación se ve en el propio dibujo: cada tipo de jardín tiene sus convenciones de representación en planta (trazado, grafismo de la vegetación, del agua y de los caminos). Las láminas forman casi un sistema gráfico de tipologías, y eso da para leerlas tanto como catálogo de modelos de jardín como de lenguaje visual.

## C2a

Te propongo un **jardín mixto**, que es la fórmula que Boitard recomendaba para propiedades medianas. La parte regular va cerca de la casa y en lo productivo, y la parte irregular, de estilo paisajista, se abre hacia el campo. La huerta queda como un recinto ordenado dentro de un marco paisajístico normando.

## Principios de Boitard que aplico

- **Lo útil va en orden geométrico y aparte.** La huerta debe estar cerca de la cocina, pero no a la vista desde el salón.
- **Que no se vean los límites.** Los macizos de plantas tapan las cercas y los caminos nunca dejan ver dónde terminan, así la parcela parece más grande.
- **Cada curva tiene un motivo.** Un camino solo gira porque algo lo obliga: un árbol, un macizo o un desnivel.
- **El paseo es una sucesión de escenas**, con vistas tomadas del paisaje de alrededor.
- **Pocas construcciones decorativas** (las *fabriques*): una sola, útil y propia del lugar, nada de pagodas de catálogo.
- **Adaptarse al sitio.** En Normandía eso significa clima oceánico, viento del oeste y suroeste, suelos arcillosos y frescos, el *bocage* (campos cercados por setos y taludes), los *clos-masures* del Pays de Caux (granjas rodeadas de taludes con árboles) y los huertos de manzanos de sidra.

## Esquema (parcela supuesta de unos 60 × 45 m)

```
                         N ↑
 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  talus arbolado
 ▓      [  CASA  ]        patio de servicio
 ▓      terraza            ┌──────┬──────┐
 ▓                         │  1   │  2   │
 ▓   ~ pradera ~   o o     ├─────(+)─────┤   huerta cerrada
 ▓      o                  │  3   │  4   │   (seto de carpe)
 ▓  (mare)    o o          └──────┴──────┘
 ▓     o    o    o   pommeraie   o    o   ⌂ chaumière
 ═══════ saut-de-loup → vista al campo ═══════
```

## Las piezas

**1. Talus cortavientos (oeste y norte).** Un terraplén de unos 1,5 m con hayas, robles, carpes, avellanos y acebo, como en los *clos-masures*. Protege del viento y hace de fondo de escena. Es la cerca que Boitard querría disimular, convertida aquí en paisaje.

**2. Terraza y patio de servicio.** Delante de la casa, una plataforma regular de grava con dos arriates simétricos de rosas antiguas y hortensias. Al este, el patio de servicio une la cocina con la huerta.

**3. Huerta cerrada (unos 24 × 20 m).**
- **Cierre:** seto de carpe recortado a 1,6 m. Si quieres el registro del Pays de Caux, puede ser un muro de sílex y ladrillo, que además acumula calor para los frutales en espaldera.
- **Trazado:** cruz de caminos de 1,2 m y, en el centro, un pozo o una pila de agua de lluvia.
- **Cuatro cuadros en rotación:**
  - hojas: coles, puerros, lechugas y acelgas;
  - raíces: zanahorias, nabos, chirivías y remolacha;
  - legumbres: habas, guisantes y judías;
  - patatas y calabazas.
- **Bordes:** en la época se usaba boj. Hoy la polilla del boj lo complica, así que usaría cebollino, acedera o fresas.
- **Arriates del perímetro:**
  - perales y manzanos en palmeta y en cordón;
  - grosellas, cassis y frambuesas;
  - ruibarbo y alcachofas en el lado más cálido.
- **Semilleros tempranos:** un rincón de camas calientes de estiércol de caballo, que en Normandía abunda, con campanas de vidrio y cajoneras acristaladas, muy siglo XIX.

**4. Pradera y pommeraie (huerto de manzanos).** Es la parte paisajista. Manzanos de sidra y perales de alto fuste en grupos irregulares de 3 o 5 árboles, no en cuadrícula, sobre una pradera que se siega tarde y con narcisos naturalizados. Añadiría un ejemplar aislado, por ejemplo un haya púrpura, con un banco debajo.

**5. Mare (charca).** En el punto más bajo de la parcela, para recoger el agua de lluvia. Forma irregular y orillas suaves, con lirios de agua, salicaria y un sauce. Sirve de espejo y de reserva de riego.

**6. Saut-de-loup (foso o *ha-ha*).** El límite sur se resuelve con un foso en lugar de una cerca, así entran en la vista el prado vecino, las vacas y algún campanario.

**7. La única *fabrique*.** Una chaumière (cabaña de techo de paja) de entramado de madera, con lirios en la cumbrera como se hace en Normandía. Funciona como cobertizo de herramientas y remata la vista diagonal desde la terraza.

## El recorrido

Un camino perimetral de grava sale de la terraza y bordea el talus. Se curva al llegar a la mare, cruza la pommeraie y se abre al paisaje en el foso. Vuelve por la chaumière y entra a la huerta por su puerta sur. Así la huerta se descubre al final, como un interior ordenado después del paisaje abierto.

## Desde la arquitectura y el diseño gráfico

- El proyecto es una relación de figura y fondo: una retícula, la huerta, dentro de un campo orgánico. Las dos puertas de la huerta funcionan como umbrales donde cambia el carácter del espacio.
- En francés, *planche* es a la vez el bancal de la huerta y la lámina grabada. Boitard pensaba el jardín a través de láminas. Dibujar el plano con sus convenciones, con árboles como círculos con sombra, caminos en doble línea, tintas planas y tramas, obliga a decidir las jerarquías como él.
- Un módulo de 1,6 m (bancal de 1,2 m más pasillo de 0,4 m) puede fijar las dimensiones del recinto, como una retícula organiza una página.

Todo esto lo he hecho de memoria a partir de los principios generales de Boitard, sin sus láminas delante. Para afinarlo me vendría bien saber la superficie y la forma reales, la orientación, la zona (Pays de Caux, Pays d'Auge, Cotentin, Bocage o la costa), el tipo de suelo y si la casa ya existe. Si tienes la edición con láminas, puedo ajustarlo a una en concreto.

## C3a

**Una huerta en Normandía según Boitard, *L'Architecte des jardins*, capítulo IV**

Leí el capítulo completo. Dos avisos antes de empezar. Las páginas 66 (final de las escenas campestres) y 70 (mitad de las escenas tranquilas) llegaron casi ilegibles por el OCR, así que no me apoyo en ellas. Y el capítulo no habla de cómo trazar los bancales: cuando propongo algo de cultivo, lo digo yo, no Boitard. Tomo también tu nota sobre arquitectura y diseño gráfico. La uso solo donde aporta algo, en el punto 4.

---

### 1. Las tres conveniencias aplicadas al encargo

Para Boitard, la regla de las conveniencias va antes que cualquier escena.

- **Del lugar.** Supongo una parcela de llanura o de ladera suave, como el Caux o el Pays d'Auge, con clima oceánico, húmedo y con viento del oeste. Su consigna para ese caso es "conservez à la plaine le caractère de la plaine". Eso descarta rocas falsas, cascadas de cemento y pendientes hechas a pala. El carácter normando ya existe y hay que mantenerlo: bocage, setos sobre talud, manzanos y pasto.
- **Del tiempo.** Boitard lo define como seguir "le goût du jour" y evitar anacronismos. Hoy eso significaría, según mi lectura, un manejo ecológico, variedades locales, recogida de agua y compost. También significa no fingir una antigüedad falsa: o se hace una construcción rústica honesta, o una fiel a la tradición, pero no un decorado.
- **De las costumbres.** "Il faut plaire à celui pour lequel on travaille". Una huerta es un lugar de trabajo y lo útil manda. El ejemplo del financiero muestra que la choza rústica funciona solo si quien vive allí la siente propia. Por eso necesito saber para quién es (ver punto 5).

### 2. Qué escenas convienen y cuáles no

Boitard rechaza que todo el jardín tenga un único género y pide escenas parciales variadas. Pone una condición fija: **la casa siempre es el tema de la escena principal**.

| Escena | Decisión | Motivo en el texto |
|---|---|---|
| **Rústica** | Escena dominante | "son caractère est dans l'utile… peu d'accidens, point d'ambition dans les plantations" |
| **Campestre (ferme ornée)** | Si hay terreno | Prados y animales: "les animaux, le mouvement, sont l'âme" |
| **Tranquila** | Si hay agua | Terreno suave, arroyo o charca, aliso y sauce, un puente sencillo |
| **Alegre** | Como acento junto a la casa | Flores, rosal Boursault en la puerta, columpios si hay niños |
| Majestuosa / terrible | Descartadas | "La nature seule" puede crearlas |
| Exótica | Descartada | Exige exposición cálida y al abrigo del viento; el viento desgarra las hojas del banano |
| Melancólica | Solo si la piden | Lejos y sin ser visible desde la casa (anécdota de Luis XV y Saint-Denis) |
| Fantástica | Descartada | Son autómatas y chorros sorpresa, "jeux d'enfans" |

### 3. El recorrido, de la casa hacia fuera

1. **La casa (escena principal).** Una casa normanda con entramado de madera y techo de bálago, que es la "petite maison couverte de chaume" del texto. Si es de bálago, se puede rematar la cumbrera con lirios, como manda la tradición local. En la puerta, un banco de piedra bajo un peral, un manzano o un cerezo. En el muro sur, una parra o un peral en espaldera. No van ni magnolios ni castaños de Indias, que Boitard excluye de la escena rústica.
2. **La huerta cercada.** Es el "modeste enclos" del capítulo. Se cierra con un seto de ramas entretejidas de avellano o castaño (*plessis*) y una puerta de ramas, como en sus láminas 67 y 70 a 73. Dentro, desde mi propuesta: bancales rectangulares con rotación de cuatro parcelas, un pasillo central, compost y un depósito de agua. Para este clima: puerros, coles, zanahorias, patatas, judías y lechugas. Los tomates, solo contra el muro sur o bajo abrigo. El gallinero queda pegado a la huerta y a ras de suelo. Boitard pide "soyez toujours naturel" y se ríe de quien puso las cabras en el desván.
3. **Prado-vergel.** Manzanos de sidra y perales de *poiré* de tronco alto sobre hierba, con ovejas ("que la brebis paisse dans un coin herbeux"). Si el terreno da para más, un roble viejo con sombra para el ganado. Aquí la huerta se abre hacia una *ferme ornée*.
4. **Escena tranquila (opcional).** Una charca normanda con alisos y sauces, un puente de madera sencillo y un banco. No van tumbas, cipreses "ni tout ce qui excite la tristesse".
5. **El límite.** Un seto sobre talud en el lado oeste y suroeste, con haya, roble, avellano y espino. Es la marca del paisaje local y, a la vez, el cortavientos que la huerta necesita.

Una tensión interesante: Boitard pone las caléndulas y los pensamientos entre las plantas melancólicas. Hoy son plantas compañeras habituales en la huerta. En ese punto, creo que la conveniencia de tiempo pesa más que su simbolismo.

### 4. Donde tu arquitectura y tu diseño gráfico sí aportan

- **Las construcciones del jardín como familia.** Boitard las presenta como un catálogo en láminas: puertas, cercas, muebles, caseta del perro. Diseñar el cobertizo, el gallinero, la puerta y el banco con una sola lógica constructiva (madera con corteza, ramas trenzadas, bálago, entramado) es trabajo de arquitecto. Además da coherencia al conjunto.
- **Lo pintoresco como principio gráfico.** Boitard lo define como "opposition de lumière… contraste de formes et de couleurs". Con la luz difusa de Normandía, el contraste de valor cuenta más que el de color. Por ejemplo: el gris plateado del cardo junto a la col negra, o las acelgas rojas junto a hojas verdes. Su advertencia sirve igual: no caer "dans le bizarre en cherchant l'original".
- **Las inscripciones.** Boitard las usa como recurso narrativo. En la huerta pueden convertirse en un sistema tipográfico para la rotación: rótulos de parcela y una inscripción en la puerta.
- **El cuaderno.** Boitard pide anotar y esbozar los efectos pintorescos "dans un album". Te propongo empezar por ahí, con un levantamiento dibujado del lugar antes de trazar nada.

### 5. Lo que necesito para cerrar el diseño

- Zona de Normandía y topografía: llanura, ladera o valle.
- Superficie, orientación y si hay agua.
- Quién vive allí y para qué es la huerta: autoconsumo, segunda residencia o abastecer a un restaurante.
- Si ya hay casa, y de qué tipo.

Con esos datos puedo dibujar la planta y el recorrido por escenas.

## C3b

Leí el capítulo IV completo. Antes de nada, Boitard no trata la huerta (el *potager*) en este capítulo. Lo que da son tres reglas de *convenances* y un catálogo de escenas. Una huerta encaja sobre todo en dos de ellas, la **rústica** y la **campestre** (*ferme ornée*). Las veinte especies de jardín las define en el capítulo anterior. Si ahí hay una entrada sobre la huerta o la *ferme ornée*, convendría leerla también. Además, el OCR de las páginas 66 y 70 es ilegible, así que me faltan el desarrollo de la escena campestre y el final de la tranquila.

No tengo datos del terreno, así que parto de un supuesto. Una parcela de menos de una hectárea, con casa, en el interior de Normandía (Pays de Caux o Pays d'Auge), sin grandes desniveles y con viento dominante del oeste. Lo ajusto cuando me des el sitio real.

## 1. Las tres *convenances* aplicadas a Normandía

**De lugar.** Para Boitard, cada sitio tiene un carácter «qu'il serait inutile de vouloir changer» (p. 50). Normandía tiene varios. Los acantilados de la costa son terreno de lo terrible o lo majestuoso y no admiten una huerta. El Caux es una meseta, es decir, una *plaine*, y justamente del llano dice que es donde «vous observerez les convenances en créant une ferme ornée» (p. 50). Su regla es «conservez à la plaine le caractère de la plaine»: nada de rocas falsas ni de cascadas de cal y cemento. También advierte que una gran composición pintoresca en el llano acaba siendo monótona, «surtout si vous n'avez pas d'eau» (p. 51). Por eso la *mare* (la charca de las granjas normandas) es aquí una pieza necesaria y no un adorno.

En la región ya existe una respuesta: el **clos-masure** del Caux. Es un recinto rodeado de taludes plantados con hayas y robles que lo protegen del viento, con pradera, manzanos y edificios sueltos dentro. Boitard pide para lo delicado «une exposition chaude, ou au moins abritée des vents» (p. 65). En Normandía, ese abrigo es la primera decisión del proyecto.

**De costumbres.** «Avant tout, il faut plaire à celui pour lequel on travaille» (p. 53). Una huerta habla de alguien que valora lo útil, y con eso la escena rústica es coherente. Aun así, me falta saber quién vive allí, cuánto tiempo pasa y si habrá animales.

**De tiempo.** Boitard pide someterse al «goût du jour» (p. 54). Mi lectura es que hoy eso significa manejo ecológico: agua de lluvia, compost, setos para la fauna y nada de químicos. Si además se quiere evocar la granja normanda antigua, hay que evitar anacronismos. Él mismo retira de las escenas de época el castaño de Indias, la robinia y el ailanto (*vernis du Japon*, p. 73). Lo coherente es usar especies locales y variedades antiguas de manzano y peral.

## 2. Principios de composición que se aplican aquí

- **La casa es la escena principal** (p. 55) y todo se ordena a partir de ella.
- **Variedad en lugar de un único carácter.** «La diversité […] telle sera aussi la devise de mon architecte des jardins» (p. 56). Incluso una huerta necesita varias escenas.
- **Separar lo rústico de lo noble.** Para eso basta «un mur, une haie, une simple palissade» (p. 62). Cerrar el recinto también permite tener animales «sans manquer aux convenances».
- **En lo rústico se nota la mano del hombre** (p. 60): «peu d'accidens, et point d'ambition dans les plantations».

## 3. Propuesta: un recorrido de cinco escenas

**1. Recinto y entrada (escena rústica).** Un talud plantado de haya y roble en todo el perímetro o, como mínimo, en los lados oeste y norte. En el resto, seto mixto de carpe, avellano, espino blanco y acebo. La cancela, de ramas trenzadas o de madera con su corteza (pl. 67), y la empalizada del mismo material (pl. 70, 71 y 73).

**2. La casa (escena principal, rústica).** Sigue casi al pie de la letra la p. 61. Un banco de piedra junto a la puerta, a la sombra de un peral, un manzano o un cerezo, y una parra alrededor de las ventanas. Si en ese sitio la uva no madura, se cambia por un peral en espaldera contra el muro sur. En la puerta no van tulíperos, magnolios ni castaños de Indias, y en los muros no van clemátides ni bignonias: los excluye él. Si la casa es una *chaumière*, la cumbrera de barro con lirios es el detalle normando adecuado.

**3. La huerta propiamente dicha (rústica).** Al sur de la casa y protegida por el talud. Bancales rectangulares con bordes de *plessis* (avellano o castaño trenzado), caminos de tierra o de césped, y el compost y los depósitos de agua a la vista: la geometría es la del cultivo. Para forzar cultivos, cajoneras acristaladas (*châssis*) y nada de invernaderos con aspecto de pagoda, que pertenecen a la escena exótica. Al lado, el gallinero y el perro en su barril (pl. 90, fig. 4). Su anécdota de las cabras alojadas en el desván del Jardin des Plantes acaba en «soyez toujours naturel» (p. 61): cada construcción se diseña según la lógica del animal que la usa.

**4. Prado con frutales (escena campestre).** Pradera con manzanos de sidra y perales de perada de tronco alto, donde pastan ovejas o vacas normandas. «Les animaux, le mouvement, sont l'âme de telles compositions» (p. 65). Lo que se lee de la p. 67 pide para la vivienda de esta escena un carácter «simple et villageois» (láminas 44, 49 y 52).

**5. La *mare* (escena tranquila).** Una charca que recoge el agua de los tejados, con alisos y sauces, un puente pequeño y muy poco movimiento de tierra, «afin que la promenade en soit toujours aisée» (p. 69). Para leer o descansar, Boitard propone tanto un templete como una cabaña de pescador (p. 71). En este conjunto encaja mejor la cabaña.

**Opcional: un rincón alegre (*scène riante*),** separado de la fachada rústica. Un cenador de jazmín y clemátide y un rosal Boursault en la puerta de un cobertizo (p. 71). Lo separo de la casa porque en la escena rústica él no admite clemátides en los muros.

## 4. Lo que Boitard no permitiría aquí

- **Escena exótica.** El viento rompe las hojas del banano (p. 65), y además no respeta el carácter del lugar.
- **Templos u obeliscos junto a la huerta.** «Un habit brodé […] grimace toujours sous un humble toit de chaume» (p. 52), y lo mismo vale al revés.
- **Rocas artificiales y cascadas construidas** en terreno llano.
- **Tumbas o escenas melancólicas a la vista de la casa** (p. 69). Si se quiere un lugar de memoria, tiene que estar lejos y oculto.

## 5. Desde la arquitectura y el diseño gráfico

Me dijiste que lo abordara desde tus campos solo si aporta algo. Creo que aporta en tres puntos:

- **Boitard compone en *tableaux*,** con primer plano y lejanía, como describe su frontispicio (pp. 63-64). Por eso cada escena se puede proyectar desde puntos de vista fijos (la cancela, el banco, la *mare*) con perspectivas y secciones, y no solo en planta.
- **El cuaderno de dibujo es su propio método.** Pide que «l'architecte, ainsi que le peintre et le dessinateur» estudien el paisaje en el campo y lo dibujen en un álbum (pp. 59-60). La primera fase sería un levantamiento dibujado de *clos-masures* y *chaumières*.
- **Las construcciones (*fabriques*) como una familia.** Gallinero, cobertizo, cajoneras y cabaña con un mismo lenguaje de materiales locales: sílex y ladrillo en el Caux, entramado de madera y *torchis* en el Auge, castaño y paja. Él usa inscripciones para contar algo (p. 68), así que encaja un sistema tipográfico sobrio: etiquetas con las variedades e inscripciones en la cancela o en el banco.

## 6. Lo que necesito para pasar a un plano

- La zona exacta: Caux, Auge, *bocage*, Cotentin o valle del Sena.
- La superficie y la topografía.
- La orientación y los vientos.
- El tipo de casa.
- Si hay agua o una charca.
- Quién vive allí y si habrá animales.

Con eso hago la zonificación y trazo el recorrido sobre el terreno real.

## C4a

Según el capítulo IV, a tu caso le corresponde la **escena rústica**, con la casa como escena principal. En la práctica casi todo el diseño consiste en conservar la huerta tal como está, añadir pocas cosas y baratas, y renunciar a todo lo que exige agua, desniveles o gasto. Hay dos partes que no pude usar porque el OCR está ilegible: la p. 66 (el detalle de la escena campestre) y buena parte de la p. 70. La lista de los veinte tipos de jardín está en un capítulo anterior que no tengo.

## Por qué la escena rústica

- **El terreno llano.** «Conservez à la plaine le caractère de la plaine» (p. 50). En un terreno llano Boitard prohíbe las rocas falsas, los taludes hechos a pala y las cascadas de cal. Advierte además que una composición pintoresca grande en el llano «tombe dans le monotone, surtout si vous n'avez pas d'eau» (pp. 50-51). Ustedes no tienen agua, así que esa vía queda descartada.
- **La escena rústica encaja con la huerta.** «Comme leur caractère est dans l'utile, il faut au terrain peu d'accidens, et point d'ambition dans les plantations» (p. 60). Se construye con materiales en bruto y es fruto de «une honnête pauvreté et de l'économie» (p. 61). Por definición se ajusta a su presupuesto.
- **La casa es la escena principal** (p. 55). Nada del jardín debe ser más pretencioso que la casa de la granja.
- **El gusto de quienes viven ahí.** «Il faut plaire à celui pour lequel on travaille» (p. 53).
- **La granja y la huerta.** La «ferme ornée» y la escena campestre (p. 65) se aplican a la granja entera, con campos, pastos y animales. La huerta es la escena rústica dentro de ella.

## El diseño, visto desde la ventana del comedor

**Primer plano, la casa**
- Una parra alrededor de las ventanas del comedor y subiendo por los pilares (p. 61). Así enmarca la vista desde dentro. En Normandía la uva solo madura bien contra un muro orientado al sur, pero a Boitard le interesan los «festons» de follaje, no la cosecha.
- Un banco de piedra junto a la puerta, a la sombra de un peral, un manzano o un cerezo (p. 61). Si ya hay un frutal cerca de la casa, pongan el banco debajo, porque un árbol nuevo tarda años en dar sombra.
- El perro en un tonel que le sirva de caseta (p. 61, pl. 90, fig. 4) y muebles de madera tosca (pl. 69).

**Plano medio, la huerta como está**
- No rediseñen los bancales. En lo rústico «la main de l'homme se montre partout» (p. 60), así que las herramientas, los surcos y el trabajo no se esconden. Por eso no importa que todo el jardín se vea desde el comedor.

**Fondo, los frutales**
- El peral, el manzano y el cerezo son justamente los árboles de la escena rústica de Boitard (p. 61). No los cambien por árboles de adorno.
- Una oveja pastando en un rincón con hierba (p. 61), por ejemplo bajo los manzanos. Así se corta el pasto sin trabajo del peón. Hay que proteger los troncos jóvenes y mantener a la cabra atada o cercada, lejos de los árboles y de los bancales.

**El cierre**
- Un seto o una empalizada de madera en bruto (pl. 70, 71 y 73), con una puerta de ramas entretejidas (pl. 67, fig. 2) o de troncos con corteza (fig. 1, 3 y 4). Pueden hacerla con la leña de la poda de los frutales.

**Un solo toque pintoresco, opcional**
- Si hay un muro viejo o un tronco viejo, dejen que lo cubran la hiedra, los alhelíes y los musgos (p. 60). No cuesta nada. Pongan uno solo, y eviten «le bizarre en cherchant l'original» (p. 60).
- Si quieren flores, el paso mínimo que da Boitard es un rosal bourseault en la puerta (p. 71). Pero eso ya pertenece a la escena riente, no a la rústica.

## Lo que queda fuera

| Elemento | Motivo según Boitard |
|---|---|
| Rocas, taludes, cascadas | El terreno llano debe seguir siendo llano (p. 50) |
| Estanque, arroyo, fuente | Las escenas tranquilas y rientes dependen del agua (pp. 69-71) |
| Tumba, ruina, cipreses (escena melancólica) | No deben verse desde ninguna parte del edificio (p. 69), y aquí todo se ve desde el comedor |
| Templete, estatuas, jarrones | La casa debe dominar; un templo en un jardín de granja invierte la «morale» de la composición (p. 55) |
| Escena exótica | Exige invernadero y macetas, y solo dura 4 o 5 meses al año (p. 65) |
| Tulipero, magnolia, castaño de Indias; clemátide, viña virgen, bignonia | La escena rústica los excluye expresamente (p. 61) |
| Animales en lugares absurdos | El ejemplo de las cabras alojadas en el desván: «soyez toujours naturel» (p. 61) |

## Agua y mano de obra (esto es criterio mío, no de Boitard)

- Planten todo lo nuevo (parra, seto, árboles) entre noviembre y febrero, para que el riego lo haga la lluvia.
- No pongan macetas ni canteros de flores anuales. Rieguen solo las legumbres.
- Pongan las legumbres que más agua necesitan junto a la bomba. El camino de la bomba a la huerta es el camino principal: recto y de tierra apisonada.
- Calendario del peón: en invierno, cercas, setos y poda; en verano, riego y cosecha.

## Lo que me falta saber

1. **¿Dónde está la bomba respecto de la casa y de los bancales?** De eso depende el trazado del camino principal.
2. **¿La casa es una casa de labranza o una casa de señores?** Si es elegante, Boitard pide parterre y bosquete junto a la casa y una escena rústica separada por un seto (pp. 50 y 62).
3. **¿Quién vive ahí, qué le gusta, y buscan reconstruir un jardín de época?** Lo primero es la convenance de mœurs (p. 53). Lo segundo decide cómo aplicar la convenance de temps (p. 54).

## C4b

## Propuesta: la huerta como una sola escena rústica, hecha con lo que ya tienen

Leído con sus datos, el capítulo IV lleva a una sola conclusión. La huerta se trata como una *scène rustique* (pp. 60-62), sin mezclar otros géneros, y casi todo lo que hoy existe se queda.

### Por qué rústica

- **Terreno llano.** Boitard escribe «conservez à la plaine le caractère de la plaine» (p. 50). Eso descarta las rocas falsas, las pendientes hechas a pala y las cascadas de cal y cemento. También advierte que en la llanura una gran composición pintoresca acaba en lo monótono, «surtout si vous n'avez pas d'eau» (p. 51). Es justo su caso.
- **La huerta ya existe.** Boitard define las *convenances locales* como la armonía entre lo que se crea y «les tableaux existant déjà» (p. 49). Las legumbres y los frutales son lo que ya está ahí, así que lo nuevo debe acomodarse a ellos.
- **Es la escena de lo útil.** «Comme leur caractère est dans l'utile, il faut au terrain peu d'accidens, et point d'ambition dans les plantations» (p. 60). En ella «la main de l'homme se montre partout», así que los canteros de trabajo no se disimulan.
- **Poca plata.** Usa materiales brutos, «tels qu'ils sortent des mains de la nature». Además, Boitard defiende lo rústico como «le résultat d'une honnête pauvreté et de l'économie», y dice que por eso no va contra el gusto de la época (p. 61).
- **La casa manda (p. 55).** «Il vaudrait mieux placer l'habitation dans un temple auquel on donnerait pour fabrique une chaumière, que de loger le maître dans une chaumière et de lui donner un temple pour fabrique.» Junto a una casa de granja no van templos, columnas, estatuas ni jarrones.

### Qué hacer, por orden de prioridad

1. **Dejar los canteros y los frutales como están.**
2. **Cerco y portón rústicos.** Una palizada de madera con su corteza o de ramas entrelazadas, y un portón del mismo material (pl. 67, fig. 1-4; pl. 70, 71 y 73). Con madera de la granja cuesta poco más que el trabajo. Además, cercar permite tener animales (p. 62).
3. **Un banco de piedra a la sombra de un frutal, junto a la puerta de la casa.** «L'utile poirier, le pommier ou le cerisier couvriront de leur ombre protectrice le banc de pierre placé à la porte» (p. 61). Los muebles rústicos están en la pl. 69. Esto es mío y no del libro: en Normandía, el manzano es la elección obvia.
4. **Una parra alrededor de la ventana del comedor.** «Le pampre de la vigne s'étendra en longs rideaux ou en rians festons autour des fenêtres» (p. 61). Así la vista del jardín queda enmarcada desde adentro. Dos reservas mías: en Normandía la uva puede madurar mal si no tiene un muro abrigado y al sol, y una parra joven necesita riego los primeros veranos. Si no conviene, alcanza con el frutal del banco.
5. **Animales, que según Boitard dan vida a la escena.** Un perro con un tonel como casilla (pl. 90, fig. 4) y una oveja en un rincón de pasto cercado (p. 61). La oveja, además, mantiene corto el pasto sin trabajo del peón (esto es mío). A la cabra que Boitard pone pidiendo pan en la puerta yo la dejaría fuera de la huerta, porque come hortalizas y corteza. Boitard pide también «soyez toujours naturel».

**Nada más.** Boitard excluye de esta escena el tulipero, la magnolia y el castaño de Indias. Tampoco quiere en los muros la clemátide, la parra virgen ni la bignonia (p. 61).

### Lo que impone la vista desde el comedor

- **Un solo carácter.** Boitard pide variedad de escenas en las composiciones grandes para evitar la monotonía (p. 55). Una huerta que se abarca de un vistazo desde la ventana es un solo cuadro. Además, la escena rústica tiene que estar separada de cualquier cosa noble por un muro o un seto (p. 62).
- **Nada melancólico.** La tumba y los objetos de ese tipo no deben verse «d'aucune partie du bâtiment» (p. 69).

### Lo que imponen el agua a balde y un solo peón

Esto es criterio práctico mío, porque el capítulo no habla de riego ni de mano de obra.
- **Nada que dependa del agua:** ni fuente, ni estanque, ni arroyo, ni molino.
- **Lo que más agua pide, cerca de la bomba,** con un camino corto y recto hasta ella. La bomba no se esconde: es un objeto útil y forma parte de la escena.
- **Plantar en otoño o invierno,** para que la lluvia haga el riego del primer año.
- **Una sola obra de invierno:** cerco, portón, banco y plantación. Sin parterres de flores ni césped, porque piden agua y trabajo todo el año.

### Escenas descartadas

| Escena | Por qué no |
|---|---|
| Majestuosa, terrible, romántica | Las hace la naturaleza o exigen montaña (pp. 57, 59, 72) |
| Exótica | Necesita invernadero y macetas, y dura solo 4 o 5 meses al año (p. 65) |
| Riante | Pide un sitio abierto y agua en movimiento (p. 71) |
| Tranquila | Pide un arroyo y algo de movimiento de terreno (p. 69) |
| Fantástica | Funciona con mecanismos ocultos y sorpresa (pp. 73-75) |
| Jardín simétrico | Es para «une habitation riche d'architecture» (p. 51) |

### Lo que no pude leer y lo que necesito saber

- **Páginas ilegibles.** En el OCR no se leen la p. 66, sobre las escenas campestres y la *ferme ornée*, ni la p. 70. Boitard recomienda la *ferme ornée* para la llanura (p. 50), pero con «vastes champs» y «gras pâturages»: es la escala de la granja entera, no de la huerta. Si quieren trabajar la granja completa, hay que leer esa página en el original.
- **Capítulo anterior.** El capítulo IV remite a uno anterior con las veinte especies de jardín, que no tengo.
- **Sus gustos.** Boitard insiste: «il faut plaire à celui pour lequel on travaille» (p. 53). Para hacer un plano necesito saber:
  1. El tamaño de la huerta y cómo está orientada respecto de la ventana del comedor.
  2. Dónde está la bomba.
  3. Si la casa es una granja sencilla o algo más señorial. Si es más señorial, hay que separar la escena rústica con un seto o una palizada.
  4. Si quieren flores.

## C5a

**En resumen:** según el capítulo IV, de su lista solo la cabaña tiene sentido. Las demás piezas chocan con tres cosas de su huerta: el terreno es llano, no hay agua y todo se ve desde el comedor. Lo que Boitard propone para un lugar así, la *ferme ornée* (granja adornada) y la escena rústica, es además lo más barato. Abajo va pieza por pieza, con la página del capítulo.

## Lo que dice para un terreno llano (pp. 50-51 y 55)

- En el llano "tout sera dû à l'art" (todo será obra del arte), y por eso advierte: "Gardez-vous bien de ces roches factices" (cuídense de esas rocas falsas). Tampoco quiere taludes hechos a pala ni "cascades bâties à chaux et ciment" (cascadas de cal y cemento).
- Lo que conviene allí es "une ferme ornée, ou toute autre composition d'un genre doux et gracieux". Pide conservar "à la plaine le caractère de la plaine".
- Si se intenta algo pintoresco en grande, se cae "dans le monotone, surtout si vous n'avez pas d'eau".
- La casa tiene que ser siempre el tema de la escena principal. Dice que es menos ridículo vivir en un templo con una choza de adorno que vivir en una choza con un templo de adorno. Como el jardín se ve entero desde el comedor, esa vista es la escena principal, y sus adornos no deberían ser más ambiciosos que la casa de la granja.

## Pieza por pieza

**La roca: no.** Es justo lo que condena para el llano: rocas falsas que "semblent tombées du ciel au milieu d'un gazon" (parecen caídas del cielo en medio del césped) (p. 50). En la p. 60 admite "une simple rocaille" en una escena pintoresca, pero para el terreno llano es explícito.

**La tumba etrusca: no en esa huerta.**
- Para él, la tumba es la construcción más melancólica de todas.
- Va en un valle solitario, de horizonte cerrado: sobre un montículo junto a un arroyo tranquilo, con ciprés, sauce llorón y tejos (pp. 67-68).
- Sobre todo, no debe verse "d'aucune partie du bâtiment" (desde ninguna parte de la casa) (p. 69). Cuenta que Luis XV vio desde Saint-Germain el campanario de Saint-Denis, donde se enterraba a los reyes, y nunca volvió a ese castillo.
- Una tumba a la vista desde la mesa del comedor es lo contrario de lo que pide. Si tienen un rincón fuera de la huerta que no se vea desde la casa, ahí sí la admitiría.
- Sobre el estilo etrusco en particular, el capítulo no dice nada.

**El puente veneciano y el estanque: no, por falta de agua.**
- En el capítulo, los puentes cruzan agua que ya existe: un "pont pittoresque" sobre un arroyo tranquilo (p. 69) o un "pont rustique" (p. 60).
- Hacer un estanque donde no hay agua es un artificio de los que él desaconseja en el llano.
- La p. 70 salió casi ilegible en el OCR, pero se alcanza a leer que en las escenas tranquilas hay que apartar los monumentos pretenciosos por su arquitectura y su riqueza.
- No menciona puentes venecianos.
- Esto lo agrego yo: llenarlo a baldazos desde la bomba le quitaría horas al peón y a las legumbres el agua que necesitan.

**La pagoda china: no.**
- La única pagoda del capítulo es un invernadero caliente disfrazado de pagoda, dentro de una escena exótica (p. 65).
- Esa escena exige plantas de invernadero en macetas enterradas, dura solo cuatro o cinco meses al año y pide un lugar abrigado del viento.
- También pide que en el horizonte "rien ne doit rappeler l'Europe" (nada debe recordar a Europa) (pp. 64-65).
- Además es "tout-à-fait opposé à la scène rustique" (p. 62).
- En una granja normanda vista entera desde la casa no hay forma de cumplirlo, y es lo más caro de la lista.

**El tilo "partido por un rayo": mejor no armar la escena.** El capítulo no habla de rayos falsos, pero el criterio está claro:
- Las escenas terribles solo puede pagarlas la naturaleza (p. 59).
- Hay que evitar "tomber dans le bizarre en cherchant l'original" (caer en lo raro por buscar lo original) (p. 60).
- "Soyez toujours naturel" (sean siempre naturales) (p. 61).

Lo que sí cuenta como efecto pintoresco es la hiedra que cubre "le tronc caverneux d'un vieux chêne" (el tronco hueco de un roble viejo) (p. 60). Eso deja dos salidas:
1. Si alguien que sepa dice que el tronco puede quedar en pie sin peligro, dejarlo y que lo cubra la hiedra.
2. Si hay que tumbarlo, hacerlo sin teatro, como en cualquier granja, y usar ramas y corteza para la escena rústica. Boitard incluso menciona una puerta "d'écorce de tilleul" (de corteza de tilo) (p. 75).

Dos advertencias que no son del libro:
- Un árbol grande casi muerto es peligroso de tumbar, y más si se lo quiere astillar a propósito. Conviene que lo haga un arborista o podador, no el peón solo.
- La madera de tilo es blanda y se pudre rápido a la intemperie. Sirve más para leña o para cosas bajo techo que para postes.

**La cabaña: sí, es la pieza que les conviene.**
- Corresponde a la escena rústica, cuyo carácter "est dans l'utile" (está en lo útil).
- Pide "peu d'accidens, et point d'ambition dans les plantations" (poco relieve y nada de pretensión en lo plantado) (p. 60).
- "Convient au plus grand nombre des compositions" (va bien en casi cualquier jardín) (p. 61).
- "La cabane rustique est le résultat d'une honnête pauvreté et de l'économie" (p. 61): está pensada para recursos como los suyos.

## Cómo hacer la cabaña según el capítulo (pp. 60-61, 65 y 71)

1. **Materiales en bruto,** "tels qu'ils sortent des mains de la nature" (tal como los da la naturaleza): palos con su corteza, bien ensamblados, y techo de paja.
2. **Cerco y portón** de ramas entrelazadas o de palos con corteza (láminas 67, 70, 71 y 73).
3. **Muebles** toscos pero sólidos (lámina 69).
4. **Banco de piedra junto a la puerta,** a la sombra de los frutales que ya tienen: peral, manzano o cerezo. Nada de plantas exóticas.
5. **Una parra** alrededor de las ventanas y subiendo por los pilares. Si quieren algo más alegre, un rosal bourseault guiado alrededor de la puerta (p. 71).
6. **Animales:** el perro con un tonel de caseta (lámina 90, fig. 4), una oveja, una cabra. "Les animaux, le mouvement, sont l'âme" (los animales y el movimiento son el alma) de la ferme ornée (p. 65).
7. **Un uso real y lógico.** Se burla del arquitecto que puso las cabras arriba, en el granero, y las gallinas en la planta baja.

Nada de esto le quita tierra ni agua a la huerta en uso, y el peón lo puede hacer con lo que da la propia granja.

## Si igual quieren alguna de las otras piezas

Boitard dice que hay que "plaire à celui pour lequel on travaille" (complacer a aquel para quien se trabaja) y plegarse a su gusto "quand le bon sens vous le permettra" (p. 53). La decisión es de ustedes. Sus condiciones mínimas serían:
- la tumba, fuera de la vista de la casa;
- el puente, solo sobre agua de verdad;
- la pagoda, solo como invernadero dentro de una escena exótica aparte.

Para la roca en terreno llano no da ninguna versión aceptable.

**Dos avisos sobre su copia:**
- Las láminas que cita no vienen en el texto que me pasaron; están en el atlas del libro.
- La p. 66, donde sigue la escena campestre de la ferme ornée, salió ilegible en el OCR, así que no sé qué más dice ahí.

## C5b

Si siguen el capítulo IV, la mayor parte de la lista no encaja. Boitard pone por encima de todo la regla de las *convenances*, la armonía con el lugar, con la época y con las costumbres de quien vive ahí. Para él, una huerta de granja, llana, sin agua y que se ve entera desde el comedor tiene que ser una escena rústica. De lo que quieren, solo la cabaña encaja del todo.

## Las tres razones de fondo
- **Terreno llano.** "Conservez à la plaine le caractère de la plaine" (p. 50). Para la llanura recomienda la *ferme ornée* o algo "d'un genre doux et gracieux". Dice que ahí no hay que intentar nunca "une grande composition pittoresque", porque el resultado es monótono, "surtout si vous n'avez pas d'eau" (p. 51).
- **La casa es lo principal.** La vivienda tiene que ser siempre el centro de la escena principal (p. 55). Vivir en una choza y tener un templo de adorno le parece más ridículo que lo contrario. Una pagoda, un puente veneciano y una tumba etrusca alrededor de una casa de granja caen en ese error.
- **Todo se ve desde la ventana.** Acepta mezclar estilos en un jardín grande, en escenas separadas, con contrastes usados "avec sobriété" (p. 55). Cinco construcciones de cinco estilos distintos, vistas todas juntas desde la ventana, son justo lo contrario.

## Pieza por pieza

**Roca: no.** Es la condena más clara del capítulo: "Gardez-vous bien de ces roches factices, monceaux de pierres ridicules, qui semblent tombées du ciel au milieu d'un gazon" (p. 50). En la p. 60 acepta "une simple rocaille" en escenas pintorescas, pero para la llanura no deja lugar a dudas.

**Puente veneciano y estanque: no.** En el capítulo, todas las escenas con agua (el arroyo, el estanque con la cabaña del pescador, el molino) cuentan con agua de verdad. Además pide que los adornos estén "dans une position motivée", es decir, que tengan un motivo para estar ahí (lo dice de jarrones y estatuas, p. 71). Esto ya no es de Boitard, es mío: llenar un estanque a baldes desde la bomba le quita al peón el tiempo de regar la huerta, y en verano el agua se estanca o se seca. Si algún día tienen agua, él habla de "un pont rustique" (p. 60), no de uno veneciano.

**Tumba etrusca: no en la huerta.** Para Boitard la tumba es "la fabrique la plus éminemment mélancolique". Hay que ponerla donde "ne puisse être aperçu d'aucune partie du bâtiment, et même des principales poses du jardin" (p. 69), es decir, donde no se vea desde la casa ni desde los puntos principales del jardín. Además pide:
- un valle solitario;
- una pequeña loma junto a un arroyo tranquilo, o una isla;
- un ciprés y un sauce llorón;
- árboles oscuros que cierren la vista (pp. 67–68).

Cuenta que Luis XV abandonó Saint-Germain para siempre por haber visto desde la terraza el campanario de Saint-Denis, donde se entierra a los reyes. Si la quieren igual, lo único coherente con el texto es un rincón de la granja que no se vea desde la casa. Sobre el estilo etrusco, el capítulo no dice nada.

**Pagoda china: no.** Aparece una sola vez, como disfraz de un invernadero: "une serre chaude à laquelle vous donnerez l'aspect d'une pagode" (p. 65). Pertenece a la escena exótica, que pide:
- plantas de invernadero y de orangerie, con las macetas enterradas;
- un lugar cálido y protegido del viento;
- que a lo lejos "rien ne doit rappeler l'Europe", o sea, tapar todo lo que se vea normando.

Encima, solo luce cuatro o cinco meses al año. Él mismo dice que es "tout-à-fait opposé à la scène rustique" (p. 62). Con poca plata y la granja a la vista, no funciona.

**Cabaña: sí.** Es la escena rústica tal cual (pp. 60–62). Su carácter "est dans l'utile", con "peu d'accidens" en el terreno y "point d'ambition dans les plantations". Y añade que "la cabane rustique est le résultat d'une honnête pauvreté et de l'économie". La describe así:
- una casita con techo de paja;
- una puerta de ramas entrelazadas o de palos con su corteza, y una empalizada del mismo material alrededor;
- muebles rústicos;
- un peral, un manzano o un cerezo que dé sombra a un banco de piedra junto a la puerta, y una parra alrededor de las ventanas;
- animales: el perro en un tonel que le sirve de caseta, una oveja, una cabra.

Insiste en "soyez toujours naturel", así que conviene que la cabaña sirva para algo de verdad: herramientas, semillas, un lugar para sentarse. Si guarda animales, que estén como los tendría un granjero. Si tienen las láminas que cita, les sirven de modelo: pl. 67 para las puertas, 69 para los muebles, 70, 71 y 73 para las empalizadas, y 90, fig. 4, para el tonel del perro.

**El tilo "caído por un rayo".** El capítulo no habla de simular rayos, pero lo que sí dice va en contra. Los efectos terribles tiene que darlos "la nature seule" (p. 59), y en lo pintoresco el riesgo es "tomber dans le bizarre en cherchant l'original" (p. 60). Además lo tendrían delante en cada comida. Hay dos opciones que sí encajan con el texto:
- **Dejar el tronco en pie**, si alguien que sepa confirma que aguanta, y dejar que lo cubra la hiedra o una clemátide. Un tronco viejo y hueco cubierto de hiedra figura entre sus efectos pintorescos fáciles de reproducir (p. 60).
- **Tumbarlo como lo haría un granjero** y usar la madera en el jardín: los palos con corteza para la puerta, la empalizada y los muebles de la cabaña. En su lugar pueden plantar un manzano o un peral, que en Normandía es lo natural.

Esto ya no es de Boitard: tumbar un árbol grande y casi muerto es un trabajo peligroso para un solo peón, así que conviene contratar a alguien con experiencia.

## En resumen
Para Boitard, su huerta ya es la escena que corresponde: lo rústico es "un produit de l'art, où la main de l'homme se montre partout". El plan barato y que un solo peón puede llevar adelante:
- mantener las legumbres y los frutales como protagonistas;
- sumar la cabaña con su empalizada;
- poner el banco bajo un frutal, la parra y algunos animales;
- resolver el tilo con una de las dos opciones de arriba.

Boitard también dice que hay que complacer al dueño, pero "quand le bon sens vous le permettra" (p. 53). La decisión es de ustedes, aunque esta lista choca con casi todo lo que defiende el capítulo.
