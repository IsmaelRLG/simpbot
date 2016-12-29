# -*- coding: utf-8 -*-


sample = """
;EJEMPLO: CONFIGURACIÓN DEL SERVIDOR

[user]
nick = SimpBot                ; Nombre de nick
user = ircbot                 ; Nombre de usuario

;[nickserv]
;sasl = no                    ; Indica si se usará SASL
;username = SimpBot           ; Usuario de NickServ
;password = *******           ; Contraseña de Nickserv

[server]
network = Freenode            ; Nombre de la red
address = chat.freenode.net   ; Dirección del servidor
port = 6667                   ; Número de puerto
password =                    ; Contraseña del servidor

[simpbot]
autoconnect = yes             ; Conectar automáticamente
prefix = $-                   ; Prefijo de SimpBot
wtime = 15                    ; Tiempo para reconectar
msgps = 0.5                   ; Mensajes por segundo
timeout = 240                 ; Tiempo fuera de la conexión
default_lang = es_UN          ; Lenguaje por default

[database]
chanregister = request        ; Registro de canales
userregister = allow          ; Registro de usuarios
;maxusers = 20                ; Máximo de usuarios en base de datos
;maxchans = 20                ; Máximo de canales en base de datos
"""