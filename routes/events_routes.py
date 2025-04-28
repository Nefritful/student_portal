# routes/events_routes.py


from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from db import db, User, Event, ForumTopic
from datetime import datetime, date
import calendar
import locale

events_bp = Blueprint('events_bp', __name__, url_prefix='/events')

# Установите локаль на русском языке
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    # Если локаль не поддерживается, используем английский
    locale.setlocale(locale.LC_TIME, 'C')


@events_bp.route('/')
def events_home():
    user_logged_in = 'user_id' in session
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = User.query.get(user_id)

    # Получаем текущую дату
    today_date = date.today()

    # Получаем параметры year и month из запроса, если они есть
    year = request.args.get('year', today_date.year, type=int)
    month = request.args.get('month', today_date.month, type=int)

    # Проверяем валидность месяца
    if month < 1 or month > 12:
        flash("Неверный месяц. Показан текущий месяц.")
        year = today_date.year
        month = today_date.month

    # Получаем название месяца на русском языке
    try:
        month_name = datetime(year, month, 1).strftime('%B').capitalize()
    except ValueError:
        month_name = calendar.month_name[today_date.month].capitalize()

    # Получаем список мероприятий из БД
    events = Event.query.filter(
        db.extract('year', Event.start_date) <= year,
        db.extract('month', Event.start_date) <= month,
        db.extract('year', Event.end_date) >= year,
        db.extract('month', Event.end_date) >= month
    ).all()

    # Создаём календарь
    cal = calendar.Calendar(firstweekday=0)  # Неделя начинается с понедельника
    month_days = cal.monthdatescalendar(year, month)

    # Генерируем данные для календаря
    calendar_data = []
    for week in month_days:
        week_data = []
        for day in week:
            day_obj = {
                'number': day.day,
                'date': day,
                'is_current_month': day.month == month,
                'has_event': False,
                'event_info': []
            }
            # Проверяем наличие мероприятий на этот день
            for event in events:
                if event.start_date.date() <= day <= event.end_date.date():
                    day_obj['has_event'] = True
                    day_obj['event_info'].append(event.title)
            week_data.append(day_obj)
        calendar_data.append(week_data)

    # Определяем предыдущий и следующий месяц для навигации
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    return render_template('events.html',
                           user_logged_in=user_logged_in,
                           user=user,
                           events=events,
                           calendar_data=calendar_data,
                           year=year,
                           month=month,
                           month_name=month_name,
                           prev_year=prev_year,
                           prev_month=prev_month,
                           next_year=next_year,
                           next_month=next_month,
                           today=today_date)


@events_bp.route('/create', methods=['POST'])
def create_event():

    # Проверка авторизации
    user_id = session.get('user_id')
    if not user_id:
        flash("Вы не авторизованы")
        return redirect(url_for('events_bp.events_home'))

    user = User.query.get(user_id)
    if user.role != 'admin':
        flash("Доступ только для админов")
        return redirect(url_for('events_bp.events_home'))

    # Извлекаем данные из формы
    title = request.form.get('title')
    description = request.form.get('description')
    start_date_str = request.form.get('start_date')  # "2025-01-28T10:00"
    end_date_str = request.form.get('end_date')

    # Преобразуем строки в datetime
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        flash("Неверный формат даты и времени.")
        return redirect(url_for('events_bp.events_home'))

    # Создаём событие
    new_event = Event(
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        topic_id=None  # Пока None, заполним после создания топика
    )
    db.session.add(new_event)
    db.session.commit()

    # Создаём топик в разделе "Мероприятия" (ID=1)
    new_topic = ForumTopic(
        title=title,
        content=description,
        created_at=datetime.utcnow(),
        section_id=1  # ID=1 подразумеваем, что в forum_sections (id=1) - это "Мероприятия"
    )
    db.session.add(new_topic)
    db.session.commit()

    # Привязываем событие к топику
    new_event.topic_id = new_topic.id
    db.session.commit()

    flash("Мероприятие и топик успешно созданы!")
    return redirect(url_for('events_bp.events_home'))
