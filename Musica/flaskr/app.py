"""
Autor: Saúl Flores Benavente
Fecha-última_modificación: 08-04-2020
Modulo principal de la aplicación
Contiene el main y es el módulo a ejecutar para lanzar la aplicación
"""

import os
from flaskr.app_content import APP

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=os.environ['PORT'])
