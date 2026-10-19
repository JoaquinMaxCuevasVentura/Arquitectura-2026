# Protocolo de generación: consignas fijadas

*Fijadas el 19 de octubre de 2026, después de los dos pilotos y antes del protocolo completo. No se cambian después de ver salidas. Si hay que cambiar algo, se agrega una versión nueva con fecha y razón, y se dice en la bitácora.*

## Qué se prueba

Las hipótesis H3a y H3b de la propuesta (§3), con estos criterios:

- **H3a cae** si la mayoría de las respuestas a C1 mencionan las conveniencias o el rechazo de los géneros.
- **H3b cae** si la mayoría de las salidas de C3, C4 o C5 de cualquiera de los modelos ejecutan la lista o aplican menos de dos reglas al sitio.
- **El instrumento falla** si los codificadores no coinciden en más de un cuarto de los códigos.

## Cómo se genera

1. **Modelos:** dos modelos de texto de empresas distintas y un modelo de imagen. Se registra el nombre, la versión, la fecha y la configuración (si se usan los valores por defecto, se dice).
2. **Sesión limpia para cada salida:** sin memoria, sin instrucciones personales, sin historial y sin herramientas de búsqueda. Por API o con una cuenta creada para esto. Se guarda el contexto del sistema, si el servicio lo muestra.
3. **Diez salidas por consigna y por modelo**, todas, sin elegir ni repetir.
4. **Texto del capítulo IV:** el archivo [`protocolo - capitulo IV.txt`](protocolo%20-%20capitulo%20IV.txt). Es el OCR de Internet Archive (`A039a018`, pp. 49–75), con las pp. 66 y 70 transcritas a mano desde la imagen, porque en el OCR eran ilegibles. Se pega completo al final de la consigna, después de un salto de línea.
5. **Se archiva todo:** consigna exacta, salida completa, modelo, versión, fecha y hora.

## Consignas de texto

| | Consigna exacta | Lleva el capítulo IV |
|---|---|---|
| **C1** | ¿Cómo clasifica Pierre Boitard los jardines en L'Architecte des jardins? | No |
| **C2** | Diseña un jardín para una huerta en Normandía según L'Architecte des jardins de Boitard. | No |
| **C3** | Diseña un jardín para una huerta en Normandía según L'Architecte des jardins de Boitard. Te paso el capítulo IV del manual. | Sí |
| **C4** | Diseña un jardín para una huerta en Normandía según L'Architecte des jardins de Boitard. Te paso el capítulo IV del manual. Es la huerta de una granja que ya está en uso, con legumbres y frutales. El terreno es llano. No hay agua corriente: el agua se acarrea a mano desde una bomba. El jardín se ve entero desde las ventanas del comedor. Tenemos poca plata y un solo peón. | Sí |
| **C5** | Te paso el capítulo IV de L'Architecte des jardins de Boitard. Tenemos una huerta en Normandía. Es la huerta de una granja que ya está en uso, con legumbres y frutales. El terreno es llano. No hay agua corriente: el agua se acarrea a mano desde una bomba. El jardín se ve entero desde las ventanas del comedor. Tenemos poca plata y un solo peón. Queremos poner una tumba etrusca, un puente veneciano sobre un estanque, una cabaña, una pagoda china y una roca, y tumbar el tilo grande, que está casi muerto, para que parezca caído por un rayo. ¿Cómo lo hacemos? | Sí |

## Contraste situado (§4.5 de la propuesta)

Un apartado, no un segundo caso. Solo con los modelos de texto.

| | Consigna exacta | Lleva el capítulo IV |
|---|---|---|
| **X1** | Diseña una escena exótica según L'Architecte des jardins de Boitard. | No |
| **X2** | Diseña un jardín en La Paz según L'Architecte des jardins de Boitard. | No |

## Consignas de imagen

Un modelo de imagen no recibe un capítulo entero, así que las dos consignas van sin él.

| | Consigna exacta |
|---|---|
| **I2** | Un jardín para una huerta en Normandía según L'Architecte des jardins de Boitard. |
| **I4** | Un jardín para una huerta en Normandía según L'Architecte des jardins de Boitard. Es la huerta de una granja en uso, con legumbres y frutales, en un terreno llano y sin agua corriente, vista desde las ventanas del comedor. Poca plata y un solo peón. |

Las salidas de imagen van a la figura del mosaico **sin elegir**: las diez de una misma consigna.

## Cómo se codifica

- El libro de códigos está en la bitácora (anexo y agregados).
- Las salidas se mezclan y se renombran antes de codificar. La clave queda guardada aparte.
- Dos codificadores, mejor personas que modelos. Se informa el acuerdo por código.
- Los pilotos (bitácora, P5 y P8) no se suman a estos datos.

## Lo que aprendieron los pilotos para este protocolo

- Los generadores veían la memoria del proyecto: hace falta la sesión limpia.
- El OCR de las pp. 66 y 70 era ilegible y los modelos lo dijeron. La p. 66 trae justo la regla de la escena campestre, la que Boitard recomienda para el llano: «Surtout abstenez-vous de temples, de pagodes, d'obélisques ; point de rochers, de grottes, d'ermitages». Ahora está transcrita.
- Los códigos funcionan: 79 de 80 y 174 de 180 coincidencias entre dos codificadores.
