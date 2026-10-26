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
- **Resultado** ([ronda 1](resultados/ronda1.md)): σ = 1,12 MPa (peso propio) + 8,79 MPa (P) = **9,9 MPa**, frente a un límite de 2,3. Ni el mármol más resistente (5 MPa) la salva. La barra solo admite 138 N en el centro, el peso de una olla grande.
- **Contraste**: se cumple lo que anticipaban Kessler (F13) y Semper (F07). La frase del borrador dice que la piedra sostiene, pero **la piedra no puede sostenerse ni a sí misma con una carga de uso**.
- **Decisión**: **descartar V0 tal como está**. Para salvar la idea, la madera tiene que cargar la piedra: eso da V0b (ronda 2). Siguiente acción: probar V0b.

## E2 · La madera se mueve y la piedra no
- **Pregunta**: ¿qué holgura necesita cada unión piedra-madera para el rango de humedad 4-13 %? ¿Alguna exige encolar piedra a contraveta?
- **Decisión que habilita**: cómo se fija la piedra (asentada, acuñada, encolada) y cuánto se ve la junta.
- **Tipo**: cálculo (cambio dimensional lineal, FPL ec. 13-5).
- **Prerregistro**: si una unión necesita encolado a contraveta o una holgura > 3 mm por lado, **esa unión se rediseña**. Si en V2 la holgura deja el montante suelto en la caja y hay que acuñarlo, entonces **«hincar» deja de ser la acción** (pasa a ser encajar y acuñar) y V2 pierde su razón de ser.
- **Qué no demuestra**: la velocidad del cambio, los gradientes dentro de la pieza (abarquillado) ni la pieza concreta (radial o tangencial).
- **Resultado** ([ronda 1](resultados/ronda1.md), [ronda 2](resultados/ronda2.md)):
  - El tablero de 1000 mm cambia **13,7 mm** entre 6 y 11 % de humedad, y 24,7 mm entre los extremos de 4 y 13 %. Eso afecta a todas las versiones.
  - **V0**: si las mitades se fijan por el borde exterior, la junta junto a la piedra varía hasta **10,4 mm por lado** (✗). Si se fijan junto a la piedra, casi no cambia: el cálculo no condena a V0 por esto, sí obliga a fijarla de ese modo.
  - **V2**: la caja necesita **1,8 mm de holgura por lado** para que el montante no la abra al hincharse, y en seco la junta llega a **3,2 mm** (✗). Para que el montante no quede suelto hay que acuñarlo.
  - **V1**: la caja de la llave varía 0,25 mm por lado (✓).
  - **V0b**: el canal varía de 0,9 a 2,0 mm por lado (✓) si la piedra **se asienta sin cola**.
  - **V4**: el agujero del collar pide 0,6 mm de holgura por lado en alto (1,1 mm en seco) (✓).
- **Contraste**: ninguna versión necesita encolar piedra a contraveta, siempre que la piedra no se pegue. El prerregistro decía: «si en V2 hay que acuñar el montante, hincar deja de ser la acción». **Se cumple.**
- **Decisión**: V2 pierde su razón de ser (ver también E4). En todas, la regla es **piedra asentada o apretada, nunca pegada**.

## E3 · ¿El lastre estabiliza?
- **Pregunta**: ¿cuánto aumenta la piedra la carga necesaria para volcar la mesa (vertical en el extremo y en el borde largo; horizontal en el tablero)? Y ¿el peso resiste el balanceo (*roulement*, F10)?
- **Decisión que habilita**: si «la piedra estabiliza» puede seguir en el concepto.
- **Tipo**: cálculo (equilibrio de momentos sobre la arista de vuelco) más un argumento de estática para el balanceo.
- **Prerregistro**: si la mesa **sin piedra** ya resiste ≥ 2 × la carga de referencia en todos los casos y la piedra aporta < 25 % adicional, **la frase «la piedra estabiliza» se retira del concepto**: es cierta, pero no importa. Para el balanceo, la hipótesis es que **el peso no aporta nada** en un armazón articulado. Si el modelo muestra lo contrario, se revisa.
- **Qué no demuestra**: el comportamiento dinámico (golpes) ni el deslizamiento sobre el suelo.
- **Resultado, ronda 1** (caballete a 450 mm del extremo, pie de 80 mm):
  - **Ninguna versión** resiste 2 P en el extremo sin piedra. V1, V2 y V3 llegan a 1,65 P; V0, a 1,37 P.
  - La piedra de V0 suma **+40 %**, y aun así se queda en **1,93 P**: no llega. La de V2 suma +71 %. Las de V1 y V3, +1 % y 0 %.
  - El empuje horizontal nunca vuelca la mesa: **se desliza antes**, con rozamiento de 0,4.
  - Lo que sí resuelve el vuelco es la **geometría**: alargar el pie 50 mm hacia el extremo (pie simétrico de 180 mm) o llevar el caballete a ≤ 400 mm del extremo.
- **Contraste con el prerregistro**: la condición para retirar la frase era «sin piedra ya ≥ 2× y piedra < 25 %». **No se cumplió en la ronda 1**: la mesa sin piedra no llegaba a 2×, y la piedra de V0 sí aportaba mucho. Hay que decirlo así: en la geometría de partida, **el lastre sí estabilizaba**. Pero la corrección geométrica estabiliza más, y sirve también para la madera sola.
- **Resultado, ronda 2** (corrección común: pie de 180 mm): sin piedra, V3, V0b y V4 resisten 2,1-2,2 P. La piedra de V0b aporta **+16 %** y la de V4 +5 %. **Se cumple la condición: se retira «la piedra estabiliza»** para V0b y V4.
- **Balanceo** (*roulement*, F10): en un armazón articulado, el peso no da rigidez lateral; una carga vertical mayor solo agranda el efecto del desplome (P-Δ). Por eso el instrumento no le asigna al peso ninguna resistencia al balanceo, y la llave (E4) es la que la da. Es un argumento de estática, no una medición.
- **Decisión**: (1) **corrección común**: pie de 180 mm en todas las versiones, para no acercar el caballete a las cabeceras y quitar sitio a las rodillas; (2) **la frase del borrador sale del concepto**. El peso estabiliza, pero lo mismo pasa con cualquier masa, y la geometría lo hace mejor.

