# db.py
import pymysql
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

db = SQLAlchemy()
ma = Marshmallow()

def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="student_portal",  # <-- Ваше название БД
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )

# ------------ МОДЕЛИ ----------------

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(10), default='user', nullable=False)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("forum_topics.id"), nullable=True)

class Publication(db.Model):
    __tablename__ = 'publications'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_type = db.Column(db.String(100), default='Неизвестно', nullable=False)
    file_path = db.Column(db.String(255), nullable=True)

class ForumSection(db.Model):
    __tablename__ = 'forum_sections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)


class ForumTopic(db.Model):
    __tablename__ = 'forum_topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Добавляем связь с ForumSection
    section_id = db.Column(db.Integer, db.ForeignKey('forum_sections.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Добавленное поле

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------ НОВАЯ ТАБЛИЦА ДЛЯ ФАЙЛОВ ----------------
class FileResource(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)      # «Название» или «Заголовок» файла
    filename = db.Column(db.String(250), nullable=False)   # Реальное имя или путь к файлу
    file_type = db.Column(db.String(100), nullable=False)  # Тип (Руководство, Методичка и т. д.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------ СХЕМЫ MARSHMALLOW -------------
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True

class PublicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Publication
        load_instance = True

class ForumTopicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ForumTopic
        load_instance = True

class ForumPostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ForumPost
        load_instance = True

class FileResourceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FileResource
        load_instance = True
