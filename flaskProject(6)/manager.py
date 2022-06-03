import os

from flask import Flask, render_template, request
import base64
import sqlite3


def connect_database(db_file):
    """ Open the database and create a cursor. """
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    return conn, cur


def close_database(conn, cur):
    """ Commit and close the cursor and connection. """
    conn.commit()
    cur.close()
    conn.close()


def create_tables_in_database():
    """ Create four tables in database.sqlite, contain users, plates, articles, and comments. """
    conn, cur = connect_database('database.sqlite')

    query = '''CREATE TABLE if not exists users(
               name                 text        primary key, 
               password             text        NOT NULL,
               email                text        NOT NULL,
               major                text,
               birthday            text,
               follow_count         integer     DEFAULT 0,
               follower_count       integer     DEFAULT 0,
               article_count        integer     DEFAULT 0,
               comment_count        integer     DEFAULT 0,
               liked_count          integer     DEFAULT 0,
               collect_count        integer     DEFAULT 0,
               collected_count      integer     DEFAULT 0,
               unread_comment       integer     DEFAULT 0,
               unread_chat          integer     DEFAULT 0)'''
    cur.execute(query)

    query = '''CREATE TABLE if not exists plates(
                platename    text       primary key,
                moderator    text       NOT NULL,
                FOREIGN KEY(moderator) REFERENCES users(name))'''
    cur.execute(query)

    query = '''CREATE TABLE if not exists articles(
                id                  integer     primary key, 
                author              text        NOT NULL, 
                title               text        NOT NULL, 
                content             text        NOT NULL,
                liked_count         integer     DEFAULT 0,
                commented_count     integer     DEFAULT 0,
                collected_count     integer     DEFAULT 0,
                click_count         integer     DEFAULT 0,
                privacy             text,
                plate               text        DEFAULT "sharing",
                FOREIGN KEY(author) REFERENCES users(name))'''
    cur.execute(query)

    query = '''CREATE TABLE if not exists comments(
                author              text        NOT NULL,
                content             text        NOT NULL,
                commented_aid       integer     NOT NULL,
                floor               integer     NOT NULL,
                liked_count         integer     DEFAULT 0,
                PRIMARY KEY(commented_aid, floor),
                FOREIGN KEY(author) REFERENCES users(name),
                FOREIGN KEY(commented_aid) REFERENCES articles(id))'''
    cur.execute(query)

    query = '''CREATE TABLE if not exists follows(
                follower     text       NOT NULL,
                followed     text       NOT NULL,
                PRIMARY KEY(follower, followed),
                FOREIGN KEY(follower) REFERENCES users(name),
                FOREIGN KEY(followed) REFERENCES users(name))'''
    cur.execute(query)

    query = '''CREATE TABLE IF NOT EXISTS image(
            picture      BLOB       NOT NULL,
            identity     text       primary key ,
            FOREIGN KEY(identity) REFERENCES users(name))'''
    cur.execute(query)

    close_database(conn, cur)


# The following functions are deal with users.


def insert_user(username, password, email):
    ''' This function is to insert a user's username, password and email into the database. '''
    conn, cur = connect_database('database.sqlite')
    cur.execute("insert into users (name, password, email) values (?, ?, ?)", (username, password, email))
    close_database(conn, cur)


def check_username(username):
    ''' This function is to check whether the username exists or not, if it exists, it will return False. '''
    button = False
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.execute("SELECT name, password, email  from users")
    for row in cursor:
        if username == row[0]:
            button = True
    conn.close()
    return button


def get_password(username):
    """ This function is to return the password of the known username. """
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.execute("SELECT name, password, email  from users")
    password = "wrong user name."
    for row in cursor:
        if username == row[0]:
            password = row[1]
    conn.close()
    return str(password)


def change_password_in_database(username, new_password):
    """ This function is to change the password storaged in database. """
    conn, cur = connect_database('database.sqlite')
    cur.execute("UPDATE users SET password = ? where name = ?", (new_password, username))
    close_database(conn, cur)


