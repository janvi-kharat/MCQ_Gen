from datetime import datetime

from flask import Flask, render_template, request, url_for, session, flash, redirect, jsonify
import requests
import pyperclip
from transformers import pipeline

import pandas as pd
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError
import bcrypt
from flask_mysqldb import MySQL
import email_validator
from gen_mcq import display
import cloudinary
from cloudinary.uploader import upload

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))




summarizer = pipeline("summarization", model="Falconsai/text_summarization")

API_URL1 = "https://api-inference.huggingface.co/models/rabiyulfahim/grammerchecking"
headers1= {"Authorization": "Bearer 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"}


app = Flask(__name__)

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")


# Mysql connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Omkar@2004'
app.config['MYSQL_DB'] = 'userdata'
app.secret_key = 'secret'

mysql = MySQL(app)






@app.route('/', methods=['GET','POST'])
def index():
    form = LoginForm()
    form1 = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users1 WHERE email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        print(user)
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            print("login successful")
            return redirect(url_for('home'))
        else:
            print("login failed")
            flash("Login failed. Please check your email and password")
            return redirect(url_for('index'))
    return render_template('index.html',form=form,form1=form1)

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
        password = form.password.data
        hased_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users1(name,email,password) VALUES(%s,%s,%s)", (name, email, hased_password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('index'))


    #     Store data into database
    return render_template('index.html',form=form)





@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('index'))


@app.route('/home')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        print(user_id)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users1 where name=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            print("login successful")
            return render_template('home.html', user=user)
    print("login failed")
    return redirect(url_for('index'))
    return render_template('home.html')


