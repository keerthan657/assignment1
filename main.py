from flask import Flask, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
import pdfkit
# pdfkit also needs wkhtmltopdf application

# app initialization
app = Flask(__name__)
postgreSQL_pass = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:'+postgreSQL_pass+'@localhost/test_db1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
	__tablename__ = 'STUDENT'
	studentID = db.Column(db.Integer, primary_key=True)
	studentName = db.Column(db.String(30), nullable=False)
	grade = db.Column(db.String(1), nullable=False)

	def __init__(self, name, grade):
		self.studentName = name
		self.grade = grade

class Teacher(db.Model):
	__tablename__ = 'TEACHER'
	teacherID = db.Column(db.Integer, primary_key=True)
	teacherName = db.Column(db.String(30), nullable=False)

	def __init__(self, name):
		self.teacherName = name

class Teaches(db.Model):
	__tablename__ = 'TEACHES'
	teacherID = db.Column(db.Integer, db.ForeignKey('TEACHER.teacherID'), primary_key=True)
	studentID = db.Column(db.Integer, db.ForeignKey('STUDENT.studentID'), primary_key=True)
	numHours = db.Column(db.Integer)

	def __init__(self, teacherID, studentID):
		self.teacherID = teacherID
		self.studentID = studentID


def get_teacher_name(teacherID):
	# query in Teacher table
	entry = Teacher.query.filter_by(teacherID=teacherID).first()
	if(entry):
		return entry.teacherName
	return 'def'

def get_student_name(studentID):
	# query in Student table
	entry = Student.query.filter_by(studentID=studentID).first()
	if(entry):
		return entry.studentName
	return 'def'

# main page
@app.route('/', methods=['POST', 'GET'])
def front_page():
	return render_template('main_page.html', message='', result_list=None)

# method to get list of teachers
@app.route('/get_teacher_all', methods=['POST', 'GET'])
def get_teachers_all():
	teachers_list = Teacher.query.all()
	return render_template('main_page.html', message='All teachers: ', result_list=[get_teacher_name(e.teacherID) for e in teachers_list])

# method to get list of teachers for a particular student
@app.route('/get_teacher_specific', methods=['POST', 'GET'])
def get_teacher_specific():
	student_id = request.form['student_id']
	teaches_list = Teaches.query.filter_by(studentID=student_id).all()
	return render_template('main_page.html', message='All teachers for studentID='+student_id, result_list=[get_teacher_name(e.teacherID) for e in teaches_list])

# method to get list of students for a particular teacher
@app.route('/get_student_specific', methods=['POST', 'GET'])
def get_student_specific():
	teacher_id = request.form['teacher_id']
	teaches_list = Teaches.query.filter_by(teacherID=teacher_id).all()
	return render_template('main_page.html', message='All students for teacherID='+teacher_id, result_list=[get_student_name(e.studentID) for e in teaches_list])

# method to get and download certificate
@app.route('/download_certificate', methods=['POST', 'GET'])
def get_certificate():
	teacher_id = request.form['teacher_id']
	student_id = request.form['student_id']
	if student_id=='' and teacher_id=='':
		return render_template('main_page.html', message='Not found any entries!!', result_list=[])
	elif student_id=='' and teacher_id!='':
		teaches_list = Teaches.query.filter_by(teacherID=teacher_id).all()
		rendered = render_template('pdf_template.html', body1='Teacher: '+get_teacher_name(teacher_id), body2_list=[get_student_name(e.studentID) for e in teaches_list])
	elif student_id!='' and teacher_id=='':
		teaches_list = Teaches.query.filter_by(studentID=student_id).all()
		rendered = render_template('pdf_template.html', body1='Student: '+get_student_name(student_id), body2_list=[get_teacher_name(e.teacherID) for e in teaches_list])
	else:
		teaches_list = Teaches.query.filter_by(studentID=student_id, teacherID=teacher_id).all()
		rendered = render_template('pdf_template.html', body1='Student: '+get_student_name(student_id), body2_list=[get_teacher_name(e.teacherID) for e in teaches_list])

	pdf = pdfkit.from_string(rendered, False)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'
	return response

if __name__=='__main__':
	app.run(debug=True)