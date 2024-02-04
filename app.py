from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.Integer)

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender


@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/add_student', methods=["POST"])
def add_student():
    name = request.form['name']
    gender = request.form['gender']
    student = Student(name, gender)
    db.session.add(student)
    db.session.commit()
    return redirect('/')


@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get(student_id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.gender = request.form['gender']
        db.session.commit()
        return redirect('/')

    return render_template('edit_student.html', student=student)


@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect('/')


@app.route('/generate_groups', methods=['POST'])
def generate_groups():
    num_students = len(Student.query.all())
    num_groups = int(request.form['num_groups'])

    female_students = Student.query.filter_by(gender='female').all()
    male_students = Student.query.filter_by(gender='male').all()

    random.shuffle(female_students)
    random.shuffle(male_students)
    
    num_female = len(female_students)
    num_male = len(male_students)

    group_size = num_students // num_groups
    remaining_students = num_students % num_groups

    female_per_group = num_female // num_groups
    remaining_females = num_female % num_groups

    groups = []
    start_index = 0
    for i in range(num_groups):
        end_index = start_index + group_size
        if i < remaining_students:
            end_index += 1
        group = []
        female_count = 0
        while len(group) < group_size:
            if female_count < female_per_group and len(female_students) > 0:
                female = female_students.pop()
                group.append(female.name)
                female_count += 1
            elif len(male_students) > 0:
                male = male_students.pop()
                group.append(male.name)
        groups.append(group)
        start_index = end_index

    # Distribute remaining female students evenly among groups
    for i in range(remaining_females):
        group_index = (i % num_groups)
        female = female_students.pop()
        groups[group_index].append(female.name)

    # Randomly shuffle the students within each group
    for group in groups:
        random.shuffle(group)

    return render_template('dashboard.html', groups=groups)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)