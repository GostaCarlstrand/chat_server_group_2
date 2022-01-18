from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
users = [{'username': 'Edvin', 'password': '1234'}]


@app.get('/authenticate')
def authenticate():
    return render_template("authenticate.html")


@app.post('/authenticate')
def authenticate_post_login():
    username = request.form['user_name']
    password = request.form['password']

    for user in users:
        if user['username'] == username and user['password'] == password:
            return redirect(url_for('user_login'))
    return render_template("unauthorized.html")


@app.get('/create_user')
def user_post():
    return render_template("create_user.html")


@app.get('/authenticate/login')
def user_login():
    return render_template("login.html")


@app.get('/authenticate/create_user')
def user_create_user():
    return render_template("create_user.html")


if __name__ == "main":
    app.run(port=4879)