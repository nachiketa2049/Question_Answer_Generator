import os
import unicodedata
from werkzeug.utils import secure_filename #2.1.0
import model
import requests #2.27.1
from bs4 import BeautifulSoup #4.10.0
from threading import Thread
from flask_sqlalchemy import SQLAlchemy  #2.5.1
from sqlalchemy import ForeignKey #1.4.34
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request, redirect, url_for, session #2.1.1
import re
from flask_bcrypt import Bcrypt #3.2.0
import docx2txt #0.8
import random
import math
from flask_mail import Mail, Message #0.9.1
from password_generator import gen_password

app = Flask(__name__)
app.secret_key = 'nb2049'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nh2001nh@localhost/question_answer_database'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

#mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "nlquest001@gmail.com"
app.config['MAIL_PASSWORD'] = "tzexydyeosxtbzht"
mail = Mail(app)

Base = declarative_base()

class UserData(Base, db.Model):
    __tablename__ = 'user_data'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    children = relationship("QuestionAnswer", back_populates="parent")


class QuestionAnswer(Base, db.Model):
    __tablename__ = 'question_answer'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1500), nullable=False)
    paraphrased_question = db.Column(db.String(2000), nullable=False)
    answer = db.Column(db.String(2500), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user_data.user_id'))
    timestamp = db.Column(db.Integer, nullable=False)
    parent = relationship("UserData", back_populates="children")

# intialize bcrypt
bcrypt = Bcrypt(app)

def generate_otp():
    OTP=""
    digits = "0123456789"
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


@app.route('/', methods=['GET', 'POST'])
def login():
    #  give the Output message if something goes wrong...
    msg = ''
    msg1 = ''
    # Check  the condition if "email" and "password" POST requests exist when user submitted form
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']

        user = UserData.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                session['loggedin'] = True
                session['id'] = user.user_id
                session['username'] = user.user_name
                session['email']=user.email
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect email/password!'
                msg1 = 'forget password ?'
        else:
            #  print the message if lAccount doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
            msg1 = 'forget password ?'
            return render_template('index.html', msg=msg, msg1=msg1)
    return render_template('index.html', msg=msg, msg1=msg1)


@app.route('/sendotp', methods=['POST','GET'])
def sendotp():
    global OTP
    OTP= generate_otp()
    if request.method == "POST":
        email = request.form["email"]
        login = UserData.query.filter_by(email=email).first()
        print(login)
        if login != None:
            session['id'] = login.user_id
            session['email'] = login.email

            msg = Message()
            msg.subject = "Login OTP"
            msg.recipients = [email]
            msg.sender = "nlquest001@gmail.com"
            msg.body = "Hi, your OTP for login is " + OTP
            mail.send(msg)
            msg="OTP sent succesfully.."
            return render_template("otp.html", msg=msg)
        else:
            msg1 = 'Eneter valid email addres'
            return render_template("email.html", msg1=msg1)
    return render_template('email.html')

@app.route('/verify', methods=["POST"])
def verify():
    user_otp = request.form['otp']
    if int(OTP) == int(user_otp):
        session['loggedin'] = True
        # Redirect to home page
        user=UserData.query.filter_by(user_id=session['id']).first()
        return render_template('home.html',username=user.user_name)
    else:
        msg="Please enter valid otp"
        return render_template('otp.html', msg=msg)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_pwd():
    if request.method == "POST":
        email = request.form["email"]
        user = UserData.query.filter_by(email=email).first()
        if user!=None:
            temp_pwd= gen_password()
            print(temp_pwd)
            #encrypt password
            encrypted_password = bcrypt.generate_password_hash(temp_pwd)
            user.password= encrypted_password
            db.session.add(user)
            db.session.commit()
            msg = Message()
            msg.subject = "Forgot Password"
            msg.recipients = [email]
            msg.sender = "nlquest001@gmail.com"
            msg.body = "Hi, your new Generated password is " + temp_pwd
            mail.send(msg)
            msg1='Password successfully sent to your email. Now you have to go to login page for login again '
            return render_template("forgot.html",msg1=msg1)
        else :
            msg1 = "Not valid email or User doesn't exist with same email"
            return render_template("forgot.html",msg1=msg1)
    return render_template("forgot.html")

@app.route('/logout')
def logout():
    # Remove session data, show the user is logout and redirect login page
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    # Check if user is login display home page otherwise redirect login page
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist user submitted form
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        user_name = request.form['username']
        email = request.form['email']
        encrypt_password = bcrypt.generate_password_hash(request.form['password'])
        user = UserData.query.filter_by(email=email).first()

        # If account exists show error and validation checks
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z]+', user_name):
            msg = 'Username must contain only characters and numbers!'
        elif not user_name or not encrypt_password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            user = UserData()
            user.user_name = user_name
            user.email = email
            user.password = encrypt_password
            db.session.add(user)
            db.session.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    elif request.method == 'get':
        # Form is empty return message
        msg = 'Please fill out the form!'
    # Show registration form with message
    return render_template('register.html', msg=msg)


