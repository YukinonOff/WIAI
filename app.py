from flask import Flask, request, redirect, url_for, render_template, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Загрузка данных из JSON-файлов
def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {filename}: {e}")
            return {}
    return {}

# Сохранение данных в JSON-файлы
def save_data(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"Error writing to {filename}: {e}")

# Инициализация файлов данных при первом запуске
if not os.path.exists('data.json'):
    save_data('data.json', {'sections': []})
if not os.path.exists('users.json'):
    save_data('users.json', {'admin': 'admin'})

data = load_data('data.json')
users = load_data('users.json')

# Главная страница
@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('index.html', data=data)
    return redirect(url_for('login'))

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Добавление нового раздела
@app.route('/add_section', methods=['POST'])
def add_section():
    if 'logged_in' in session:
        section_name = request.form['section_name']
        if section_name:
            data['sections'].append({'name': section_name, 'subsections': []})
            save_data('data.json', data)
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Удаление раздела
@app.route('/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    if 'logged_in' in session:
        if 0 <= section_id < len(data['sections']):
            del data['sections'][section_id]
            save_data('data.json', data)
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Добавление подраздела
@app.route('/add_subsection', methods=['POST'])
def add_subsection():
    if 'logged_in' in session:
        section_id = int(request.form['section_id'])
        subsection_name = request.form['subsection_name']
        if 0 <= section_id < len(data['sections']) and subsection_name:
            data['sections'][section_id]['subsections'].append({'name': subsection_name, 'files': []})
            save_data('data.json', data)
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Удаление подраздела
@app.route('/delete_subsection/<int:section_id>/<int:subsection_id>', methods=['POST'])
def delete_subsection(section_id, subsection_id):
    if 'logged_in' in session:
        if (0 <= section_id < len(data['sections']) and
            0 <= subsection_id < len(data['sections'][section_id]['subsections'])):
            del data['sections'][section_id]['subsections'][subsection_id]
            save_data('data.json', data)
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Добавление файла
@app.route('/add_file', methods=['POST'])
def add_file():
    if 'logged_in' in session:
        section_id = int(request.form['section_id'])
        subsection_id = int(request.form['subsection_id'])
        file_name = request.form['file_name']
        if (0 <= section_id < len(data['sections']) and
            0 <= subsection_id < len(data['sections'][section_id]['subsections']) and
            file_name):
            data['sections'][section_id]['subsections'][subsection_id]['files'].append(file_name)
            save_data('data.json', data)
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Удаление файла
@app.route('/delete_file/<int:section_id>/<int:subsection_id>/<int:file_id>', methods=['POST'])
def delete_file(section_id, subsection_id, file_id):
    if 'logged_in' in session:
        if (0 <= section_id < len(data['sections']) and
            0 <= subsection_id < len(data['sections'][section_id]['subsections']) and
            0 <= file_id < len(data['sections'][section_id]['subsections'][subsection_id]['files'])):
            del data['sections'][section_id]['subsections'][subsection_id]['files'][file_id]
            save_data('data.json', data)
        return redirect(url_for('index'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
