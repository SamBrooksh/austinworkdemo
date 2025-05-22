from flask import Flask, redirect, url_for, request, render_template, jsonify
from email.message import EmailMessage 
import json
import smtplib
import os
from copy import deepcopy
from sqlbackend import client, add_job

app = Flask(__name__)

database ={}

def get_updated_database():
    global database
    with open("configfiles/information.json") as json_file:
        database = json.load(json_file)

get_updated_database()

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
        id = str(id)    #So that it is json valid - shouldn't need the actual number value....
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
    personal = {}
    updated_dict = {}
    for key in given_dict:
        if "client" in key:
            personal[key] = given_dict[key]
            #Should pull it out as well - probably should be specific... 
        else:
            updated_dict[key] = given_dict[key]
    print(personal, updated_dict)
    return personal, updated_dict

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

prev_func = ""
def recurse_compute_func(func_name:str, var_dict:dict, functions:dict)->dict:
    global prev_func
    expr = database['functions'][func_name]
    if prev_func == func_name:
        raise ValueError(f"{prev_func}\n{var_dict}\n{functions}\n{expr}\n")
    prev_func = func_name
    if func_name in var_dict:
        return var_dict
    
    # Current error where if const has a partial match of function it breaks 
    # ex const: concrete_found_expedited_const - Functions concrete_found_expedited
    # Make the dict comprehension grab exact word matches
    var_dict.update({k: recurse_compute_func(k, var_dict, functions) for k in functions if k in expr and k not in var_dict})
    for k in var_dict:
        #print(f"{k} : {var_dict[k]} : {expr}")
        expr = expr.replace(k, str(var_dict[k]))
        #print(f"new expr = {expr}")

    var_dict[func_name] = str(eval(expr, None, var_dict))
    var_dict['FUNC_DEF_USED_'+func_name] = database["functions"][func_name]
    # May want to pull all of these out and place in their own - so that there isn't redundancy with this part.
    # Not very important though
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
    running_total = 0
    for job in cat:
        for subjob in cat[job]:
            #Should handle decimals better here
            subtotal, result_vars = get_job_cost(cat[job][subjob], job)
            result[job][subjob]['result_vars'] = result_vars
            result[job][subjob]['use_cost'] = subtotal
            running_total += subtotal
            #print(f"Subtotal: {subtotal}")
    result['TOTAL_COST'] = running_total
    print(f"FINAL DICT - {result}")
    client_obj = client(**personal_data)
    add_job(result, client_obj)
    #Need to make client object 


@app.route('/concretefoundation')
def get_new_concretefoundation():
    get_updated_database()
    concretefoundationindex = request.args.get('concretefoundationindex', type=int)
    return render_template('foundation.html', database=database, concretefoundationindex=concretefoundationindex)

@app.route('/gutters')
def get_new_gutters():
    get_updated_database()
    guttersindex = request.args.get('guttersindex', type=int)
    return render_template('gutters.html', database=database, guttersindex=guttersindex)


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
    