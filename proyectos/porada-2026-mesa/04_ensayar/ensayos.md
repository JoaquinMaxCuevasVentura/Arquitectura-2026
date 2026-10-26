# Ensayos

Cada ensayo tiene:

- **Pregunta** y la **decisión que habilita**: «¿qué podré decidir después de hacer esto?».
- **Tipo de contraste**: cálculo (instrumento), fuentes, prueba física o juicio de terceros. El tipo dice **qué puede demostrar y qué no**.
- **Prerregistro**: qué resultado obligaría a cambiar y qué se cambiaría. Se escribe **antes** de ver el resultado y queda fijado en el historial de git (commit anterior al del instrumento).
- **Resultado** y **decisión** (conservar, modificar, descartar o cambiar la pregunta), con la siguiente acción.

## Supuestos comunes (fijados antes de calcular)

| Supuesto | Valor | Fuente o razón |
|---|---|---|
| Carga vertical de referencia | **P = 1000 N** en el punto más desfavorable | supuesto: una persona de ~100 kg que se apoya o se sienta en el borde. A contrastar con EN 12521 / EN 1730, no leídas aquí |
| Empuje horizontal de referencia | **H = 300 N** a la altura del tablero | supuesto: empujar o arrastrar la mesa cargada; un golpe |
| Resistencia de diseño | **media / 3**, para madera y piedra | supuesto prudente; Kessler pide «a large factor of safety» (F13) |
| MOR del mármol | **7 a 15 MPa** → diseño con el bajo: **2,3 MPa** | rango típico; Kessler tabla 6 pendiente (F13) |
| Humedad de la madera | fabricación 8 % · mínima 4 % · máxima 13 % | FPL tabla 13-2: extremos de la recomendación para muebles de interior (F11) |
| Coeficiente de cambio dimensional | tangencial (el peor caso): nogal 0,00274 / % | FPL tabla 13-5 (F11) |

---

## E1 · ¿Puede la piedra ser viga? (V0)
- **Pregunta**: la barra de mármol de V0 (160 × 40 mm, luz 1500 mm) ¿soporta su peso más P en el centro sin pasar el umbral K2?
- **Decisión que habilita**: si V0 sigue tal como está o si la madera tiene que cargar la piedra.
- **Tipo**: cálculo (viga biapoyada, flexión elástica).
- **Prerregistro**: si σ > 2,3 MPa, **la barra no puede ser el travesaño**. Entonces o se apoya continua sobre madera (la madera la carga, al revés del concepto), o sale del tablero. Si además σ > 15/3 = 5 MPa, **ningún mármol de catálogo la salva** por cambio de material.
- **Qué no demuestra**: fatiga, vetas o fisuras de la pieza real, impacto.
- **Resultado**: *pendiente*.

## E2 · La madera se mueve y la piedra no
- **Pregunta**: ¿qué holgura necesita cada unión piedra-madera para el rango de humedad 4-13 %? ¿Alguna exige encolar piedra a contraveta?
- **Decisión que habilita**: cómo se fija la piedra (asentada, acuñada, encolada) y cuánto se ve la junta.
- **Tipo**: cálculo (cambio dimensional lineal, FPL ec. 13-5).
- **Prerregistro**: si una unión necesita encolado a contraveta o una holgura > 3 mm por lado, **esa unión se rediseña**. Si en V2 la holgura deja el montante suelto en la caja y hay que acuñarlo, entonces **«hincar» deja de ser la acción** (pasa a ser encajar y acuñar) y V2 pierde su razón de ser.
- **Qué no demuestra**: la velocidad del cambio, los gradientes dentro de la pieza (abarquillado) ni la pieza concreta (radial o tangencial).
- **Resultado**: *pendiente*.

## E3 · ¿El lastre estabiliza?
- **Pregunta**: ¿cuánto aumenta la piedra la carga necesaria para volcar la mesa (vertical en el extremo y en el borde largo; horizontal en el tablero)? Y ¿el peso resiste el balanceo (*roulement*, F10)?
- **Decisión que habilita**: si «la piedra estabiliza» puede seguir en el concepto.
- **Tipo**: cálculo (equilibrio de momentos sobre la arista de vuelco) más un argumento de estática para el balanceo.
- **Prerregistro**: si la mesa **sin piedra** ya resiste ≥ 2 × la carga de referencia en todos los casos y la piedra aporta < 25 % adicional, **la frase «la piedra estabiliza» se retira del concepto**: es cierta, pero no importa. Para el balanceo, la hipótesis es que **el peso no aporta nada** en un armazón articulado. Si el modelo muestra lo contrario, se revisa.
- **Qué no demuestra**: el comportamiento dinámico (golpes) ni el deslizamiento sobre el suelo.
- **Resultado**: *pendiente*.

