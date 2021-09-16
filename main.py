
import sqlite3
from flask import (Flask, render_template, request, session, redirect,
                   url_for, flash)
import os

app = Flask(__name__)
app.secret_key = """b'(\x9a^\xde\xf8tZm_/&?X\xeb\x00\xda'"""
UPLOAD_FOLDER = './static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1000*1000*15


def allowed_filename(filename):
    return "." in filename and filename.rsplit(".", 1).lower() in ALLOWED_EXTENSIONS


def hash(password):
    # returns a hashed string of the input
    edit = []
    edit += password
    for i in range(len(edit)):
        edit[i] = str(ord(edit[i]))
    password = ''.join(edit)
    password = int(((int(password)/10)**0.5 * int(password) % 1000.5)**5)
    return password


def do_query(query, data, fetch):
    # returns the result from an sql query
    # query is a string data is a tuiple and fetch is a boolien
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
    # main home page route
    name = ''
    id = 0
    saved = []
# if there is a user signed in fetch their information feom the database
    if session.get("_User") is None:
        posts = do_query("""SELECT Post.id,Post.title, Post.content,
                        Post.Text, Post.Usefulness, User.name,
                        classroom.name,Cid from Post join user ON
                        Post.Uid=User.id join classroom ON Post.Cid =
                        classroom.id order by Post.id DESC;""", (), None)
        classes = do_query("""SELECT name, id from classroom""", (), None)
# if there is no user logged in fetch all the
# collect general information from the database
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
        saved = do_query(
            "SELECT pid from saved_post where uid = ?", (id,), None)
        print(saved)
        names = do_query("""SELECT User.name from Post join User on User.id =
                            Post.Uid WHERE Post.Cid in
                            (SELECT Cid from User_Classroom Where Uid = ?)
                            order by Post.id DESC""",
                         (int(session["_User"]),), None)
        # replace user ids with names
        for i in range(len(posts)):
            posts[i] = list(posts[i])
        try:
            for i in range(len(names)):
                posts[i].append(posts[i][5])
                posts[i][5] = names[i][0]

        except Exception:
            pass
        classes = do_query("""select classroom.name, id from User_Classroom
                            join classroom ON classroom.id = Cid WHERE Uid = ?;
                            """, (int(session["_User"]),), None)
        name = do_query("SELECT name from User where id = ?",
                        (session["_User"],), "fetch")
    # redirect to different page if user isn't in any classess
    if classes == [] and session["_User"] is not None:
        return redirect(url_for("view_classess"))
    return render_template("main.html", title="main", stuff=posts,
                           classrooms=classes, uid=id, user_name=name, Saved=saved, page=0)


@app.route("/c/<ClassID>")
def classrooms(ClassID):
    # page that shows the basic classroom infromation and all its containing posts
    name = ''
    saved = []
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
        saved = do_query(
            "SELECT pid from saved_post where uid = ?", (id,), None)
        classes = do_query("""select classroom.name, id from User_Classroom
                            join classroom ON classroom.id = Cid WHERE Uid = ?;
                            """, (int(session["_User"]),), None)
        name = do_query("SELECT name from User where id = ?",
                        (session["_User"],), "fetch")
    return render_template("classroom.html", stuff=posts, info=classroom,
                           classrooms=classes, user_name=name,
                           uid=id, Saved=saved)


@app.route("/login", methods=["POST"])
def login():
    # function that gets the input of the user in the sign in form and checks
    # wether it fits their account information and signs them in
    name, password = "", ""
    name, password = str(request.form.get("UserName")), str(
        request.form.get("Password"))
    info = do_query("""SELECT id,name,password From user where name = ?""",
                    (name,), 'hi')
    if info is not None:
        if str(info[2]) == str(hash(str(password))):
            session["_User"] = info[0]
    return redirect(url_for("main_user"))


@app.route("/logout", methods=["POST"])
def logout():
    # function that makes noone signed in
    session.pop("_User")
    return redirect(url_for("main_user"))


