import sqlite3
from time import sleep


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

    def updateUserAvatar(self, avatar, user_id, type_avatar):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"""
            UPDATE user SET {type_avatar} = ? WHERE id = ?""", (binary, user_id))
            self.__db.commit()
            sleep(1)
        except Exception as ex:
            print(ex)
            return False

        return True

    def addCardBeat(self, login, photo_path, music_path, text):
        try:
            self.__cur.execute("""
        INSERT INTO users_card VALUES(?, ?, ?, ?)""", (login, photo_path, music_path, text))
            self.__db.commit()
        except Exception as ex:
            print(ex)

    def getCardBeat(self, login):
        try:
            self.__cur.execute("""
            SELECT photo_path, music_path, text_beat FROM users_card WHERE login = ?""", (login,))
            rows = self.__cur.fetchall()
            posts = []
            if rows:
                for row in reversed(rows):
                    post = {
                        'photo_path': row[0],
                        'music_path': row[1],
                        'text': row[2]
                    }
                    posts.append(post)
            return posts
        except Exception as ex:
            print(ex)
            return []



