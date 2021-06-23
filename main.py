import sqlite3
from flask import (Flask, Response, render_template, abort, request, session, redirect, url_for,flash)
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = """b'(\x9a^\xde\xf8tZm_/&?X\xeb\x00\xda'"""
UPLOAD_FOLDER = './static/images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_filename(filename):
    return "." in filename and filename.rsplit(".", 1).lower() in ALLOWED_EXTENSIONS


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
    name = ''
    id = 0
# if there is a user signed in fetch their information feom the database
    if session.get("_User") is None:
        posts = do_query("""SELECT Post.id,Post.title, Post.content,
                        Post.Text, Post.Usefulness, User.name,
                        classroom.name,Cid from Post join user ON
                        Post.Uid=User.id join classroom ON Post.Cid =
                        classroom.id order by Post.id DESC;""", (), None)
        classes = do_query("""SELECT name, id from classroom""", (), None)
# if there is no user logged in fetch all the
# general information from the database
    else:
        id = session["_User"]
        posts = do_query("""SELECT Post.id,Post.title, Post.content, Post.Text,
                        Post.Usefulness, Post.Uid, classroom.name,
                        User_Classroom.Cid from User
                        Join User_Classroom ON User.id = User_Classroom.Uid
                        JOIN classroom ON User_Classroom.Cid = classroom.id
                        JOIN Post ON classroom.id = Post.Cid
                        WHERE User.id = ? order by Post.id DESC""",
                         (int(session["_User"]),), None)
        names = do_query("""SELECT User.name from Post join User on User.id =
                            Post.Uid WHERE Post.Cid in
                            (SELECT Cid from User_Classroom Where Uid = 1)""",
                         (), None)
        print(names)
        for i in range(len(posts)):
            posts[i] = list(posts[i])
        try:
            for i in range(len(names)):
                print(posts[i][5])
                posts[i][5] = names[i][0]

        except Exception as error:
            print(error)
        classes = do_query("""select classroom.name, id from User_Classroom
                            join classroom ON classroom.id = Cid WHERE Uid = ?;
                            """, (int(session["_User"]),), None)
        name = do_query("SELECT name from User where id = ?",
                        (session["_User"],), "fetch")

    return render_template("main.html", title="main", stuff=posts, classrooms=
                           classes, uid=id, user_name=name)


@app.route("/classroom/<ClassID>")
def classrooms(ClassID):
    name = ''
    id = 0
    # collect all of the posts within a classroom and open the classsroom page
    posts = do_query("""SELECT Post.id,Post.title, Post.content,
                            Post.Text, Post.Usefulness, User.name,
                            classroom.name,Cid from Post join user ON Post.Uid
                            = User.id join classroom ON Post.Cid = classroom.id
                            where cid = ? order by Post.id DESC;
                            """, (ClassID,), None)
    classroom = do_query("select * from classroom where id=?", (ClassID,), 1)
    classes = do_query("select name, id from classroom;", (), None)
    if session.get("_User") is not None:
        id = session["_User"]
        classes = do_query("""select classroom.name, id from User_Classroom
                            join classroom ON classroom.id = Cid WHERE Uid = ?;
                            """, (int(session["_User"]),), None)
        name = do_query("SELECT name from User where id = ?",
                        (session["_User"],), "fetch")
    return render_template("classroom.html", stuff=posts, info=classroom,
                           classrooms=classes, user_name=name,
                           uid=id)


@app.route("/login", methods=["POST"])
def login():
    name, password = "", ""
    name, password = str(request.form.get("UserName")), str(request.form.get("Password"))
    info = do_query("""SELECT id,name,password From user where name = ?""",
                    (name,), 'hi')
    print(info)
    if info is not None:
        if str(info[2]) == str(password):
            session["_User"] = info[0]
    return redirect(url_for("main_user"))


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("_User")
    return redirect(url_for("main_user"))


@app.route("/classes")
def view_classess():
    name = ''
    my_classess = ""
    id = 0
# if there is a user signed in fetch their information feom the database
    if session.get("_User") is None:
        classes = do_query("""SELECT name, id from classroom""", (), None)
# if there is no user logged in fetch all the
# general information from the database
    else:
        id = session["_User"]
        classes = do_query("""select classroom.name, id from User_Classroom
                            join classroom ON classroom.id = Cid WHERE Uid = ?;
                            """, (int(session["_User"]),), None)
        name = do_query("SELECT name from User where id = ?",
                        (session["_User"],), "fetch")
        my_classess = do_query("""SELECT id from classroom where id in (select Cid from User_Classroom where Uid = ?)""", (session["_User"],), None)
        print(my_classess)
    posts = do_query("SELECT * from classroom", (), None)
    return render_template("ClassMenu.html", title="Classes", stuff=posts,
                           classrooms=classes, uid=id, user_name=name, myclassrooms=my_classess)


@app.route("/join_Classroom", methods=["POST"])
def join_class():
    my_classess = do_query("""SELECT id from classroom where id in (select Cid from User_Classroom where Uid = ?)""", (session["_User"],), None)
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    room = request.form.get("Join")
    if (int(room),) not in my_classess:
        cur.execute("""INSERT Into User_Classroom (Uid,Cid,Admin)
                    Values(?,?,0)""", (str(session["_User"]), str(room)))
    else:
        cur.execute("""DELETE FROM User_Classroom where Uid = ? and Cid = ?""", (session["_User"], room))
    conn.commit()
    conn.close()
    return redirect(url_for("view_classess"))


@app.route("/Post")
def Post():
    classes = do_query("""select classroom.name, Cid from User_Classroom
                        join classroom ON classroom.id = Cid WHERE Uid = ?;
                        """, (int(session["_User"]),), None)
    id = session["_User"]
    name = do_query("SELECT name from User where id = ?",
                    (session["_User"],), "fetch")
    return render_template("Post.html", title="Post", classrooms=classes,
                           uid=id, user_name=name)


@app.route("/SubmitPost", methods=["GET", "POST"])
def submit_post():
    id = []
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    # upload selected image if any
    if request.method == "POST":
        if "file1" in request.files:
            file1 = request.files["file1"]
            if file1.filename != "":
                cur.execute("select id from post order by id DESC")
                id = cur.fetchone()
                filename = file1.filename + "_" + str(int(id[0])+1)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file1.save(path)
    # add information into database
    if file1.filename == "":
        filename = None
    cur.execute("INSERT INTO Post (Uid,Cid,Topic,title,content,Text,usefulness) Values (?,?,1,?,?,?,0)", (session["_User"], request.form.get("classroom"), request.form.get("Title"), filename, request.form.get("content")))
    conn.commit()
    conn.close()
    return redirect(url_for("main_user"))


if __name__ == "__main__":
    app.run(debug=True)
