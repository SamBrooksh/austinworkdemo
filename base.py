from flask import Flask, redirect, url_for, request, render_template, jsonify
from email.message import EmailMessage 
import json
import smtplib
import os

app = Flask(__name__)

database ={}
with open("information.json") as json_file:
    database = json.load(json_file)

@app.route('/', methods=['GET', 'POST'])
def step_one():
    if request.method == 'GET':
        return render_template("foundation.html", database=database)
    elif request.method == 'POST':
        data = request.form
        print(data)
        return render_template("foundation.html")

def email_content_details(results)->str:
    choice = results.getlist("samplechoice")
    amount = 0
    for key in choice:
        print(key)
        for other_key in results.keys():
            print(other_key)
            if key in other_key and key != other_key:
                amount += int(results.get(other_key))
    #print(f"choices are {choice}")
    return f"The sample cost is {amount}"
    
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
    