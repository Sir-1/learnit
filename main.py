import sqlite3
from flask import Flask, Response, render_template, abort, request, session

app = Flask(__name__)
app.secret_key = """b'(\x9a^\xde\xf8tZm_/&?X\xeb\x00\xda'"""


def do_query(query, data, fetch):
    # connect to the database
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    cur.execute(query, data)
    # bases on info fetch either one or all items
    if fetch is None:
        result = cur.fetchall()
    else:
        result = cur.fetchone()
    conn.close()
    return result


@app.route("/")
def main_user():
    session["_User"] = 0
# if there is a user signed in fetch their information feom the database
    if session["_User"] == 0:
        posts = do_query("""SELECT Post.id,Post.title, Post.content,
                        Post.Text, Post.Usefulness, User.name,
                        classroom.name,Cid from Post join user ON
                        Post.Uid=User.id join classroom ON Post.Cid =
                        classroom.id;""", (), None)
        classes = do_query("""SELECT name, id from classroom""", (), None)
# if there is no user logged in fetch all the
# general information from the database
    else:
        posts = do_query("""SELECT Post.id,Post.title, Post.content, Post.Text,
                        Post.Usefulness, Post.Uid, classroom.name,
                        User_Classroom.Cid from User
                        Join User_Classroom ON User.id = User_Classroom.Uid
                        JOIN classroom ON User_Classroom.Cid = classroom.id
                        JOIN Post ON classroom.id = Post.Cid
                        WHERE User.id = ?""",
                         (int(session["_User"]),), None)
        classes = do_query("""select classroom.name, id from User_Classroom join
                            classroom ON classroom.id = Cid WHERE Uid = ?;""",
                           (int(session["_User"]),), None)
    return render_template("main.html", title="main", stuff=posts,
                           classrooms=classes, uid=session["_User"])


@app.route("/classroom/<ClassID>")
def classrooms(ClassID):
    # collect all of the posts within a classroom and open the classsroom page
    posts = do_query("""SELECT Post.id,Post.title, Post.content,
                            Post.Text, Post.Usefulness, User.name,
                            classroom.name,Cid from Post join user ON Post.Uid
                            = User.id join classroom ON Post.Cid = classroom.id
                            where cid = ?;
                            """, (ClassID,), None)
    classroom = do_query("select * from classroom where id=?", (ClassID,), 1)
    classes = do_query("select name, id from classroom;", (), None)
    return render_template("classroom.html", stuff=posts, info=classroom,
                           classrooms=classes)


if __name__ == "__main__":
    app.run(debug=True)