def add_users_information(username, change_part, new_information):
    """ This function is to change the users' information such as major and birthday. """
    conn, cur = connect_database('database.sqlite')
    if change_part == "major":
        cur.execute("UPDATE users SET major = ? where name = ?", (new_information, username))
    if change_part == "birthday":
        cur.execute("UPDATE users SET birthday = ? where name = ?", (new_information, username))
    close_database(conn, cur)


# The following functions are deal with articles.


def insert_article_in_database(author, title, content, plate):
    """ This function is to insert an article's aid, author, title, and body into articles table.
        Then the article_count in users table of the author will be added 1. """
    conn, cur = connect_database('database.sqlite')
    cur.execute("insert into articles (author, title, content, plate) values (?, ?, ?, ?)", (author, title, content, plate))
    cur.execute("UPDATE users SET article_count = article_count + 1 WHERE name = '" + author + "'")
    close_database(conn, cur)


def delete_article_in_database(id):
    """ This function is to delete an article from the database.
        The related comments will be deleted.
        The article_count of the author will be minus 1.
        The comment_count of the comment authors will be minus. """
    conn, cur = connect_database('database.sqlite')
    id = str(id)
    cursor = cur.execute("SELECT * from articles where id =" + id)
    row = cursor.fetchall()[0]
    cur.execute("UPDATE users SET article_count = article_count - 1 where name = '" + row[1] + "'")
    cur.execute("DELETE from articles where id =" + id)
    close_database(conn, cur)


def change_article_in_database(id, new_title, new_content):
    """ This function is to change the title and content of an article. """
    conn, cur = connect_database('database.sqlite')
    id = str(id)
    cur.execute("UPDATE articles SET title = ?, content = ? where id = ?", (new_title, new_content, id))
    close_database(conn, cur)


def search_article(search_keywords):
    """ This function is to search the keywords and return the articles whose title contain it. """
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute(
        "SELECT * from articles where title like '%" + search_keywords + "%' ""OR content like '%" + search_keywords + "%'")
    return cursor.fetchall()


def search_author(username):
    """ This function is to search article which published by user"""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT * from articles where author like '%" + username + "%' ")
    return cursor.fetchall()


def search_user(username):
    """ This function is to search feature which published by user"""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT major ,birthday from users where name like '%" + username + "%' ")
    return cursor.fetchall()


def search_email(username):
    """ This function is to search users' email"""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT email from users where name = '" + username + "' ")
    return cursor.fetchall()[0][0]


def search_id_title(ids):
    """ This function is to search users' email"""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT * from articles where  id = '" + ids + "' ")
    return cursor.fetchall()[0][2]


def search_id_content(ids):
    """ This function is to search users' email"""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT * from articles where  id = '" + ids + "' ")
    return cursor.fetchall()[0][3]


# The following functions is to deal with follows.


def insert_follows(follower, followed):
    """ This function is to add a pair of follower and the user be followed in to the follows table.
        And change the follow count and follower count of them. """
    # follower就是关注者（给别人点关注的人），followed就是被关注者（被别人关注了的人）
    # follow count是关注人数（该用户关注了多少人），follower count是粉丝人数（该用户被多少人关注）
    conn, cur = connect_database('database.sqlite')
    cur.execute("insert into follows values (?, ?)", (follower, followed))
    cur.execute("UPDATE users SET follow_count = follow_count + 1 WHERE name = '" + follower + "'")
    cur.execute("UPDATE users SET follower_count = follower_count + 1 WHERE name = '" + followed + "'")
    close_database(conn, cur)


def delete_follows(follower, followed):
    """ This function is to delete a pair of follower and the user be followed from the follows table.
        And change the follow count and follower count of them. """
    conn, cur = connect_database('database.sqlite')
    cur.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (follower, followed))
    cur.execute("UPDATE users SET follow_count = follow_count - 1 WHERE name = '" + follower + "'")
    cur.execute("UPDATE users SET follower_count = follower_count - 1 WHERE name = '" + followed + "'")
    close_database(conn, cur)


