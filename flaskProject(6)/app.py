import os

from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, join_room, leave_room

from manager import *
from sendemaik import *


def enPassWord(password):
    return generate_password_hash(password)


def checkPassWord(enpassword, password):
    return check_password_hash(enpassword, password)


app = Flask(__name__)

create_tables_in_database()

app.secret_key = "123sdr23"
socketio = SocketIO()
socketio.init_app(app)

online_user = []
room_user = {}


class resetuser():
    username = None
    code = None


@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        user = request.form.to_dict()
        result = user['search']
        article = search_article(result)
        article = sorted(article, key=lambda article: article[7], reverse=True)
        return render_template('searchresult.html', name=username, article=article)


@app.route('/change', methods=['GET', 'POST'])
def change():
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        if len(search_user_picture(username)) > 0:
            p = 1
            pic = show_picture()
        else:
            p = 0
            pic = None
        return render_template('personalinformation.html', name=username, pic=pic, p=p)


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        if not session.get("username"):
            return redirect("/login")
        else:
            username = session.get("username")
            file = request.files.get("image")
            file_name = file.filename.replace(" ", "")
            file.save(os.path.dirname(__file__) + '/upload/' + file_name)
            if len(search_user_picture(username)) == 0:
                insert_image(username, file_name)
            else:
                delete_user_picture(username)
                insert_image(username, file_name)
            user = request.form.to_dict()
            major = user['major']
            birthday = user['birthday']
            add_users_information(username, "major", major)
            add_users_information(username, "birthday", birthday)
            return redirect("/user")

    if request.method == 'GET':
        if not session.get("username"):
            return redirect("/login")
        else:
            username = session.get("username")
            li = search_user(username)
            long = len(list_all_follower(username))
            if len(search_user_picture(username)) > 0:
                p = 1
                pic = show_picture()
            else:
                p = 0
                pic = None
            return render_template('blankinformation.html', long=long, name=username, list=li, pic=pic, p=p)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if not session.get("username"):
        return redirect("/login")
    else:
        return render_template('submit.html', name=session.get("username"))


@app.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'GET':
        if not session.get("username"):
            return redirect("/login")
        else:
            username = session.get("username")
            article = search_author(username)
            return render_template('history.html', name=username, article=article)
    if request.method == 'POST':
        user = request.form.to_dict()
        title = user['title']
        text = user['text']
        plates = user['plates']
        username = session.get("username")
        insert_article_in_database(username, title, text, plates)
        article = search_author(username)
        return render_template('history.html', name=username, article=article)


@app.route('/postsuccess/<x>', methods=['GET', 'POST'])
def post(x):
    if not session.get("username"):
        return redirect("/login")
    else:
        user = request.form.to_dict()
        title = user['title']
        text = user['text']
        change_article_in_database(x, title, text)
        return redirect("/history")


