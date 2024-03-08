import sqlite3
from time import sleep
import json

class FDatabase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addPost(self, text, bigtext, photo_path):
        try:
            self.__cur.execute("""
            INSERT INTO posts VALUES(NULL, ?, ?, ?)""", (text, bigtext, photo_path))
            self.__db.commit()
        except Exception as ex:
            print(ex)
            return False

        return True

    def getPost(self):
        try:
            self.__cur.execute("""
                        SELECT text, bigtext, photo_post FROM posts""")
            rows = self.__cur.fetchall()
            posts = []
            if rows:
                for row in reversed(rows):
                    post = {
                        'text': row[0],
                        'bigtext': row[1],
                        'photo_path': row[2]
                    }
                    posts.append(post)
            print(posts)
            return posts
        except Exception as ex:
            print(ex)
        return []

    def addUser(self, name, email, login, hpsw):
        try:
            self.__cur.execute(f"""
                SELECT COUNT() as count FROM user WHERE email = '{email}'""")
            email_count = self.__cur.fetchone()['count']
            if email_count > 0:
                return 400

            self.__cur.execute(f"""
                SELECT COUNT() as count FROM user WHERE login = '{login}'""")
            login_count = self.__cur.fetchone()['count']
            if login_count > 0:
                return 401

            self.__cur.execute("""
                INSERT INTO user VALUES(NULL, ?, ?, ?, ?, NULL, NULL)""", (name, email, login, hpsw))
            self.__db.commit()
            return "Пользователь успешно добавлен"
        except Exception as ex:
            print(ex)

    def updateUser(self, user_id, name, email, login):
        try:
            self.__cur.execute(f"""
                            SELECT COUNT() as count FROM user WHERE email = '{email}' and id != '{user_id}'""")
            email_count = self.__cur.fetchone()['count']
            if email_count > 0:
                return 400

            self.__cur.execute(f"""
                            SELECT COUNT() as count FROM user WHERE login = '{login}' and id != '{user_id}'""")
            login_count = self.__cur.fetchone()['count']
            if login_count > 0:
                return 401

            self.__cur.execute("""
                UPDATE user SET name = ?, email = ?, login = ? WHERE id = ?""", (name, email, login, user_id))
            self.__db.commit()
            return True
        except Exception as ex:
            print(ex)
        return False

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"""
            SELECT * FROM user WHERE id = {user_id} LIMIT 1""")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except Exception as ex:
            print(ex)

        return False

    def getUserByLogin(self, login):
        self.__cur.execute(f"SELECT * FROM user WHERE login = '{login}' LIMIT 1")
        res = self.__cur.fetchone()
        if not res:
            print("Пользователь не найден")
            return False

        return res

    def updateUserAvatar(self, avatar, login, type_avatar):
        if not avatar:
            return False

        try:

            self.__cur.execute(f"""
            UPDATE user SET {type_avatar} = ? WHERE login = ?""", (avatar, login))
            self.__db.commit()
            sleep(1)
        except Exception as ex:
            print(ex)
            return False

        return True

    def addCardBeat(self, login, photo_path, music_path, text, genre, bpm, tags):
        try:
            self.__cur.execute("""
        INSERT INTO users_card VALUES(?, ?, ?, ?, ?, ?, ?)""", (login, photo_path, music_path, text, genre, bpm, tags))
            self.__db.commit()
        except Exception as ex:
            print(ex)

    def getCardBeat(self, data, colum):
        try:
            self.__cur.execute(f"""
            SELECT photo_path, music_path, text_beat, bpm, genre, tags FROM users_card WHERE {colum} = ?""", (data,))
            rows = self.__cur.fetchall()
            posts = []
            if rows:
                for row in reversed(rows):
                    post = {
                        'photo_path': row[0],
                        'music_path': row[1],
                        'text': row[2],
                        'bpm': row[3],
                        'genre': row[4],
                        'tags': json.loads(row[5])
                    }
                    posts.append(post)
            return posts
        except Exception as ex:
            print(ex)
            return []

    def getNameTagsBeat(self):

        self.__cur.execute("""
        SELECT name, login FROM user""")
        row = self.__cur.fetchall()
        search_data = []
        if row:
            for i in row:
                search_data.append((i['name'], i['login']))
        else:
            print("Данных нету")
        return search_data




