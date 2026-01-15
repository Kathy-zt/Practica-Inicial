**Definiciones:**



**Organization (org):**

* Qué es: Un espacio lógico de trabajo.
* Para qué sirve:

 	Separar proyectos

 	Separar equipos

 	Controlar permisos



🔹 Ejemplo mental:

“Proyecto ranitas”

👉 Nada se guarda sin una organización.



**Token:**

* Qué es: Una llave de acceso (autenticación + permisos).
* Qué define el token:

 	A qué organización puede acceder

 	Qué buckets puede leer/escribir

 	Qué acciones puede hacer



🔹 Importante:

El token NO guarda datos, solo autoriza.

👉 Sin token:

no hay escritura

no hay lectura

no hay conexión



**Bucket**

* Qué es: El contenedor físico de los datos.
* Qué define un bucket:

 	Dónde se guardan los datos

 	Cuánto tiempo se retienen (retention policy)

🔹 Ejemplo mental:

“ranitas\_bucket” = disco donde viven las mediciones

👉 Todos los puntos terminan dentro de un bucket.



**Measurement**

* Qué es: El tipo de dato que estás guardando.

🔹 Ejemplo:

ranitas

temperatura

humedad

👉 En tu caso:

measurement = "ranitas"



**Point (el dato real)**

Un Point es UNA observación en el tiempo.



Internamente tiene:

Point =

{

  time,

  measurement,

  tags,

  fields

}



 	a) **Time (timestamp)**

 	InfluxDB lo agrega automáticamente si no lo indicas

 	Es la base de todo el sistema



 	b) **Tags (metadatos)**



 	🔹 Son:

 	texto

 	indexados

 	sirven para filtrar y agrupar



 	🔹 En tu proyecto:

 	tipo = verde / azul / roja

 	👉 Los tags no se promedian, se usan para clasificar.



 	c) **Fields (valores medidos)**



 	🔹 Son:

 	números

 	datos reales

 	lo que se analiza









https://www.youtube.com/watch?v=GLE71pIHUU8



https://www.youtube.com/watch?v=B0UiboKrgEI



https://www.youtube.com/watch?v=8iXZTS7f\_hY\&list=PLS1QulWo1RIYkDHcPXUtH4sqvQQMH3\_TN



https://www.youtube.com/watch?v=7i9VRJoeoOg



https://www.youtube.com/watch?v=rSsouoNsNDs\&list=PLYt2jfZorkDqZiH\_ahojNIxI0ikPCTbYP