def list_all_followed(username):
    """ This function is to list all the users that the username follow to. """
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT followed FROM follows where follower = '" + username + "'")
    list = []
    for row in cursor:
        list.append(row[0])
    return list


def list_all_follower(username):
    """ This function is to list all the users who follow the username. """
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT follower FROM follows where followed = '" + username + "'")
    list = []
    for row in cursor:
        list.append(row[0])
    return list


def check_follows(follower, followed):
    num = False
    for x in list_all_follower(followed):
        if x == follower:
            num = True
    return num


def search_id_author(ids):
    """ This function is to search users' email"""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT * from articles where  id = '" + ids + "' ")
    return cursor.fetchall()[0][1]


# For pictures


def convert_image_into_binary(filename):
    with open(os.path.dirname(__file__) + '/upload/' + filename, 'rb') as file:
        photo_image = file.read()
    return photo_image


def insert_image(user, image):
    image_database, data = connect_database('database.sqlite')
    insert_photo = convert_image_into_binary(image)
    data.execute("insert into image(identity, picture) values (?, ?)", (user, insert_photo))
    image_database.commit()
    image_database.close()
    os.remove(os.path.dirname(__file__) + '/upload/' + image)


def show_picture():
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT * from image ")
    picture = (cursor.fetchall()[0][0])
    img_stream = base64.b64encode(picture)
    s = img_stream.decode()
    return s


def search_user_picture(user):
    """this function is used to search one user's all pictures."""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT picture from image where identity = '" + user + "' ")
    return cursor.fetchall()


def delete_user_picture(user):
    conn, cur = connect_database('database.sqlite')
    cur.execute("DELETE FROM image where identity ='" + user + "' ")
    close_database(conn, cur)


def change_user_image(user, picture):
    delete_user_picture(user)
    insert_image(user, picture)


# The following functions are about comments.


def insert_comment(author, content, commented_aid):
    """ This function is to add a comment into database table comments.
        The author is the user who send this comment. commented_aid is the id of the article. """
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT commented_count FROM articles where id = " + str(commented_aid))
    floor = int(cursor.fetchone()[0]) + 1
    cur.execute("insert into comments (author, content, commented_aid, floor) values (?, ?, ?, ?)",
                (author, content, commented_aid, floor))
    cur.execute("UPDATE articles SET commented_count = commented_count + 1 WHERE id = " + str(commented_aid))
    close_database(conn, cur)


def delete_comment(commented_aid, floor):
    """ This function is to delete a comment. But the commented_count will not change. """
    # 评论删掉，但是这层楼就是“少了一层”也就是“怎么三楼之后就是五楼，四楼的人呢？”这样的，前后的楼层数不会变化。
    # 总楼数（该文章的总评论数）也不会变化。
    conn, cur = connect_database('database.sqlite')
    cur.execute("DELETE from comments where commented_aid = " + str(commented_aid) + " AND floor = " + str(floor))
    close_database(conn, cur)


def return_comments_of_article(commented_aid):
    """ This function is to return all the comments of the article."""
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT * FROM comments where commented_aid = " + str(commented_aid))
    return cursor.fetchall()


def change_plate(aid, plate):
    conn, cur = connect_database('database.sqlite')
    cur.execute("UPDATE articles SET plate = ? WHERE id = ?", (plate, aid))
    close_database(conn, cur)


def return_articles_of_plate(plate):
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT * from articles where plate like '%" + plate + "%' ")
    return cursor.fetchall()


def search_click_count(id):
    conn, cur = connect_database('database.sqlite')
    cursor = cur.execute("SELECT click_count FROM articles where id = " + id)
    return cursor.fetchall()[0][0]


def add_click_count(id):
    """ This function is to return click count of the article."""
    conn, cur = connect_database('database.sqlite')
    num = search_click_count(id)+1
    conn.execute("UPDATE articles SET click_count ="+str(num)+" where id= "+id)
    close_database(conn, cur)

def read_pictures(item):
    if len(search_user_picture(item)) > 0:
        p = 1
        pic = show_picture()
    else:
        p = 0
        pic = None
    return p, pic