# crete profile page it can  only accessible for login users
@app.route('/profile')
def profile():
    # Check if user is login show detail in profile page
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        account = UserData.query.filter_by(email=session['email']).first()
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route("/update", methods=['get', 'post'])
def update():
    msg=' '
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'email' in request.form:
            old_username = request.form['old_username']
            user_name = request.form['username']
            new_password = request.form['password']
            confirm_password = request.form['conpassword']
            user=UserData.query.filter_by(user_name=user_name).first()
            if user!=None:
                msg = 'Account already exists !'
            elif not re.match(r'[A-Za-z0-9]+', user_name):
                msg = 'name must contain only characters and numbers !'
            elif new_password != confirm_password:
                msg = "confirm and new password doesn't match"
                return render_template("update.html", msg=msg)
            else:
                encrypt_password = bcrypt.generate_password_hash(new_password)
                cursor = UserData.query.filter_by(user_name=old_username).first()
                cursor.user_name = user_name
                cursor.password = encrypt_password
                db.session.add(cursor)
                db.session.commit()
                return redirect(url_for('profile'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
            return render_template("update.html", msg=msg)
        return render_template("update.html", msg=msg)


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    msg=''
    if 'loggedin' in session:
        if request.method == "POST":
            delete_data=request.form['delete_data']
            if delete_data == 'Delete your Account':
                user_id = session['id']
                user = UserData.query.filter_by(user_id=user_id).first()
                db.session.delete(user)
                db.session.commit()
                msg = 'User deleted successfully!'
                return redirect(url_for('login'))
            elif delete_data == 'Delete your Dashboard Data':
                user_id = session['id']
                question_answer = QuestionAnswer.query.filter_by(user_id=user_id).all()
                for i in question_answer:
                    db.session.delete(i)
                    db.session.commit()
                return redirect(url_for('home'))

        elif request.method == 'POST':
            msg = 'delete data in from !'
        return render_template("delete.html", msg=msg)


@app.route("/resetpwd", methods=['GET', 'POST'])
def resetpwd():
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form:
            new_password = request.form['password']
            confirm_password = request.form['conpassword']

            # Check the account exists using MySQL
            data = UserData.query.filter_by(user_id=session['id'])

            # If account exists show error and validation checks
            if data!=None:
                if new_password == confirm_password:
                    encrypt_password = bcrypt.generate_password_hash(new_password)
                    data.password = encrypt_password
                    db.session.add(data)
                    db.session.commit()
                    msg = 'You have successfully changed password!'
                    return render_template('index.html', msg=msg)

                else:
                    msg = "new password and confirm password doesn't match"
                    return render_template('resetpwd.html', msg=msg)

            else:
                msg = "user doesn't exist"
                return render_template('register.html', msg=msg)

        # password resseting
        return render_template('resetpwd.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if 'loggedin' in session:
        if request.method == 'POST' and request.form.get('inputs') != None:
            inputs = request.form.get('inputs')
            print(inputs)
            text = ' '
            if inputs == 'test':
                text = inputs = request.form.get('test')
                text = text.replace('\n', ' ')

            elif inputs == 'link':
                # link for extract html data
                url = request.form.get('hidden-other')
                r = requests.get(url)
                htmldata = r.text
                soup = BeautifulSoup(htmldata, 'html.parser')
                for data in soup.find_all("p"):
                    text += data.get_text()
                paras = text.replace('\n', ' ').replace('\r', '')
                text = unicodedata.normalize("NFKD", paras)
                text_list = text.split(" ")
                if len(text_list)>150:
                    text = " ".join(text_list[:150])

            elif inputs == 'fileUpload':
                # PDF procssing
                file = request.files['fileUpload']
                filename=secure_filename(file.filename)
                path = os.getcwd() + "\\static\\uploads"
                file.save(os.path.join(path, filename))
                open_path=os.getcwd() + "\\static\\uploads\\" + filename
                FileObj = open(open_path, 'rb')
                text = docx2txt.process(FileObj)
                text = text.replace('\n', ' ').replace('\t', '').replace('\r', ' ')
                text_list = text.split(" ")
                if len(text_list)>150:
                    text = " ".join(text_list[:150])
                FileObj.close()
                os.remove(open_path)

            #Thread(target=model.generate_question_answer, args=(text, session['id'], session['email'])).start()
            model.generate_question_answer(text,session['id'], session['email'])
            return redirect(url_for('dashboard'))
        return render_template('input.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        question_answer_list=[]
        quest_ans=QuestionAnswer.query.filter_by(user_id=session['id']).all()
        if len(quest_ans)>0:
            timestamp = quest_ans[-1].timestamp
        else:
            timestamp=0
        question_answer=QuestionAnswer.query.filter_by(user_id=session['id'],timestamp=timestamp).all()
        for i in question_answer:
            qa_dict={"Question":i.question,
                     "Paraphrased_Question":eval(i.paraphrased_question),
                     "Answer":i.answer}
            question_answer_list.append(qa_dict)
            
        return render_template('generated.html',question_answer_list=question_answer_list)


if __name__ == '__main__':
    app.run(debug=False)