@app.route("/c")
def view_classess():
    # page that displays teh names and desriptions of all the classrooms for people to join
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
        my_classess = do_query(
            """SELECT id from classroom where id in
            (select Cid from User_Classroom where Uid = ?)""",
            (session["_User"],), None)
    posts = do_query("SELECT * from classroom", (), None)
    return render_template("ClassMenu.html", title="Classes", stuff=posts,
                           classrooms=classes, uid=id, user_name=name, myclassrooms=my_classess)


@app.route("/join_c", methods=["POST"])
def join_class():
    # functiomn that adds a class and user to user_classroom
    my_classess = do_query(
        """SELECT id from classroom where id in
        (select Cid from User_Classroom where Uid = ?)""",
        (session["_User"],), None)
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    room = request.form.get("Join")
    if (int(room),) not in my_classess:
        cur.execute("""INSERT Into User_Classroom (Uid,Cid,Admin)
                    Values(?,?,0)""", (str(session["_User"]), str(room)))
    else:
        cur.execute(
            """DELETE FROM User_Classroom where Uid =   ? and Cid = ?""", (session["_User"], room))
    conn.commit()
    conn.close()
    return redirect(url_for("view_classess"))


@app.route("/p")
def Post():
    # page where users can create and submit posts
    # redirect anonomus users
    if session.get("_User") is None:
        return redirect(url_for("main_user"))
    # get teh required information for creating a post
    classes = do_query("""select classroom.name, Cid from User_Classroom
                        join classroom ON classroom.id = Cid WHERE Uid = ?;
                        """, (int(session["_User"]),), None)
    id = session["_User"]
    name = do_query("SELECT name from User where id = ?",
                    (session["_User"],), "fetch")
    return render_template("Post.html", title="Post", classrooms=classes,
                           uid=id, user_name=name)


@app.route("/SubmitPost", methods=["POST"])
def submit_post():
    # function that verafies and stores saved posts
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
    elif(file1.filename.rsplit(".")[1].lower() not in ALLOWED_EXTENSIONS):
        return redirect(url_for("Post"))
    if request.form.get("Title") == "":
        return redirect((url_for("Post")))
    if filename is None and request.form.get("conent"):
        return redirect(url_for("Post"))
    cur.execute("""INSERT INTO Post (Uid,Cid,Topic,title,
                content,Text,usefulness)
                Values (?,?,1,?,?,?,0)""",
                (session["_User"], request.form.get("classroom"),
                 request.form.get("Title"), filename,
                 request.form.get("content")))
    conn.commit()
    conn.close()
    return redirect(url_for("main_user"))


@app.route("/sign-up")
def sign_up():
    # page that allows people to input a username and passwrod to join the website
    id = 0
    classes = do_query("select name,id from classroom order by id", (), None)
    name = ''
    return render_template("signUp.html", title="sign up", classrooms=classes,
                           uid=id, user_name=name, login="1")


@app.route("/make_User", methods=["POST"])
def make_User():
    # verification and storage of new users submited from the user sign up page
    thing = []
    # check account is valid and return error messages
    password = request.form.get("password1")
    passwordc = request.form.get("password2")
    if request.form.get("userName") == '' or request.form.get("userName") is None:
        flash("sorry no name has been given")
        return redirect(url_for("sign_up"))
    names = do_query("select name from User", (), None)
    for i in names:
        thing.append(str(i[0]))
    if (str(request.form.get("userName")) not in thing):
        if password != passwordc or password == "":
            flash("sorry password and confimation are different")
            return redirect(url_for("sign_up"))
        # add user into the database
        conn = sqlite3.connect("learnit.db")
        cur = conn.cursor()
        cur.execute("""insert into User (name,description,password)
                    values (?,?,?)""",
                    (str(request.form.get("userName")),
                     request.form.get("description"), hash(password)),)
        conn.commit()
        conn.close()
        # sign in user automatically
        user = do_query("select id from User where name = ?",
                        (str(request.form.get("userName")),), "hte")
        session["_User"], = user
        return redirect(url_for("main_user"))
    else:
        flash("sorry username is already taken")
        return redirect(url_for("sign_up"))
    return redirect(url_for("sign_up"))