## E4 · ¿La piedra de la unión trabaja a compresión? (V1, V3, V2)
- **Pregunta**: en V1, ¿qué tensión de flexión tiene la llave de piedra con la tracción T que el balanceo produce en la espiga? ¿Qué tamaño mínimo de llave cumple K2? En V2, ¿qué tensión tienen las paredes de la caja? En ambas: ¿puede el peso propio mantener asentada la llave?
- **Decisión que habilita**: si V1 o V2 pueden conservar la piedra en la unión y con qué proporciones. Esas proporciones definen su **presencia visual**.
- **Tipo**: cálculo (pórtico simplificado para T; llave como viga corta; pared de la caja como ménsula).
- **Prerregistro**:
  - V1: si la llave de 28 × 20 supera 2,3 MPa, se agranda **solo si el tamaño mínimo cabe** en la espiga sin debilitarla (ancho de la llave ≤ ½ del espesor de la espiga; profundidad ≤ ⅓ del vuelo de la espiga). **Si no cabe, la piedra no puede ser una llave que trabaje a flexión** y hay que buscar una unión donde trabaje a **compresión pura**.
  - V2: si las paredes de la caja superan 2,3 MPa, o la pieza pesa > 25 kg, V2 se descarta o se rediseña.
  - Gravedad: si el peso de la llave no basta para mantenerla asentada contra el empuje de la propia cuña, la frase «el peso traba» también se retira.
- **Qué no demuestra**: el ajuste real, el astillado de aristas ni la percepción. Eso es E6.
- **Modelo** (ver [`../instrumentos/README.md`](../instrumentos/README.md)): un empuje H en el tablero produce en cada unión travesaño-montante un momento que se resiste con un par entre el hombro del travesaño y la llave. Brazo: la mitad de la altura del travesaño. **Modelo b**: el momento se reparte con las uniones montante-cabezal; T ≈ 1020 N. **Modelo a**: solo resisten las uniones del travesaño; T ≈ 2045 N. Es simple a propósito: sirve para comparar, no para dimensionar.
- **Resultado** ([ronda 1](resultados/ronda1.md)):
  - **V1, llave de mármol**: 8,3 MPa (modelo b) y 16,6 MPa (modelo a), frente a un límite de 2,3. Necesitaría una profundidad de **53-75 mm**, y en la espiga caben **37 mm**. **No cabe.**
  - **V3, llave de fresno** (control): 8,3 MPa frente a un límite de 34,3. Le bastan **14-19 mm**. Cabe con holgura.
  - **V2, paredes de la caja**: 1,4 MPa (b) cumple; 2,9 MPa (a) no. **No es robusto.** Además, el pie de piedra pesa 28,6 kg (> 25).
  - **Gravedad**: el peso de la llave de piedra es el **0,6 %** del rozamiento que la sostiene, así que **el peso no traba**.
- **Contraste**: se cumple la rama del prerregistro: «si no cabe, la piedra no puede ser una llave que trabaje a flexión → buscar una unión a **compresión pura**». El control V3 muestra además que **la madera hace mejor el trabajo de llave**.
- **Decisión**: **descartar V1** (la piedra como llave) y **V2** (piedra hincada: no es robusta, pesa demasiado y la acción ya no es hincar). Se retira «el peso traba». Se deriva **V4 (collar)**: la espiga atraviesa un bloque de piedra y la llave de fresno lo aprieta contra el montante. La piedra queda **solo a compresión**. Siguiente acción: ronda 2.
- **Resultado, ronda 2** ([ronda 2](resultados/ronda2.md)):
  - **V4**: compresión en el collar de 0,08 MPa (b) y 0,17 MPa (a), frente a 18 MPa de diseño.
  - **Qué aporta la piedra**: el apoyo de la llave sobre el montante baja de 0,64 a 0,08 MPa. Es un trabajo real (una placa de apoyo, como una basa bajo un poste), pero **la madera no lo necesita**: resiste 2,3 MPa.
- **Decisión, ronda 2**: V4 es **la única versión con piedra que cumple K1-K4**, y lo hace con la piedra trabajando como piedra. Pero el control V3 cumple lo mismo sin piedra. **La piedra no se justifica por la estructura en ninguna versión.** Si se queda, tiene que justificarse por lo que E6 responda: percepción, montaje y el sentido que le da la fuente (F01: la piedra fija donde se ata la madera). Si no, sale.

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

## E8, E9, E2b, E10 · Ensayos de la propuesta B
El prerregistro está en [`../03_proponer/propuesta_B.md`](../03_proponer/propuesta_B.md#prerregistro-de-los-ensayos-propios-de-b-antes-de-calcular), escrito antes de calcular. Los resultados van más abajo, en la sección «Propuesta B».

## E7 · Originalidad · *pendiente*
- **Pregunta**: ¿algún ganador de 2017-2018 o algún producto actual de Porada ya resuelve una mesa con unión de piedra?
- **Tipo**: contraste con antecedentes.
- **Prerregistro**: si existe un antecedente directo, **cambia la unión o el argumento**, no solo el aspecto.
