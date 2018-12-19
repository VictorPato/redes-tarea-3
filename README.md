# Tarea 3 CC4303-Redes

Tarea 3 del curso de Redes.

## Integrantes

* Pedro Belmonte
* Víctor Garrido

## Cómo correr la tarea

La tarea fue resuelta en Python 3, para Ubuntu x64. A continuación se indica cómo correrla.

La ejecución es casi idéntica al ejemplo del enunciado, pero se debe indicar además un atributo nuevo llamado "type" con valor "d" para indicar que el paquete contiene datos y no una tabla de ruta (type "t"). Se recomienda ejecutar cada línea por consola y no programáticamente de manera de poder enviar varios paquetes a la red sin problemas y ver los mensajes de logging más fácilmente.

```
$ from topology import start, stop
$ from send_packet import send_packet
$ import json
$ routers = start('topology.json')
$ send_packet(12345, json.dumps({'type': "d", 'destination': "Router#3", 'data': "Saludos"}))
$ stop(routers)
```

El logging ya no se muestra en la consola sino que se crea un archivo "logs.txt" con los logs de cada evento. Además se modificaron los logs para que fueran más explicativos.
