from datetime import datetime
import sqlite3

def siguiente_turno(db, id_casa):
    # Obtener historial de lavados de la casa
    cursor = db.cursor()
    cursor.execute("SELECT id_usuario, turno FROM lavados WHERE id_casa = ?", (id_casa,))
    registros = cursor.fetchall()

    # Contar cuántas veces lavó cada usuario en mediodía y noche
    turno_contador = {}
    for reg in registros:
        usuario = reg['id_usuario']
        turno_valor = reg['turno']
        if usuario not in turno_contador:
            turno_contador[usuario] = {'mediodia':0, 'noche':0}
        turno_contador[usuario][turno_valor] += 1

    # Seleccionar usuario con menos lavados totales
    min_lavados = None
    elegido = None
    for usuario, cont in turno_contador.items():
        total = cont['mediodia'] + cont['noche']
        if min_lavados is None or total < min_lavados:
            min_lavados = total
            elegido = usuario

    return elegido  # id del usuario que le toca
