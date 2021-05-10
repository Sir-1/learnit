import sqlite3
from flask import Flask, Response, render_template, abort, request

app = Flask(__name__)


@app.route("/")
def main():
    conn = sqlite3.connect("learnit.db")
    cursor = conn.cursor()
    posts = cursor.execute("""SELECT Post.id,Post.title, Post.content,
                            Post.Text, Post.Usefulness, User.name,
                            classroom.name from Post join user ON Post.Uid =
                            User.id join classroom ON Post.Cid = classroom.id;
                            """)
    return render_template("main.html", title="main", stuff=posts)


if __name__ == "__main__":
    app.run(debug=True)
