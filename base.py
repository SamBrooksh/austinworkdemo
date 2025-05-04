from flask import Flask, redirect, url_for, request, render_template, jsonify
from email.message import EmailMessage 
import smtplib
import os

app = Flask(__name__)

choices = ["Test", "Test2"]

@app.route('/', methods=['GET', 'POST'])
def step_one():
    if request.method == 'GET':
        return render_template("fill.html", checkboxes=choices)
    elif request.method == 'POST':
        data = request.form
        print(data)
        to = data.get('email')
        email_msg = email_content_details(data)
        subject = "Sample Subject"
        send_email(email_msg, subject, to)
        return render_template("fill.html", checkboxes=choices)

def email_content_details(results)->str:
    pass 

def send_email(details, subject, to):
    msg = EmailMessage()
    msg.set_content(details)
    msg['Subject'] = subject
    sender = "samhtestingemail@gmail.com"
    msg['From'] = sender
    msg['To'] = to
    password = os.environ.get("EMAIL_PASSWORD")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg) 
        # Should probably send msg to self or the like to make a record

if __name__ == '__main__':
    app.run(debug=True)
    