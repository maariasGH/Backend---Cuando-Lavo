from flask import Blueprint, render_template, request, jsonify, current_app # type: ignore
import sqlite3, datetime
from .models import get_db
from .utils import siguiente_turno

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    if request.headers.get("Accept") == "application/json":
        return jsonify(ok=True, msg="Conexion Establecida con exito ✅"), 200
    else:
        return render_template('home.html')

@bp.route('/crear_casa', methods=['GET'])
def mostrar_formulario_casa():
    return render_template('crear_casa.html')


# Crear casa
@bp.route('/casas', methods=['POST'])
def crear_casa():
    nombre = request.form.get('nombre') or (request.json.get('nombre'))
    db = sqlite3.connect(current_app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute("INSERT INTO casas (nombre) VALUES (?)", (nombre,))
    db.commit()
    db.close()
    return render_template('casacreada.html', nombre=nombre)

# Mostrar formulario para crear usuario
@bp.route('/crear_usuario', methods=['GET'])
def mostrar_formulario_usuario():
    return render_template('crear_usuario.html')

# Crear usuario
@bp.route('/crearusuario', methods=['POST'])
def crear_usuario():
    nombre = request.form.get('nombre') or (request.json and request.json.get('nombre'))
    id_casa = request.form.get('id_casa') or (request.json and request.json.get('id_casa'))

    db = sqlite3.connect(current_app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, id_casa) VALUES (?, ?)", (nombre, id_casa))
    db.commit()
    db.close()

    return render_template('usuariocreado.html', nombre=nombre)


# Mostrar formulario para agregar lavado
@bp.route('/crear_lavado', methods=['GET'])
def mostrar_formulario_lavado():
    return render_template('crear_lavado.html')

# Agregar lavado
@bp.route('/lavados', methods=['POST'])
def agregar_lavado():
  try:
        id_casa = request.form.get('id_casa') or (request.json and request.json.get('id_casa'))
        id_usuario = request.form.get('id_usuario') or (request.json and request.json.get('id_usuario'))
        fecha = request.form.get('fecha') or (request.json and request.json.get('fecha'))
        turno = request.form.get('turno') or (request.json and request.json.get('turno'))
        detalles = request.form.get('detalles') or (request.json and request.json.get('detalles'))

        db = sqlite3.connect(current_app.config['DATABASE'])
        cursor = db.cursor()
        cursor.execute("INSERT INTO lavados (id_casa, id_usuario, fecha, turno, detalles) VALUES (?, ?, ?, ?, ?)",
                       (id_casa, id_usuario, fecha, turno, detalles))
        db.commit()
        db.close()
        return jsonify(ok=True, msg="✅ Lavado agregado con éxito 🚀"), 201
  except Exception as e:
        return jsonify({"ok": False, "msg": f"❌ Error: {str(e)}"})


@bp.route("/mostrarlavados", methods=['GET'])
def mostrar_lavados():
    try:
        db = sqlite3.connect(current_app.config['DATABASE'])
        db.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
        cursor = db.cursor()

        # JOIN para obtener nombres de usuario y casa
        query = """
        SELECT l.id, u.nombre AS nombre_usuario, c.nombre AS nombre_casa,
            l.fecha, l.turno, l.detalles
        FROM lavados l
        LEFT JOIN usuarios u ON l.id_usuario = u.id
        LEFT JOIN casas c ON l.id_casa = c.id
        """
        cursor.execute(query)
        lavados_db = cursor.fetchall()
        db.close()

        # Convertimos a lista de diccionarios
        lista_lavados = []
        for l in lavados_db:
            lista_lavados.append({
                "id": l["id"],
                "usuario": l["nombre_usuario"],
                "casa": l["nombre_casa"],
                "fecha": l["fecha"],
                "turno": l["turno"],
                "detalles": l["detalles"]
            })
        return jsonify({"ok":True, "lavados":lista_lavados})
    
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}) 
        
    
# Obtener usuarios
@bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        db = sqlite3.connect(current_app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        
        cursor.execute("SELECT id, nombre, password FROM usuarios")
        usuarios_db = cursor.fetchall()
        db.close()
        # Convertimos a lista de diccionarios
        lista_usuarios = []
        for u in usuarios_db:
            lista_usuarios.append({
                "id": u["id"],
                "nombre": u["nombre"],
                "password": u["password"]
            })
        return jsonify({"ok": True, "usuarios": lista_usuarios})
    
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
# Login de usuario
@bp.route('/usuarios/login', methods=['POST'])
def login_usuario():
    try:
        data = request.get_json()
        id_usuario = int(data.get('id_usuario'))
        password = data.get('password')

        db = sqlite3.connect(current_app.config['DATABASE'])
        cursor = db.cursor()

        # Traemos al usuario de la DB
        cursor.execute("SELECT id, nombre, password, rol FROM usuarios WHERE id = ?", (id_usuario,))
        usuario = cursor.fetchone()
        db.close()

        if not usuario:
            return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

        user_id, nombre, stored_password, rol = usuario

        # Si es admin → necesita contraseña válida
        if rol == "Admin":
            if not password:
                return jsonify({"ok": False, "msg": "Se requiere contraseña para este usuario"}), 400
            if stored_password != password:
                return jsonify({"ok": False, "msg": "Contraseña incorrecta"}), 401

        # Si llega acá → login exitoso
        return jsonify({
            "ok": True,
            "msg": "Login exitoso",
            "usuario": {
                "id": user_id,
                "nombre": nombre,
                "rol": rol
            }
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

