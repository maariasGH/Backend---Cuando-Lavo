from flask import Flask # type: ignore
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración de la base de datos
    app.config['DATABASE'] = os.path.join(app.instance_path, 'lavadero.db')

    # Asegurarse de que la carpeta instance exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Importar rutas
    from . import routes
    app.register_blueprint(routes.bp)
    
     # Inicializar la base de datos si no existe
    from .models import init_db, close_db
    init_db(app)
    app.teardown_appcontext(close_db)

    return app
