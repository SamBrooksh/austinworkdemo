from flask import Flask, redirect, url_for, request, render_template, jsonify
from email.message import EmailMessage 
import json
import smtplib
import os
from copy import deepcopy

app = Flask(__name__)

database ={}

def get_updated_database():
    with open("information.json") as json_file:
        database = json.load(json_file)

def strip_number_from_key(key: str)->tuple[str, int]:
    end = len(key) - 1
    while key[end].isdigit(): #Should add that end shouldn't get below 0
        end -= 1
    return (key[:end+1], int(key[end+1:]))

def get_job(sub_key:str, delimit: str)->str:
    temp_key = sub_key.lower()
    while delimit in temp_key:
        temp_key = '-'.join(temp_key.split(delimit)[:-1])
        if temp_key in database and database[temp_key] == 'job':
            return temp_key
    #I need to handle Personal Data first
    return None

#For safety sake should santitze all values... Not sure how to really do this yet
def sanitize(given_dict)->dict:
    print("DID NOT SANITIZE - HAVENT IMPLED YET")
    return given_dict

#Change all of the various responses to be sorted together in a list of it's type
#It will return a list of each quality with the values in it 
#Sorted as dict of JOBS of ID's in job
def categorize(given_dict)->dict:
    new_dict = {}
    for key, value in given_dict.items():
        new_key, id = strip_number_from_key(key)

        job = get_job(new_key, '-')
        if job not in new_dict:
            new_dict[job] = {id : {new_key: value}}
        elif id not in new_dict[job]:
            new_dict[job][id] = {new_key: value}
        else:
            new_dict[job][id][new_key] = value
    return new_dict

def get_personal_data(given_dict: dict)->tuple[dict, dict]:
    print("Getting personal data not yet implemented!")
    return {}, given_dict

def get_job_functions(job)->list[str]:
    function_names = []
    for key in database['functions']:
        if job in key:
            function_names.append(key)
    return function_names

def get_job_constants(job:str)->dict:
    consts = {}
    for key in database['consts']:
        if job in key:
            consts[key] = database['consts'][key]
    return consts

def recurse_compute_func(func_name:str, var_dict:dict, functions:dict)->dict:
    if func_name in var_dict:
        return var_dict
    expr = database['functions'][func_name]
    var_dict.update({k: recurse_compute_func(k, var_dict, functions) for k in functions if k in expr and k not in var_dict})
    for k in var_dict:
        #print(f"{k} : {var_dict[k]} : {expr}")
        expr = expr.replace(k, str(var_dict[k]))
        #print(f"new expr = {expr}")

    var_dict[func_name] = str(eval(expr, None, var_dict))
    return var_dict

#Adds multiple items to the dict, and returns this subtotal
# different costs, and the one used - which is the number returned
def get_job_cost(given_dict: dict, job:str)->tuple[int, dict]:
    useable_functions = get_job_functions(job.replace('-', '_'))
    computed_variables = {}
    #Save the given values
    for key in given_dict:
        #print(key, given_dict[key])
        if key[0].isupper():
            if given_dict[key] == 'on': #Change booleans to true or false
                computed_variables[key] = "1"
            elif given_dict[key] == 'off':
                computed_variables[key] = "0"
            else:
                computed_variables[key] = given_dict[key]
        elif key in database and "cost" in database[key]['values'][given_dict[key]]:
            computed_variables[key] = str(database[key]['values'][given_dict[key]]['cost'])
    
    #print(f"in get job cost - JOB: {job} \ngiven_dict: {given_dict}\nuseable_functions: {useable_functions}\ncomputed_variables: {computed_variables}")
    #I may want to have a way to overwrite the current consts being used on the fly - not implemented though
    computed_variables.update(get_job_constants(job.replace('-','_')))
    check = []
    for func in useable_functions:
        if 'cost' in func:
            check.append(func)
        if func not in computed_variables:
            computed_variables.update(recurse_compute_func(func, computed_variables, useable_functions))
    
    use = float(computed_variables[min(check, key=lambda x : float(computed_variables[x]))])
    print(f"FINAL: use: {use} - variables : {computed_variables}")
    return use, computed_variables
    

def handle_data(given_dict)->str:
    #I need to know how to handle the boolean values - if they shoudl apply or not in some way and how to identify that
    sanit = sanitize(given_dict)
    personal_data, sanit = get_personal_data(sanit)
    cat = categorize(sanit)
    #Can easily and safely work with these now
    result = deepcopy(cat)
    for job in cat:
        for subjob in cat[job]:
            subtotal, result_vars = get_job_cost(cat[job][subjob], job)
            result[job][subjob]['result_vars'] = result_vars
            result[job][subjob]['use_cost'] = subtotal
            print(f"Subtotal: {subtotal}")
    print(f"FINAL DICT - {cat}")


@app.route('/concretefoundation')
def get_new_concretefoundation():
    get_updated_database()
    concretefoundationindex = request.args.get('concretefoundationindex', type=int)
    return render_template('foundation.html', database=database, concretefoundationindex=concretefoundationindex)

@app.route('/test/<file>')
def templatefile(file):
    get_updated_database()
    return render_template(file, database=database)


@app.route('/', methods=['GET', 'POST'])
def step_one():
    get_updated_database()
    if request.method == 'GET':
        return render_template("base.html", database=database, concretefoundationindex=1)
    elif request.method == 'POST':
        # Each category won't neccessarily start at 1
        data = request.form
        response = handle_data(data)
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
    