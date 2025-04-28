# routes/auth_routes.py
from flask import Blueprint, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import db, User

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        # Успешная авторизация
        session['user_id'] = user.id
        return redirect(url_for('index_bp.index'))
    else:
        flash('Неправильный email или пароль')
        return redirect(url_for('index_bp.index'))


@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Проверяем, нет ли уже пользователя с таким email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Такой email уже зарегистрирован')
        return redirect(url_for('index_bp.index'))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Сразу логиним пользователя после регистрации
    session['user_id'] = new_user.id

    return redirect(url_for('index_bp.index'))


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index_bp.index'))