@app.route('/', methods=['GET', 'POST'])
def home():  # put application's code here
    if request.method == 'POST':
        user = request.form.to_dict()
        name = user['user']
        password = user['pass']
        if check_username(name):
            t = get_password(name)
            if check_password_hash(t, password):
                session["username"] = name

                return render_template("searchpage.html", name=session.get("username"))
            else:
                return render_template("wrong.html")
        else:
            return render_template("wrong.html")

    if request.method == 'GET':
        if not session.get("username"):
            return redirect("/login")
        else:
            return render_template('searchpage.html', name=session.get("username"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('loginpage.html')

    if request.method == 'POST':
        user = request.form.to_dict()
        name = user['username']
        password = enPassWord(user['password'])
        email = user['email']
        if check_username(name):
            return render_template("wrong.html")
        else:
            insert_user(name, password, email)
            return render_template("loginpage.html")


@app.route('/register', methods=['GET', 'POST'])
def inter():
    return render_template('registerpage.html')


@app.route('/lost', methods=['GET', 'POST'])
def lost():
    return render_template('findpassword.html')


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'GET':
        return render_template('resetpassword.html')
    if request.method == 'POST':
        user = request.form.to_dict()
        code = user['text']
        code0 = resetuser.email
        if code == code0:
            return render_template('resetpassword.html')
        else:
            return render_template('findpassword.html')


@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'GET':
        return render_template('emailcode.html')
    if request.method == 'POST':
        user = request.form.to_dict()
        name = user['username']
        email = search_email(name)
        code = try_send(email)
        resetuser.username = name
        resetuser.email = code
        return render_template('emailcode.html')


@app.route('/done', methods=['GET', 'POST'])
def done():
    if request.method == 'GET':
        return render_template('changepasswordok.html')
    if request.method == 'POST':
        user = request.form.to_dict()
        password1 = user['password1']
        password2 = user['password2']
        if password1 == password2:
            password = user['password1']
            password = enPassWord(password)
            change_password_in_database(resetuser.username, password)
            return render_template('changepasswordok.html')
        else:
            return render_template("wrong.html")


@app.route('/SearchResult/<item>', methods=['GET', 'POST'])
def sea(item):
    if request.method == 'GET':
        if not session.get("username"):
            return redirect("/login")
        else:
            username = session.get("username")
            title = search_id_title(item)
            content = search_id_content(item)
            comment = return_comments_of_article(item)
            author = search_id_author(item)
            p, pic = read_pictures(author)
            if check_follows(username, author):
                boolean = True
            else:
                boolean = False
            add_click_count(item);
            if username == author:
                return render_template('detail.html', author=author, name=username, title=title, content=content,
                                       x=item,
                                       comment=comment, p=p, pic=pic)
            else:
                return render_template('result.html', author=author, name=username, title=title, content=content,
                                       item=item,
                                       comment=comment, boolean=boolean, p=p, pic=pic)
    else:
        user = request.form.to_dict()
        commen = user['comment']
        username = session.get("username")
        insert_comment(username, commen, item)
        title = search_id_title(item)
        content = search_id_content(item)
        author = search_id_author(item)
        p, pic = read_pictures(author)
        comment = return_comments_of_article(item)
        if check_follows(username, author):
            boolean = True
        else:
            boolean = False
        if username == author:
            return render_template('detail.html', author=author, name=username, title=title, content=content, x=item,
                                   comment=comment, p=p, pic=pic)
        else:
            return render_template('result.html', author=author, name=username, title=title, content=content, item=item,
                                   comment=comment, boolean=boolean, p=p, pic=pic)


@app.route('/deletecomment1/<item>/<floor>', methods=['GET', 'POST'])
def deletecomment1(item, floor):
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        delete_comment(item, floor)
        return redirect('/SearchResult/' + item)


@app.route('/detail/<x>', methods=['GET', 'POST'])
def detail(x):
    if request.method == 'GET':
        if not session.get("username"):
            return redirect("/login")
        else:
            username = session.get("username")
            title = search_id_title(x)
            content = search_id_content(x)
            comment = return_comments_of_article(x)
            author = search_id_author(x)
            p, pic = read_pictures(author)
            if username == author:
                return render_template('detail.html', author=author, name=username, title=title, content=content,
                                       x=x, comment=comment, p=p, pic=pic)
            else:
                if check_follows(username, author):
                    boolean = True
                else:
                    boolean = False
                return render_template('result.html', author=author, name=username, title=title, content=content,
                                       item=x, comment=comment, boolean=boolean, p=p, pic=pic)
    else:
        user = request.form.to_dict()
        commen = user['comment']
        username = session.get("username")
        insert_comment(username, commen, x)
        title = search_id_title(x)
        content = search_id_content(x)
        author = search_id_author(x)
        p, pic = read_pictures(author)
        comment = return_comments_of_article(x)
        if username == author:
            return render_template('detail.html', author=author, name=username, title=title, content=content,
                                   x=x, comment=comment, p=p, pic=pic)
        else:
            if check_follows(username, author):
                boolean = True
            else:
                boolean = False
            return render_template('result.html', author=author, name=username, title=title, content=content,
                                   item=x, comment=comment, boolean=boolean, p=p, pic=pic)


@app.route('/delete/<x>', methods=['GET', 'POST'])
def delete(x):
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        delete_article_in_database(x)
        return redirect("/history")


@app.route('/change/<x>', methods=['GET', 'POST'])
def edit(x):
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        return render_template("edit.html", x=x, name=username)


@app.route('/logout', methods=['GET', 'POST'])
def out():
    session.pop("username")
    return redirect("/")


@app.route('/changefollowes/<item>', methods=['GET', 'POST'])
def follows(item):
    if not session.get("username"):
        return redirect("/login")
    else:
        if request.method == 'POST':
            username = session.get("username")
            author = search_id_author(item)
            insert_follows(username, author)
            return redirect("/SearchResult/" + item)


@app.route('/deletefollowes/<item>', methods=['GET', 'POST'])
def defollows(item):
    if not session.get("username"):
        return redirect("/login")
    else:
        if request.method == 'POST':
            username = session.get("username")
            author = search_id_author(item)
            delete_follows(username, author)
            return redirect("/SearchResult/" + item)


@app.route('/space/<item>', methods=['GET', 'POST'])
def space(item):
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        li = search_user(item)
        article = search_author(item)
        if len(search_user_picture(item)) > 0:
            p = 1
            pic = show_picture()
        else:
            p = 0
            pic = None
        return render_template('spaceArticles.html', name=item, list=li, pic=pic, p=p, article=article)


@app.route('/spacefollows/<item>', methods=['GET', 'POST'])
def spacefollows(item):
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        li = search_user(item)
        l2 = list_all_followed(item)
        p, pic = read_pictures(item)
        l3 = []
        print(pic)
        print(l2)
        for i in l2:
            (p0, pic0) = read_pictures(i)
            l3.append([i, p0, pic0])
            print(l3)
        return render_template('spaceFollows.html', name=item, list=li, pic=pic, p=p, follows=l3)


@app.route('/spacefans/<item>', methods=['GET', 'POST'])
def spacefans(item):
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        li = search_user(item)
        l2 = list_all_follower(item)
        p, pic = read_pictures(item)
        l3 = []
        print(pic)
        print(l2)
        for i in l2:
            (p0, pic0) = read_pictures(i)
            l3.append([i, p0, pic0])
            print(l3)
        return render_template('spaceFollows.html', name=item, list=li, pic=pic, p=p, follows=l3)


@app.route('/plate/<item>', methods=['GET', 'POST'])
def plate(item):
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        article = return_articles_of_plate(item)
        return render_template('plate.html', name=username, article=article)


@app.route('/startchat', methods=['GET', 'POST'])
def startchat():
    if not session.get("username"):
        return redirect("/login")
    else:
        username = session.get("username")
        return render_template('index.html',name=username)

# # 连接
@socketio.on('connect')
def handle_connect():
    username = session.get('name')
    online_user.append(username)



# 断开连接
@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('name')

@socketio.on('send msg')
def handle_message(data):
    room = session.get('room')
    data['message'] = data.get('message').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
    socketio.emit('send msg', data, to=room)


@socketio.on('join')
def on_join(data):
    username = data.get('username')
    room = data.get('room')
    try:
        room_user[room].append(username)
    except:
        room_user[room] = []
        room_user[room].append(username)

    join_room(room)
    socketio.emit('connect info', username + '加入房间', to=room)


@socketio.on('leave')
def on_leave(data):
    username = data.get('username')
    room = data.get('room')
    room_user[room].remove(username)
    leave_room(room)
    socketio.emit('connect info', username + '离开房间', to=room)

@app.route('/chat/')
def chat():
    if 'name' in session and 'room' in session:
        username = session['name']
        room = session['room']
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'name' in session:
            return redirect(url_for('chat'))
        return render_template('index.html')
    else:
        username = request.form.get('username')
        room = request.form.get('room')
        session['name'] = username
        session['room'] = room
        return redirect(url_for('chat'))

@app.route('/leave/')
def logout():
    if 'room' in session:
        session['room']=None
        session['name'] = None
    return redirect('/')

app.run(debug=True, host='0.0.0.0', port=5000)
