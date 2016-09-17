# Creacion de modulos
Para programar funciones, se realiza exclusivamente con funciones
estas deben contener, obligatoriamente ciertos argumentos, los cuales
son los siguientes:

    irc, ev, result, target, channel, _

-------------------------------------------------------------------
### Argumento: `IRC`
Clase para interactuar con el irc, sus atributos destacados son:

    irc.ctcp        | Envia un ctcp a un usuario/canal
    irc.ctcp_reply  | Responde a un ctcp
    irc.join        | Ingresa el bot a un canal
    irc.kick        | Expulsa a un usuario de un canal
    irc.nick        | Cambia el nick del bot
    irc.notice      | Envia un mensaje "notice" a un canal/usuario
    irc.msg         | Envia un mensaje estandar a un canal/usuario
    irc.privmsg     | Envia un mensaje a un canal/usuario
    irc.part        | hace que el bot salga de un canal
    irc.verbose     | Envia un mensaje a todos los administradores
    irc.error       | Envia un mensaje de error a un canal/usuario
    irc.remove      | Remueve a un usario de un canal
    irc.topic       | Cambia el topic de un canal
    irc.user        | Define el usuario (unicamente al loguearse)
    irc.quit        | Desconecta al bot del IRC
-------------------------------------------------------------------
### Argumento: `ev`
Contiene la informacion del evento, se llama de la siguiente forma:

```python
ev('valor')
```
Los valores son los siguientes:

    nick    | Nombre del nick
    host    | Nombe del host
    user    | Nombre del usuario
    target  | Punto donde ingreso el mensaje
    message | Mensaje completo del evento
-------------------------------------------------------------------
### Argumento: `result`
Contiene los resultados de la busqueda en el texto (definido por el
programador)



```python
import simpbot

@simpbot.commands.addCommand('expresion regular')
@simpbot.commands.admin
def nombre_de_ejemplo_1(irc, ev, result, target, channel):
    # irc -> Clase que contiene  funciones de irc
    # ev('nick') -> Nick del usuario
    # ev('host') -> Host del usuario
    # result -> Resultado de la expresion regular
    # Target -> Blanco donde se deberia responder
    # Channel -> Canal donde se produjo la llamada
    
    # Se envia un mensaje, en donde se invoco el bot Canal/Privado
    irc.privmsg(target, 'Mensaje de prueba')

    # Se envia un mensaje siempre en privado
    irc.privmsg(ev('nick'), 'Otro mensaje de prueba')


