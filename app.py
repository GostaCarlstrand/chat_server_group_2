from flask import Flask, Response, render_template, request, redirect, url_for

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
