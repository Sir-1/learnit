import sqlite3
from flask import Flask, Response, render_template, abort, request

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("main.html", title="main")


if __name__ == "__main__":
    app.run(debug=True)
