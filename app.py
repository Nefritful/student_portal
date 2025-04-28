# app.py
from flask import Flask
from db import db, ma
import os

def create_app():
    app = Flask(__name__)

    # Секретный ключ для сессий
    app.config['SECRET_KEY'] = 'some-secret-key'
    # Подключение к базе данных (MySQL через pymysql)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/student_portal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация базы и Marshmallow
    db.init_app(app)
    ma.init_app(app)

    # Создание таблиц (если их ещё нет)
    with app.app_context():
        db.create_all()

    @app.template_filter('strftime')
    def strftime_filter(value, format_str="%Y-%m-%d"):
        """Преобразует объект datetime/date по заданному формату."""
        if not value:
            return ""
        return value.strftime(format_str)

    # Импортируем и регистрируем блюпринты (маршруты)
    from routes.index_routes import index_bp
    from routes.events_routes import events_bp
    from routes.publications_routes import publications_bp
    from routes.forum_routes import forum_bp
    from routes.profile_routes import profile_bp
    from routes.auth_routes import auth_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(publications_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(auth_bp)

    # Настройка пути для папки uploads
    UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Обслуживание папки uploads как статической
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return app

if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
