# app.py
from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import markdown
import json

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/courses')
def get_courses():
    courses = [d for d in os.listdir('Courses') if os.path.isdir(os.path.join('Courses', d))]
    return jsonify(courses)

@app.route('/api/course_structure/<course>')
def get_course_structure(course):
    course_path = os.path.join('Courses', course)
    structure = {
        'name': course,
        'modules': []
    }
    for module in sorted(os.listdir(course_path)):
        module_path = os.path.join(course_path, module)
        if os.path.isdir(module_path):
            module_structure = {
                'name': module,
                'lessons': []
            }
            for lesson in sorted(os.listdir(module_path)):
                lesson_path = os.path.join(module_path, lesson)
                if os.path.isdir(lesson_path):
                    lesson_structure = {
                        'name': lesson,
                        'steps': sorted([f for f in os.listdir(lesson_path) if f.endswith('.md')])
                    }
                    module_structure['lessons'].append(lesson_structure)
            structure['modules'].append(module_structure)
    return jsonify(structure)

@app.route('/api/content/<course>/<module>/<lesson>/<step>')
def get_content(course, module, lesson, step):
    path = os.path.join('Courses', course, module, lesson, step)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    html_content = markdown.markdown(content, extensions=['fenced_code', 'codehilite'])
    return jsonify({"content": html_content})

@app.route('/api/save_progress', methods=['POST'])
def save_progress():
    data = request.json
    user = data['user']
    progress = data['progress']
    
    with open(f'progress_{user}.json', 'w') as f:
        json.dump(progress, f)
    
    return jsonify({"status": "success"})

@app.route('/api/load_progress/<user>')
def load_progress(user):
    try:
        with open(f'progress_{user}.json', 'r') as f:
            progress = json.load(f)
        return jsonify(progress)
    except FileNotFoundError:
        return jsonify({})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)