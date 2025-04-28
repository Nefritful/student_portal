# routes/forum_routes.py

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from db import db, User, ForumSection, ForumTopic, ForumPost
from datetime import datetime

forum_bp = Blueprint('forum_bp', __name__, url_prefix='/forum')


def allowed_file(filename):
    # Вы можете добавить проверки по расширению, если нужно
    return '.' in filename


@forum_bp.route('/')
def forum_home():
    user_logged_in = 'user_id' in session
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = User.query.get(user_id)

    # Получаем все разделы
    sections = ForumSection.query.all()

    # Получаем параметр section_id из запроса
    section_id = request.args.get('section_id', type=int)

    if section_id:
        # Проверяем, существует ли раздел с таким ID
        selected_section = ForumSection.query.get(section_id)
        if not selected_section:
            flash("Выбранный раздел не существует.")
            return redirect(url_for('forum_bp.forum_home'))

        # Получаем топики, относящиеся к выбранному разделу
        topics = ForumTopic.query.filter_by(section_id=section_id).order_by(ForumTopic.created_at.desc()).all()
    else:
        # Если раздел не выбран, показываем все топики
        topics = ForumTopic.query.order_by(ForumTopic.created_at.desc()).all()
        selected_section = None  # Нет выбранного раздела

    return render_template('forum.html',
                           user_logged_in=user_logged_in,
                           user=user,
                           sections=sections,
                           topics=topics,
                           selected_section=selected_section)


@forum_bp.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    # Получаем топик по ID
    user_logged_in = 'user_id' in session
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = User.query.get(user_id)
    topic = ForumTopic.query.get_or_404(topic_id)

    # Получаем связанный раздел
    section = ForumSection.query.get(topic.section_id)
    if not section:
        flash("Раздел для этого топика не найден.")
        return redirect(url_for('forum_bp.forum_home'))

    # Получаем пользователя, создавшего топик
    user = User.query.get(topic.user_id)
    if not user:
        flash("Пользователь, создавший топик, не найден.")
        return redirect(url_for('forum_bp.forum_home'))

    # Получаем посты, связанные с топиком
    posts = ForumPost.query.filter_by(topic_id=topic.id).order_by(ForumPost.created_at.asc()).all()

    return render_template('view_topic.html', user_logged_in=user_logged_in, topic=topic, section=section, user=user, posts=posts)
@forum_bp.route('/topic/<int:topic_id>/create_post', methods=['POST'])
def create_post(topic_id):
    # Проверка авторизации
    user_id = session.get('user_id')
    if not user_id:
        flash("Вы не авторизованы.")
        return redirect(url_for('forum_bp.view_topic', topic_id=topic_id))

    user = User.query.get(user_id)
    if not user:
        flash("Пользователь не найден.")
        return redirect(url_for('forum_bp.view_topic', topic_id=topic_id))

    content = request.form.get('content')
    if not content:
        flash("Пост не может быть пустым.")
        return redirect(url_for('forum_bp.view_topic', topic_id=topic_id))

    # Проверяем существование топика
    topic = ForumTopic.query.get(topic_id)
    if not topic:
        flash("Топик не найден.")
        return redirect(url_for('forum_bp.forum_home'))

    # Создаём новый пост
    new_post = ForumPost(
        content=content,
        created_at=datetime.utcnow(),
        topic_id=topic_id,
        user_id=user_id
    )
    db.session.add(new_post)
    db.session.commit()

    flash("Пост успешно добавлен!")
    return redirect(url_for('forum_bp.view_topic', topic_id=topic_id))

@forum_bp.route('/create_topic', methods=['POST'])
def create_topic():
    user_id = session.get('user_id')
    if not user_id:
        flash("Вы не авторизованы.")
        return redirect(url_for('forum_bp.forum_home'))

    user = User.query.get(user_id)
    if user.role not in ['admin', 'moderator']:  # Пример проверки ролей
        flash("У вас нет прав для создания топиков.")
        return redirect(url_for('forum_bp.forum_home'))

    title = request.form.get('title')
    content = request.form.get('content')
    section_id = request.form.get('section_id', type=int)

    if not title or not content or not section_id:
        flash("Все поля обязательны для заполнения.")
        return redirect(url_for('forum_bp.forum_home'))

    # Проверяем существование раздела
    section = ForumSection.query.get(section_id)
    if not section:
        flash("Выбранный раздел не существует.")
        return redirect(url_for('forum_bp.forum_home'))

    # Создаём новый топик
    new_topic = ForumTopic(
        title=title,
        content=content,
        created_at=datetime.utcnow(),
        section_id=section_id,
        user_id=user_id  # Передаём user_id
    )

    db.session.add(new_topic)
    db.session.commit()

    flash("Топик успешно создан!")
    return redirect(url_for('forum_bp.view_topic', topic_id=new_topic.id))