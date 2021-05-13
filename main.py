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
    posts = cursor.fetchall()
    classes = cursor.execute("select name from classroom;")
    return render_template("main.html", title="main", stuff=posts,
                           classrooms=classes)


@app.route("/classroom/<ClassID>")
def classrooms(ClassID):
    conn = sqlite3.connect("learnit.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT Post.id,Post.title, Post.content,
                            Post.Text, Post.Usefulness, User.name,
                            classroom.name from Post join user ON Post.Uid =
                            User.id join classroom ON Post.Cid = classroom.id
                            where cid = ?;
                            """, (ClassID,))
    posts = cursor.fetchall()
    classroom = cursor.execute("""select * from classroom where id =
                               ?""", (ClassID,))
    classroom = cursor.fetchone()
    print(classroom, ClassID)
    return render_template("classroom.html", stuff=posts, info=classroom)


if __name__ == "__main__":
    app.run(debug=True)