def get_user_by_id(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users1 WHERE name = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

@app.route('/getuser', methods=['GET'])
def get_user():
    user_id = request.args.get('userId')
    user = get_user_by_id(user_id)
    return render_template('Profile.html', user=user)


# # Create a function which return the pdf file by taking input as file name the file store inside the local directory
#
#
#
# # Create a api to download the pdf and store the pdf in the database
# @app.route('/storepdf', methods=['POST'])
# def download_pdf():
# #     get the file name from the request
#     file_name = request.form['file_name']
#     file_data = get_file(file_name)


# Add Feedback api

@app.route('/feedback', methods=['GET'])
def feedback():
    user_id = request.args.get('userId')
    user = get_user_by_id(user_id)
    return render_template('feedback.html', user=user);

# Save feedback to the database

@app.route('/savefeedback', methods=['POST'])
def save_feedback():
    user_id = request.args.get('userId')
    user = get_user_by_id(user_id)
    rating = request.form['rating']
    feedback = request.form['feedback']
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO feedback(userId, date,time,rating,feedback) VALUES(%s,%s,%s,%s,%s)", (user[1], date, time, rating, feedback))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('feedback', userId=user_id))



# Upload File on Cloudinary
def upload_pdf_to_cloudinary(pdf_path):
    # Configure Cloudinary
    cloudinary.config(
        cloud_name="dyb01yvmn",
        api_key="943265581238925",
        api_secret="ihUP1HCN61Mf0MPaDgnXZeK2CBg"
    )

    try:
        # Upload PDF file to Cloudinary
        result = upload(pdf_path, resource_type="raw", use_filename=True, access_mode="public")
        print(result)
        pdfLink = "https://res-console.cloudinary.com/dyb01yvmn/media_explorer_thumbnails/"+result["asset_id"]+"/download";

        # Print public URL of the uploaded PDF file
        print("PDF uploaded successfully. Public URL:", pdfLink)

        return pdfLink

    except Exception as e:
        print("Error uploading PDF to Cloudinary:", e)


# Add MyContent page
@app.route('/mycontent', methods=['GET'])
def mycontent():
    user_id = request.args.get('userId')
    user = get_user_by_id(user_id)
    # find documents of particular user from mcqgen table
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM mcqgen WHERE userId = %s", (user[1],))
    mcqgen = cursor.fetchall()
    cursor.execute("SELECT * FROM subgen WHERE userId = %s", (user[1],))
    subgen = cursor.fetchall()
    cursor.close()
    print(mcqgen, subgen)
    return render_template('Content.html', user=user, mcqgen=mcqgen, subgen=subgen)








































@app.route('/Summarization', methods = ['POST','GET'])
def summarization():
    summary_output = " "
    summary_text = " "
    if(request.method == 'POST'):
        summary_text = request.form['input']
        response = summarizer(summary_text, max_length=300, min_length=30, do_sample=False)
        summary_output = response[0]['summary_text']

    return render_template('summarization.html', response=summary_output, text=summary_text)


@app.route('/Summarization/copy', methods=['POST'])
def copy_to_clipboard():
    summary_output = request.form['output']
    button_clicked = request.form['submit']
    summary_text = request.form['input']

    if button_clicked == 'Copy':
        pyperclip.copy(summary_output)
    elif button_clicked == 'Download':
        output="downloaded"
    return render_template('summarization.html', response=summary_output, text=summary_text, copied = "Copied to Clipboard")


@app.route('/GrammerCheck',methods = ['POST',"GET"])
def GrammerCheck():
    grammer_output = " "
    grammer_text = " "
    if (request.method == 'POST'):
        grammer_text = request.form['input']
        response = requests.post(API_URL1, headers=headers1, json=grammer_text)
        grammer_output = response.json()
        grammer_output = grammer_output[0]['grammer_text']
    return render_template('GrammerCheck.html', response = grammer_output, text = grammer_text)

@app.route('/mcqGen', methods=['POST','GET'])
def mcqGen():
    user_id=request.args.get('userId')
    user=get_user_by_id(user_id)
    return render_template('MCQ_Generator.html',data="",user=user)





@app.route('/mcqResult', methods=['POST', 'GET'])
def mcqRes():
    user_id = request.args.get('user_Id')
    user = get_user_by_id(user_id)
    print(user[1])
    para = request.form['text']
    num = request.form['num']
    print(para, num)
    display(para, num)
    data = pd.read_json('response.json')
    json_data1 = data.to_json(orient='records')
    json_data = json.loads(json_data1)
    print("Finally returning Response...")
    # Format the MCQs
    formatted_output = ""

    for index, question_data in enumerate(json_data):
        question = question_data["question"]
        options = question_data["options"]
        answer = question_data["answer"]

        formatted_output += f"{index + 1}. {question}\n"
        for i, option in enumerate(options):
            formatted_output += f"   {chr(97 + i)}) {option}\n"
        formatted_output += f"   Answer: {chr(97 + options.index(answer))}) {answer}\n\n"
    return render_template('MCQ_Generator.html', data=formatted_output, text=para,user=user)

@app.route('/download', methods=['POST'])
def text_to_pdf():
    user_id = request.args.get('user_Id')
    user = get_user_by_id(user_id)
    questions = pd.read_json('response.json')
    questions = questions.to_dict(orient='records')

    output_filename = "MCQs.pdf"
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    # Add questions to the content
    for index, question in enumerate(questions, start=1):
        question_text = f"{index}. {question['question']}\n"
        options_text = "\n".join([f"   {chr(97 + i)}. {option}" for i, option in enumerate(question['options'])])
        answer_text = f"Answer: {question['answer']}\n\n"
        # Add line break after each option
        options_text = options_text.replace('\n\n\n', '\n\n')
        content.append(Paragraph(question_text, styles["Normal"]))
        content.append(Paragraph(options_text, styles["Normal"]))
        content.append(Paragraph(answer_text, styles["Normal"]))
        # Add line break after each question except the last one
        if index < len(questions):
            content.append(Paragraph("<br/><br/><br/>", styles["Normal"]))

    doc.build(content)
    file_path = 'O:\DBMS_Project\MY_app\My_app\MCQs.pdf'
    documentLink = upload_pdf_to_cloudinary(file_path)

    # upload this data to mcqgen table

    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    user = get_user_by_id(user_id)
    print(user[1])
    documentName = output_filename
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO mcqgen(userId, date,time,docuemntName,documentLink) VALUES(%s,%s,%s,%s,%s)", (user[1], date, time, documentName, documentLink))
    mysql.connection.commit()
    cursor.close()
    return render_template('MCQ_Generator.html', data="Downloaded", user=user)

@app.route('/subjQues')
def subjQues():
    user_id = request.args.get('userId')
    user = get_user_by_id(user_id)
    return render_template('SubjQuestion.html', user=user)

@app.route('/subjGen', methods=['POST','GET'])
def subjGen():
    user_id = request.args.get('user_Id')
    user = get_user_by_id(user_id)
    text = request.form['text']
    num = request.form['num']
    marks = request.form['marks']
    print(text, num, marks)
    GOOGLE_API_KEY = 'AIzaSyAYPhza7RZmKSR8CHDnhV2aw9HxAEmbq3A'
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    propmt = "paragraph:"+str(text)+"i want create"+str(num)+"question with there answer using Blooms Taxonomy the question is for "+str(marks)+"marks and i want only Question on one line and Answer on other line else not need any single sentence or word & add '#' at the end of the answer of each question."
    response = model.generate_content(contents=propmt)
    print(response.text)
    # remove all '*' from the response
    out = response.text
    out = out.replace("*", "")
    # Answer text is bold
    out = out.replace("Answer:","ANS =>")
    return render_template('SubjQuestion.html',data=out, text=text,user=user)

@app.route('/subjDownload', methods=['POST','GET'])
def text_to_pdfsubj():
    user_id=request.args.get('user_Id')
    user=get_user_by_id(user_id)
    output_filename = 'output.pdf'
    input_text = request.form['output']
    print(input_text)
    # Create a PDF document
    # Create a PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter)

    i=1;

    # Define styles for the paragraphs
    styles = getSampleStyleSheet()

    # Initialize a list to store the paragraphs
    content = []

    # Split the input text into question-answer pairs
    pairs = input_text.split('#')

    # Add each question-answer pair to the content
    for pair in pairs:
        # Split the pair into question and answer
        print(pair)
        # Split the pair into question and answer
        question, _, answer = pair.partition('\nANS => ')
        question = question.replace('\n', '')
        question = question.replace('Question', '')

        print("ques = ", str(question))
        print("\nans = ", str(answer))
        # Create Paragraph objects for question and answer with appropriate styles
        question_para = Paragraph(f'<b>Question:</b> {question}', styles["Normal"])
        answer_para = Paragraph(f'<b>Answer:</b> {answer.strip()}', styles["Normal"])
        # Add question and answer to the content
        content.extend([question_para, answer_para, Spacer(1, 12)])  # Adding space between each pair
        i = i + 1
        if (i == len(pairs)):
            break

    # Build the PDF document
    doc.build(content)
    # save the pdf to cloudinary
    file_path = 'O:\DBMS_Project\MY_app\My_app\output.pdf'
    documentLink = upload_pdf_to_cloudinary(file_path)
    # upload this data to mcqgen table
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    user = get_user_by_id(user_id)
    print(user[1])
    documentName = output_filename
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO subgen(userId, date,time,docuemntName,documentLink) VALUES(%s,%s,%s,%s,%s)", (user[1], date, time, documentName, documentLink))
    mysql.connection.commit()
    cursor.close()

    return render_template('SubjQuestion.html', data="Downloaded",user=user)




app.run(debug=True)
