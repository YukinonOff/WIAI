from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Измени на более надежный ключ в продакшене

# Загрузка данных из JSON
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

# Сохранение данных в JSON
def save_data(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Авторизация
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Главная страница
@app.route('/')
def index():
    data = load_data('data.json')
    return render_template('index.html', data=data)

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_data('users.json')
        if username in users and users[username] == password:
            session['logged_in'] = True
            flash('You were successfully logged in', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Выход
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were successfully logged out', 'success')
    return redirect(url_for('index'))

# Админ-панель
@app.route('/admin')
@login_required
def admin():
    data = load_data('data.json')
    return render_template('admin.html', data=data)

# Добавление раздела
@app.route('/add_section', methods=['POST'])
@login_required
def add_section():
    data = load_data('data.json')
    section_name = request.form['section_name']
    data['sections'].append({"name": section_name, "subsections": []})
    save_data('data.json', data)
    flash('Section added successfully', 'success')
    return redirect(url_for('admin'))

# Добавление подраздела
@app.route('/add_subsection', methods=['POST'])
@login_required
def add_subsection():
    data = load_data('data.json')
    section_id = int(request.form['section_id'])
    subsection_name = request.form['subsection_name']
    data['sections'][section_id]['subsections'].append({"name": subsection_name, "files": []})
    save_data('data.json', data)
    flash('Subsection added successfully', 'success')
    return redirect(url_for('admin'))

# Добавление файла
@app.route('/add_file', methods=['POST'])
@login_required
def add_file():
    data = load_data('data.json')
    section_id = int(request.form['section_id'])
    subsection_id = int(request.form['subsection_id'])
    file_name = request.form['file_name']
    data['sections'][section_id]['subsections'][subsection_id]['files'].append(file_name)
    save_data('data.json', data)
    flash('File added successfully', 'success')
    return redirect(url_for('admin'))

# Удаление раздела
@app.route('/delete_section/<int:section_id>', methods=['POST'])
@login_required
def delete_section(section_id):
    data = load_data('data.json')
    data['sections'].pop(section_id)
    save_data('data.json', data)
    flash('Section deleted successfully', 'success')
    return redirect(url_for('admin'))

# Удаление подраздела
@app.route('/delete_subsection/<int:section_id>/<int:subsection_id>', methods=['POST'])
@login_required
def delete_subsection(section_id, subsection_id):
    data = load_data('data.json')
    data['sections'][section_id]['subsections'].pop(subsection_id)
    save_data('data.json', data)
    flash('Subsection deleted successfully', 'success')
    return redirect(url_for('admin'))

# Удаление файла
@app.route('/delete_file/<int:section_id>/<int:subsection_id>/<int:file_id>', methods=['POST'])
@login_required
def delete_file(section_id, subsection_id, file_id):
    data = load_data('data.json')
    data['sections'][section_id]['subsections'][subsection_id]['files'].pop(file_id)
    save_data('data.json', data)
    flash('File deleted successfully', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    if not os.path.exists('users.json'):
        save_data('users.json', {'admin': 'admin'})  # Создает начального пользователя
    if not os.path.exists('data.json'):
        save_data('data.json', {'sections': []})
    app.run(debug=True)
    