## E4 · ¿La piedra de la unión trabaja a compresión? (V1, V3, V2)
- **Pregunta**: en V1, ¿qué tensión de flexión tiene la llave de piedra con la tracción T que el balanceo produce en la espiga? ¿Qué tamaño mínimo de llave cumple K2? En V2, ¿qué tensión tienen las paredes de la caja? En ambas: ¿puede el peso propio mantener asentada la llave?
- **Decisión que habilita**: si V1 o V2 pueden conservar la piedra en la unión y con qué proporciones. Esas proporciones definen su **presencia visual**.
- **Tipo**: cálculo (pórtico simplificado para T; llave como viga corta; pared de la caja como ménsula).
- **Prerregistro**:
  - V1: si la llave de 28 × 20 supera 2,3 MPa, se agranda **solo si el tamaño mínimo cabe** en la espiga sin debilitarla (ancho de la llave ≤ ½ del espesor de la espiga; profundidad ≤ ⅓ del vuelo de la espiga). **Si no cabe, la piedra no puede ser una llave que trabaje a flexión** y hay que buscar una unión donde trabaje a **compresión pura**.
  - V2: si las paredes de la caja superan 2,3 MPa, o la pieza pesa > 25 kg, V2 se descarta o se rediseña.
  - Gravedad: si el peso de la llave no basta para mantenerla asentada contra el empuje de la propia cuña, la frase «el peso traba» también se retira.
- **Qué no demuestra**: el ajuste real, el astillado de aristas ni la percepción. Eso es E6.
- **Resultado**: *pendiente*.

## E5 · ¿Sostiene Bertonio «un solo nombre»? (contraste con fuentes)
- **Pregunta**: ¿registra Bertonio (1612) un mismo nombre para las piedras amontonadas y para la piedra hincada?
- **Decisión que habilita**: qué palabra (y qué figura: montón o unión) traduce el proyecto.
- **Tipo**: contraste con la fuente primaria.
- **Nota de honestidad**: este contraste **se hizo durante la recopilación**, antes de escribir este documento, así que **no tuvo prerregistro formal**. Se registra igual porque cambió la pregunta.
- **Resultado**: **son dos entradas**, *Chakhua* (montón) y *Chhakhua* (piedra hincada para atar los palos; también los palos atados) (F01).
- **Decisión**: **cambiar la pregunta**. El proyecto ya no pregunta «¿cómo pesa la piedra sobre la madera?», sino **«¿cómo se une la madera a una piedra fija?»**. V0 (lastre) pierde su apoyo en la fuente; V1 y V2 lo ganan. Siguiente acción: revisar la transcripción de 2011 (p. 330) y corregir la frase del artículo si corresponde (O1).

## E6 · Nodo a escala 1:1 (prueba física mínima) · *pendiente, la haces tú*
- **Pregunta**: en la mano y a la vista, ¿la piedra se lee como **parte de la unión** o como **adorno**? ¿Se astilla al montar? ¿Se arma y se desarma sin herramientas?
- **Decisión que habilita**: la forma y la proporción de la piedra en la unión; si sigue en el proyecto.
- **Tipo**: prueba física y juicio de terceros. Ninguna simulación responde esto.
- **Cómo**: un solo nodo (montante, espiga y llave o collar) en nogal o en una madera dura disponible, y un retazo de mármol de marmolería (F17). Mostrarlo a 5 personas y pedirles, **sin guiarlas**, que digan qué hace cada pieza.
- **Prerregistro**: (a) si 3 de 5 personas lo describen como adorno o perilla, la piedra **cambia de forma o de tamaño, o sale**; (b) si la arista se astilla con un golpe normal de mazo, chaflán o piedra más tenaz; (c) si hace falta herramienta para desmontar, se revisa el escenario «armar la mesa» (F09).
- **Qué no demuestra**: la durabilidad, ni la mesa entera.

## E7 · Originalidad · *pendiente*
- **Pregunta**: ¿algún ganador de 2017-2018 o algún producto actual de Porada ya resuelve una mesa con unión de piedra?
- **Tipo**: contraste con antecedentes.
- **Prerregistro**: si existe un antecedente directo, **cambia la unión o el argumento**, no solo el aspecto.
