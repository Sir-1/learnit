import sqlite3
from flask import Flask, Response, render_template, abort, request

app = Flask(__name__)


def do_query(query, data, fetch):
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    cur.execute(query, data)
    if fetch is None:
        result = cur.fetchall()
    else:
        result = cur.fetchone()
    conn.close()
    return result


@app.route("/")
def main():
    posts = do_query("""SELECT Post.id,Post.title, Post.content,
                            Post.Text, Post.Usefulness, User.name,
                            classroom.name from Post join user ON Post.Uid =
                            User.id join classroom ON Post.Cid = classroom.id;
                            """, (), None)
    print(posts)
    classes = do_query("select name from classroom;", (), None)
    return render_template("main.html", title="main", stuff=posts,
                           classrooms=classes)


@app.route("/classroom/<ClassID>")
def classrooms(ClassID):
    posts = do_query("""SELECT Post.id,Post.title, Post.content,
                            Post.Text, Post.Usefulness, User.name,
                            classroom.name from Post join user ON Post.Uid =
                            User.id join classroom ON Post.Cid = classroom.id
                            where cid = ?;
                            """, (ClassID,), None)
    classroom = do_query("select * from classroom where id=?", (ClassID,), 1)
    return render_template("classroom.html", stuff=posts, info=classroom)


if __name__ == "__main__":
    app.run(debug=True)
