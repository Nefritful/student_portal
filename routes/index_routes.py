# routes/index_routes.py
from flask import Blueprint, render_template, session
from db import db, Event, ForumTopic, Publication

index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/')
def index():
    # Пример: берём последние 5 записей, сортируя по убыванию ID
    # (или по created_at, если у вас есть такая колонка)
    events = Event.query.order_by(Event.id.desc()).limit(5).all()
    topics = ForumTopic.query.order_by(ForumTopic.id.desc()).limit(5).all()
    publications = Publication.query.order_by(Publication.id.desc()).limit(5).all()

    # Пример проверки авторизации (если надо передавать user_logged_in):
    user_logged_in = 'user_id' in session

    return render_template(
        'index.html',
        user_logged_in=user_logged_in,
        events=events,
        topics=topics,
        publications=publications
    )
