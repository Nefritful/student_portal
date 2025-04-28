# routes/publications_routes.py

import os
import logging
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, send_from_directory
from sqlalchemy import func
from db import db, User, Publication
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename  # Для безопасности
import mimetypes

publications_bp = Blueprint('publications_bp', __name__, url_prefix='/publications')

# Конфигурация пути загрузки
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = None  # Убираем проверки расширений

# Убедитесь, что папка существует
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    # Убираем все проверки расширений
    return filename

@publications_bp.route('/', methods=['GET'])
def publications_home():
    user_logged_in = 'user_id' in session
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = User.query.get(user_id)
    # Получаем текст из поля поиска (если был)
    search_term = request.args.get('search', '').strip()

    # Получаем список типов файлов + сколько их (GROUP BY file_type)
    file_types = db.session.query(
        Publication.file_type,
        func.count(Publication.id).label('count')
    ).group_by(Publication.file_type).all()

    # Фильтруем публикации, если есть поисковый запрос
    if search_term:
        publications = Publication.query.filter(Publication.title.ilike(f"%{search_term}%")).order_by(Publication.id.desc()).limit(5).all()
    else:
        publications = Publication.query.order_by(Publication.id.desc()).limit(5).all()

    logger.info(f"Отображение {len(publications)} публикаций. Поиск: '{search_term}'")

    return render_template('publications.html',
                           user_logged_in=user_logged_in,
                           user=user,
                           file_types=file_types,
                           publications=publications,
                           search_term=search_term)

@publications_bp.route('/add', methods=['POST'])
def add_publication():
    logger.info("Начало обработки добавления публикации.")
    user_id = session.get('user_id')
    if not user_id:
        flash("Вы не авторизованы")
        logger.warning("Попытка добавления публикации неавторизованным пользователем.")
        return redirect(url_for('publications_bp.publications_home'))

    user = User.query.get(user_id)
    if user.role != 'admin':
        flash("Доступ только для админов")
        logger.warning(f"Пользователь {user.username} без прав администратора пытается добавить публикацию.")
        return redirect(url_for('publications_bp.publications_home'))

    title = request.form.get('title')
    content = request.form.get('content')
    logger.info(f"Получены данные публикации: title='{title}', content='{content}'")

    # Загрузка файла
    file = request.files.get('file')  # type: FileStorage
    file_extension = file.filename.split('.')[-1]
    if file_extension == 'pdf':
        file_type = 'PDF'
    elif file_extension in {'docx', 'doc'}:
        file_type = 'Документ'
    elif file_extension in {'jpg', 'jpeg', 'png', 'gif'}:
        file_type = 'Изображение'
    else:
        file_type = 'Другой'

    file_path = None

    if file and allowed_file(file.filename):
        # Сохраняем оригинальное имя файла
        original_filename = file.filename
        if original_filename == '':
            flash("Имя файла пустое")
            logger.warning("Попытка загрузки файла с пустым именем.")
            return redirect(url_for('publications_bp.publications_home'))

        unique_filename = original_filename  # Используем оригинальное имя файла
        logger.info(f"Используемое имя файла: {unique_filename}")

        # Определяем путь для сохранения
        file_path = file.filename  # Относительный путь
        full_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        logger.info(f"Полный путь для сохранения файла: {full_path}")

        try:
            # Сохраняем файл
            file.save(full_path)
            logger.info(f"Файл успешно сохранён: {full_path}")
        except Exception as e:
            flash(f"Ошибка при сохранении файла: {e}")
            logger.error(f"Ошибка при сохранении файла {unique_filename}: {e}")
            return redirect(url_for('publications_bp.publications_home'))
    elif file:
        flash("Недопустимый тип файла или имя файла пустое")
        logger.warning("Попытка загрузки недопустимого файла.")
        return redirect(url_for('publications_bp.publications_home'))

    # Создаём новую публикацию
    pub = Publication(
        title=title,
        content=content,
        file_type=file_type,
        file_path=file_path
    )
    db.session.add(pub)
    try:
        db.session.commit()
        flash("Публикация добавлена!")
        logger.info(f"Публикация успешно добавлена: '{title}'")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при добавлении публикации: {e}")
        logger.error(f"Ошибка при добавлении публикации '{title}': {e}")
        return redirect(url_for('publications_bp.publications_home'))

    return redirect(url_for('publications_bp.publications_home'))

# Обслуживание загруженных файлов
@publications_bp.route('/<filename>')
def uploaded_file(filename):
    try:
        logger.info(f"Попытка скачивания файла: {filename}")
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        flash("Файл не найден.")
        logger.error(f"Файл не найден при попытке скачать: {filename}")
        return redirect(url_for('publications_bp.publications_home'))
