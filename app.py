from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.get('/authenticate')
def authenticate():
    return render_template("authenticate.html")


@app.get('/authenticate/login')
def user_login():
    return render_template("login.html")


@app.get('/authenticate/create_user')
def user_create_user():
    return render_template("create_user.html")


@app.post('/authenticate')
def user_post():
    return redirect(url_for('user_get'))