@app.route("/make_C")
def make_class_screen():
    # page that allows users to make classrooms
    # checks if they are allowed to be on the page
    if session.get("_User") is None:
        return redirect(url_for("main_user"))
        # gets info needed for the page
    classes = do_query("""select classroom.name, Cid from User_Classroom
                        join classroom ON classroom.id = Cid WHERE Uid = ?;
                        """, (int(session["_User"]),), None)
    id = session["_User"]
    name = do_query("SELECT name from User where id = ?",
                    (session["_User"],), "fetch")
    return render_template("makeClass.html", title="Create Class",
                           classrooms=classes, uid=id, user_name=name)


@app.route("/create_c", methods=["POST"])
def make_c():
    # function that makes and veragies classrooms
    # gets the required information
    name = request.form.get("Title")
    Desription = request.form.get("content")
    names = do_query("SELECT name from classroom", (), None)
    # verafies that the classroom is valid
    if name == '' or name is None:
        flash("please input a name")
        return redirect(url_for("make_class_screen"))
    if (name,) in names:
        flash("sorry that class already exists")
        return redirect(url_for("make_class_screen"))
    if Desription == '' or Desription is None:
        flash("please input a description")
        return redirect(url_for("make_class_screen"))
    # adds classroom to database
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    cur.execute("insert into classroom (name,description) values (?,?)",
                (str(name), str(Desription)),)
    conn.commit()
    # ads user to classroom as the admin
    classid = do_query(
        "select id from classroom where name = ?", (name, ), "hello")
    cur.execute("insert into User_Classroom (Uid,Cid,Admin) Values(?,?,?)",
                (int(session["_User"]), int(classid[0]), 1))
    conn.commit()
    conn.close()
    return redirect(url_for("main_user"))


@app.route("/save_post", methods=["POST"])
def save_post():
    # function that saves a post in the database gets called by javascript
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    # checks if post saved in database and removes or adds it
    cur.execute(
        "select pid from saved_post where uid = ?", (session["_User"],))
    t = cur.fetchall()
    posts = [str(i[0]) for i in t]
    x = request.form.get("Pid")
    if str(x) in posts:    # removes from database
        cur.execute("delete from saved_post where uid = ? and pid = ?",
                    (session["_User"], x))
    else:     # adds to database
        cur.execute("insert into saved_post (uid,pid) values (?,?)",
                    (str(session["_User"]), str(x)))
    conn.commit()
    conn.close()
    return "true"


@app.route("/delete", methods=["POST"])
def delete():
    # function that deletes a post if correct user is signed in
    # gets called by javascript
    conn = sqlite3.connect("learnit.db")
    cur = conn.cursor()
    cur.execute("Delete from Post where id = ? and uid = ?",
                (request.form.get("delete"), session["_User"]))
    conn.commit()
    conn.close()
    return "true"


@app.route("/saved")
def saved():
    # page that displays to teh user all of their saved Posts
    # checks if user allowed on page
    if session.get("_User") is None:
        return redirect(url_for("main_user"))
    # gets required information from database
    saved = do_query(
        "SELECT pid from saved_post where uid = ?", (session["_User"],), None)
    Classrooms = do_query(
        """select * from classroom where id in
        (select Cid from User_Classroom where Uid = ?)""",
        (session["_User"],), None)
    id = session["_User"]
    name = do_query("select name from User where id = ?", (id,), "fetch")
    classnames = do_query(
        """select name,id from classroom where id in
        (select Cid from User_classroom where Uid = ?) order by id""",
        (session["_User"],), None)
    Posts = do_query(
        """SELECT Post.id, Post.title, Post.content, Post.Text, User.name,
        classroom.id, classroom.name from Post Join
        User on Post.Uid = User.id Join classroom on
        Post.Cid = classroom.id where Post.id in
        (Select Pid from saved_post where Uid = ?) order by -Post.id""",
        (session["_User"],), None)
    return render_template("saved.html", classrooms=classnames, title="saved",
                           stuff=Classrooms, uid=id, user_name=name, page=1,
                           post=Posts, Saved=saved)


if __name__ == "__main__":
    # runs app
    app.run(debug="true")
