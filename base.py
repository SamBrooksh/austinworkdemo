from flask import Flask, redirect, url_for, request, render_template, jsonify
from email.message import EmailMessage 
import json
import smtplib
import os

app = Flask(__name__)

database ={}
with open("information.json") as json_file:
    database = json.load(json_file)

#Change all of the various responses to be sorted together in a list of it's type
#It will return a list of each quality with the values in it 
def categorize(dict)->dict:
    pass


@app.route('/concretefoundation')
def get_new_concretefoundation():
    concretefoundationindex = request.args.get('concretefoundationindex', type=int)

    return render_template('foundation.html', database=database, concretefoundationindex=concretefoundationindex)

@app.route('/test/<file>')
def templatefile(file):
    return render_template(file, database=database)


@app.route('/', methods=['GET', 'POST'])
def step_one():
    if request.method == 'GET':
        return render_template("base.html", database=database, concretefoundationindex=1)
    elif request.method == 'POST':
        # Each category won't neccessarily start at 1...
        data = request.form
        print(data)
        return data


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
    