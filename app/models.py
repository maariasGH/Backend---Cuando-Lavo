import sqlite3
from flask import g, current_app # type: ignore

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            timeout=10  # espera hasta 10 segundos si está lockeada
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db(app):
    db_path = app.config['DATABASE']
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Crear tablas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS casas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                id_casa INTEGER,
                FOREIGN KEY(id_casa) REFERENCES casas(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lavados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_casa INTEGER,
                id_usuario INTEGER,
                fecha DATE,
                turno TEXT,
                detalles TEXT,
                FOREIGN KEY(id_casa) REFERENCES casas(id),
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            )
        ''')
        conn.commit()


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()