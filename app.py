import os
from flask import Flask
import config

# Importar los controladores (Blueprints)
from controllers.main_controller import main_bp
from controllers.search_controller import search_bp
from controllers.download_controller import download_bp

def create_app():
    app = Flask(__name__)
    
    # Configurar claves de sesión y comportamiento básico
    app.secret_key = config.SECRET_KEY
    
    # Registrar los Blueprints (MVC)
    app.register_blueprint(main_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(download_bp)
    
    # Crear carpeta de descargas al iniciar si no existe
    if not os.path.exists(config.DOWNLOADS_DIR):
        os.makedirs(config.DOWNLOADS_DIR)
        print(f"[XtractorMP3] Carpeta creada en: {config.DOWNLOADS_DIR}")
        
    return app

app = create_app()

if __name__ == '__main__':
    print("[XtractorMP3] Iniciando servidor local en http://localhost:5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
