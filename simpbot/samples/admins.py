# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

samples = """
; Los administradores globales se definen como:
;    [global <nombre de la cuenta>]
; Los administradores locales se definen como:
;    [local <nombre de la red> <nombre de la cuenta>]
; Estos debe contener los siguientes valores:
;  password......... La contraseña cifrada con algún algoritmo hash.
;  timeout.......... El tiempo en el cual expirará la sesión administrador, este
;                    valor debe ser mayor a cero (0), se se fija como valor cero
;                    se considera como indefinido por lo que la sesion nunca
;                    expirará.
;                    Se recomienda fijar este valor como medida de seguridad.
;  maxlogins........ Máxima cantidad que podra iniciar sesión, si se le fija
;                    como valor "0", se considera como indefinido.
;                    Se recomienda fijar este valor como medida de seguridad.
;  verbose.......... Habilita o inhabilita las notificaciones, debe ser indicado
;                    como "yes" (sí) o "no" (no).
;  capability....... Define las capacidades que poseerá el administrador, estos
;                    pueden ser (opcionales):
;                     - global ó root: Administrador que cuenta con todas las
;                       capacidades y privilegios en el bot.
;                     - local ó admin: Administrador que cuenta con la mayoría
;                       de capacidades y privilegios en el bot.
;                     - semi-admin: Administrador con parciales capacidades y
;                       privilegios en el bot.
;                     - helper: Administrador con bajos privilegios y
;                       capacidades en el bot, éste es considerado como ayudante
;                    Se puede añadir varias capacidades separadas por comas (,).
;                    Para mas información sobre las capacidades disponibles ver
;                    la documentación.
;  account.......... Nombre de la cuenta de usuario que usará el administrador.
;                    Se recomienda fijar este valor como medida de seguridad.
;                    Este valor es opcional; se pueden añadir varias cuentas
;                    separadas por comas (,).
;  isonick.......... Nombre del nick ó canal para las notificaciones.
;                    Este valor es opcional; se pueden añadir varios nicks ó
;                    canales separandolos por comas (,).
;  hash_algorithm... Nombre del algoritmo hash para el valor "password", de no
;                    indicar el algoritmo se usa por default MD5.

[global root]
password = 03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4
timeout = 2419200
maxlogins = 1
verbose = yes
capability = global
account = account_name
isonick = nickname,#channel
hash_algorithm = sha256

[local network account]
password = 81dc9bdb52d04dc20036dbd8313ed055
timeout = 2419200
maxlogins = 0
verbose = yes
capability = semi-admin
isonick =
"""