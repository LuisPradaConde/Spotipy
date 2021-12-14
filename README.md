
# Componentes del Grupo 

+ Pablo Santos Cabaleiro    - p.santos.cabaleiro@udc.es
+ Luis Prada Conde          - luis.prada@udc.es
+ Borja Alonso Sobral       - borja.alonso.sobral@udc.es


## Descripcion del Proyecto 
Este proyecto permite unas serie de funcionaliades relacionadas con la música, concreamente [Spotify].  El API es realmente útil, pero hemos optado por el uso de la API [Spotipy] que es una adaptación a Python de la propia API que se encarga de la gesion de las peticiones al API . Nuestro proyecto permite, entre otras cosas, obtener informacion sobre diferentes artistas, canciones, podcast albums... así como informacion personalizada de la propia cuenta de spotify mostrando las canciones guardadas, artistas seguidos, las playlist del usuario, canciones más escuchadas ...  
Además, consideramos que es útil obtener más informacion en el caso de los artistas por lo que tanto de [Wikipedia] como de [Google News] como la de Wikipedia nos permiten mostrar en nuestro Proyecto una mayor información al ususario. Si con esto no fuera suficiente, añade tambien la posibilidad totalmente nueva en este tipo de aplicaciones como es la de  mostrar la letra de las canciones, la cuál hemos extraído del API de la famosa página de letras de canciones [Genius]. 


## Funcionalidades añadidas y actualizadas
Además de las comentadas en la primera interaccion, hemos añadido diferentes funcionalidades nuevas hacen que el proyecto sea más completo y funcional. Estas funcionalidades son: 
+ Navegacion entre los distintos resultados que nos ofrece el API (mostramos la máxima informacion que el API nos devuelve (navegacion entre distitnos resultados que devuelve la búsueda de una cancion por nombre, albums, artistas ... )) 
+ Editar el nombre y descripcion de una playlist
+ Ver noticias relacionadas del Artista 
+ Comprobar si el usuario sigue una playlist/cancion/podcast/artista
+ Ver albums del artista y ordenar esos albums por distintos parámetros a elegir
+ Ordenar canciones de un album 
+ Dejar de seguir un album 
+ Ver letra de una cancion
+ Ver si una cancion es explícita (aparece un icono cara de enfadada al lado del nombre )
+ Ver episodios e informacion de un podcast


## Uso de Pandas
Pandas ha sido nuestra base para trabajar con los datos. Lo hemos utilizado para moldear a nuestro gusto los datos que nos devolvían los distintos tipos de peticiones que hemos hecho a los APIs. Esta informacion (json) la hemos pasado a un dataframe y posteriormente con .to_html() a los templates del proyecto. 
A partir de ahi hemos modificado los dataframes para mostrar la informacion que deseábamos así como para ordenarlos, agruparlos por una columna concreta, modificar valores como columnas y otros distintos datos o mostrar alguna gráfica con los datos. 


## Errores conocidos y otros aspectos 
+ En local, al hacer logout abre en una nueva pestaña y deslogea la cuenta para poder iniciar sesion con otro usuario de spotify, pero cuando ejecutamos el proyecto en el contenedor no abre la pestaña y no desloguea la cuenta. 

+ Al eliminar canciones de la playlist, puede que no encuentre la cancion que queremos eliminar si es un título poco conocido por lo tanto no la borra de la playlist. En cambio, en el caso de añadirla, como nos movemos en los distintos resultados que nos da el api si la encuentra. Por lo tanto no la elimina si no la encuentra.

+ En la funcionalidad de editar playlist, el api no permite cambiar el nombre ni la descripcion de la playlist cuando introducimos un espacio en cualqueira de estos dos campos. 

+ Por error del API, a veces, devuelve objetos que en teoría son canciones (por ejemplo de una playlisy) pero que su contenido es null, por lo tanto en estos casos no podemos mostrar dicha informacion. 

+ El API de las noticias permite pocas peticiones por hora, por lo que tras realizar un par de peticiones donde se llame a este API, no devuelve nada. Tras esperar un tiempo vuelve a funcionar otro corto periodo de tiempo hasta que se agotan las peticiones disponibles

+ El API de Google News a veces muestra noticias y resultados que no tienen que ver por culpa de que el nombre del artista es poco conocido, y debido a eso muestra noticias de otras personas, por lo lo que la informacion que nos ofrece este API en determinadas ocasiones no es tan precisa como nos gustaría. 

+ Los test para la aplicacion, concretamente para las APIS de Genius, Wikipedia y Google News no hemos sabido que comprobar ni como, pues los resultados que nos devuelven pueden cambiar con el tiempo y los test saldrían erroneos. Del mismo modo las test del API de Spotipy son bastante simples por el mismo motivo y algunas funcionalidades sabemos que funcionan bien porque conocemos la informacion que debe devolver de antemano, pero no es posible comprobarla en un test. 

## Instrucciones de ejecucion del contenedor 

1. Ejecucion del script: 
 
2. En el navegador local acceder al la ruta 
 ```
 http://localhost:8000/musicapp
 ```


Otro metodo sería ejecutando los siguiente comandos:

```
docker build -t pi-luis-borja-pablo .
```

```
docker run -itd -p 8000:8000 pi-luis-borja-pablo python3 musicpy/manage.py runserver 0.0.0.0:8000
