# routes/profile_routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import db, User, ForumPost

profile_bp = Blueprint('profile_bp', __name__, url_prefix='/profile')


@profile_bp.route('/')
def profile_home():
    if 'user_id' not in session:
        flash("Вы не авторизованы.")
        return redirect(url_for('index_bp.index'))
    user_logged_in = 'user_id' in session
    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        flash("Пользователь не найден.")
        return redirect(url_for('index_bp.index'))

    user_posts = ForumPost.query.filter_by(user_id=user_id).order_by(ForumPost.created_at.desc()).all()

    return render_template(
        'profile.html',
        user_logged_in=user_logged_in,
        user=user,
        user_posts=user_posts
    )
