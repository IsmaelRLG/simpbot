# -*- coding: utf-8 -*-

help_config = """# -*- coding: utf-8 -*-
#  ____  _  __    _______  ____   ______________
# / ___|(_)|  \  /   ___ \| __ \ / _ \___   ___/
# | |__ | ||   \/   |___||||__||| / \ |  | |
# \___ \| || |\  /|  ____/| __ || | | |  | |
# ___| || || | \/ | |     ||__||| \_/ |  | |
#/____ /|_|| |    |_|     |____/ \___/   |_|
#    Copyright 2016, Ismael Lugo (kwargs)    v%s
#
# EJEMPLO DE CONFIGURACION

                             ###############################
                             #         INFORMACION         #
############################################################
#          USUARIO           # Configuracion de usuario    #
##############################                             #
NICK = "SimpBot"             # Nombre de nick              #
USER = "ircbot"              # Nombre de usuario           #
##############################                             #
#         NICKSERV           # Configuracion de NickServ   #
##############################                             #
USENS = False                # Indica si se usara o no     #
SASL = False                 # Indica si se usara SASL     #
USERNAME = "SimpBot"         # Usuario de NickServ         #
PASSWORD = "*******"         # Contraseña de Nickserv      #
##############################                             #
#         SERVIDOR           # Configuracion del servidor  #
##############################                             #
SSL = False                  # Uso de SSL                  #
PORT = 6667                  # Numero de puerto            #
NETWORK = "Freenode"         # Nombre de la red            #
SERVER = "irc.freenode.net"  # Direccion del servidor      #
SERVPASS = ""                # Contraseña del servidor     #
TIMEOUT = 240                # Tiempo fuera de la conexion #
##############################                             #
#          SIMPBOT           # Configuracion de SimpBot    #
##############################                             #
PREFIX = '$-'                # Prefijo de SimpBot          #
WTIME = 15                   # Tiempo para reconectar      #
MSGPS = 0.5                  # Mensajes por segundo        #
ADMINS = [                   # Host del administrador      #
    'hostname'               #                             #
    ]                        #                             #
CHANNELS = [                 # Canales para el autoingreso #
    '#channel'               #                             #
    ]                        #                             #
VERBOSE = True               # Habilita las notificaciones #
VERBOSENICKS = [             # Nicks para notificaciones   #
    'nickname'               #                             #
    ]                        #                             #
############################################################
"""


def save_conf():
    from . import envvars
    from . import __version__
    with file(envvars.CONFPATH, 'w') as conf:
        conf.write(help_config % __version__)