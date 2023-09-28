# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, Blueprint
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from flask_dance.contrib.github import github
from apps import db, login_manager
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from apps.authentication.util import verify_pass
import json
import random
import requests
import asyncio
import os

blueprint = Blueprint('authentication_blueprint', __name__)

def get_rotation_gates():
    GATE_LIST = os.environ.get('GATE_LIST')
    if GATE_LIST is None:
        return 'gate-001.up.railway.app'
    else:
        GATE_LIST = [item.strip() for item in GATE_LIST.split(',')]
        return random.choice(GATE_LIST)

def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
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
        user_id = request.form['username']
        password = request.form['password']
        user = Users.find_by_username(user_id)

        if not user:
            user = Users.find_by_email(user_id)
        
        if not user:
            return render_template('accounts/login.html', msg='Unknown User or Email', form=login_form)

        if verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        return render_template('accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html', form=login_form)
    
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:
        username = request.form['username']
        email = request.form['email']
        user = Users.query.filter_by(username=username).first()

        if user:
            return render_template('accounts/register.html', msg='Username already registered', success=False, form=create_account_form)

        user = Users.query.filter_by(email=email).first()
        
        if user:
            return render_template('accounts/register.html', msg='Email already registered', success=False, form=create_account_form)

        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()
        logout_user()

        return render_template('accounts/register.html', msg='User created successfully.', success=True, form=create_account_form)
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

async def process_task(value, gates):
    reqUrl = f"https://{gates}/runserver/"
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Content-Type": "application/json" 
    }
    payload = json.dumps({"userinfo": "your_user_info_here", "remarks": "your_remarks_here", "card": value})
    response = requests.post(reqUrl, data=payload, headers=headersList)
    await asyncio.sleep(1)
    message = find_between(response.text, '"message":"', '"')
    print(message)
    return value, message

async def worker(queue, results):
    while True:
        value = await queue.get()
        gates = get_rotation_gates()
        print(gates)
        result = await process_task(value, gates)
        results.append(result) 
        queue.task_done()

@blueprint.route('/gate<int:gate_number>', methods=['POST'])
async def gate(gate_number):
    value = request.form.get('value')
    queue = asyncio.Queue()
    queue.put_nowait(value)
    results = []
    worker_task = asyncio.create_task(worker(queue, results))
    await asyncio.gather(queue.join(), worker_task)
    response = ''
    for result in results:
        response += f"{result[0]} => {result[1]}\n"
    return response
