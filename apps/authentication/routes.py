# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from flask_dance.contrib.github import github
# from check.checker import check_card
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from flask import jsonify
from apps.authentication.util import verify_pass
import json
import time
import random
import requests
import threading
# import jsonify

user_semaphores = {}
def find_between( data, first, last ):
    try:
        start = data.index( first ) + len( first )
        end = data.index( last, start )
        return data[start:end]
    except ValueError:
        return None

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route("/github")
def login_github():
    """ Github login """
    if not github.authorized:
        return redirect(url_for("github.login"))

    res = github.get("/user")
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        user_id  = request.form['username'] # we can have here username OR email
        password = request.form['password']

        # Locate user
        user = Users.find_by_username(user_id)

        # if user not found
        if not user:

            user = Users.find_by_email(user_id)

            if not user:
                return render_template( 'accounts/login.html',
                                        msg='Unknown User or Email',
                                        form=login_form)

        # Check the password
        if verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)
#     isallowed = Users.check_allowed(user_id)
    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


@blueprint.route('/gate1', methods=['POST'])
def gate1():
    gate = ['gate1', 'gate2', 'gate3', 'gate4', 'gate5', 'gate6', 'gate7', 'gate8', 'gate9']   
    gate = random.choice(gate)
    print(gate)
    value = request.form.get('value')
    reqUrl = f"https://str1pe-{gate}.up.railway.app/runserver/"
    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Content-Type": "application/json" 
    }


    
    payload = json.dumps({"card": value})
    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
    time.sleep(1)
    message = find_between(response.text, '"message":"', '"')
    # message = response.json()['message']
    print(response.text)
    print(value)
    return f"{value}  =>  {message}" 
    # Render the form template for GET requests
    
    
@blueprint.route('/gate2', methods=['POST'])
def gate2():
#     gate = ['gate1', 'gate2', 'gate3', 'gate4', 'gate5', 'gate6', 'gate7', 'gate8', 'gate9']   
#     gate = random.choice(gate)
#     print(gate)
    value = request.form.get('value')
    reqUrl = "https://cvv-fdata1.up.railway.app/runserver/"
    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Content-Type": "application/json" 
    }
    
    payload = json.dumps({"card": value})
    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
    time.sleep(1)
    message = find_between(response.text, '"message":"', '"')
    # message = response.json()['message']
    print(response.text)
    print(value)
    return f"{value}  =>  {message}" 
    # Render the form template for GET requests
   
@blueprint.route('/gate3', methods=['POST'])
def gate3():
    userid = request.form.get('user_id')
    # userid = current_user.get_id()
    semaphore = user_semaphores.setdefault(userid, threading.Semaphore(5))
    semaphore.acquire()
    try:
        # gate = ['fortis1', 'fortis2', 'fortis3', 'fortis4', 'fortis5', 'fortis6', 'fortis7', 'fortis8', 'fortis9', 'fortis10', 'fortis11', 'fortis12', 'fortis13']
        # gate = random.choice(gate)
        # print(gate)
        value = request.form.get('value')
        # reqUrl = f"https://CVV-{gate}.up.railway.app/runserver/"
        reqUrl = "https://charge-fortis1.up.railway.app/runserver/"
        headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Content-Type": "application/json" 
        }
        
        payload = json.dumps({"userinfo": "your_user_info_here",
                              "remarks": "your_remarks_here",
                              "card": value})
        response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
        time.sleep(1)
        message = find_between(response.text, '"message":"', '"')
    
    finally:
        semaphore.release()
    # message = response.json()['message']
    print(response.text)
    print(value)
    return f"{value}  =>  {message}" 
    # Render the form template for GET requests
