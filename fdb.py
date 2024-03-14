from time import sleep
import json


class FDatabase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addPost(self, login, text, bigtext, photo_path):
        try:
            self.__cur.execute("""
            INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)""", (login, text, bigtext, photo_path))
            self.__db.commit()
        except Exception as ex:
            print(ex)
            return False

        return True

    def getPost(self, login):
        try:
            self.__cur.execute("""
                        SELECT text, bigtext, photo_post FROM posts WHERE login = ?""", (login, ))
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

    def addUser(self, name, email, login, hpsw, instagram=None, telegram=None, facebook=None, tik_tok=None, vk=None, youtube=None):
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
                INSERT INTO user VALUES(NULL, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, ?, ?)""", (name, email,
                                                                                             login, hpsw,
                                                                                             instagram, telegram,
                                                                                             facebook, tik_tok,
                                                                                             vk, youtube))
            self.__db.commit()
            return "Пользователь успешно добавлен"
        except Exception as ex:
            print(ex)

    def updateUser(self, user_id, name, email, login, instagram, telegram, facebook, tik_tok, vk, youtube):
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
            UPDATE user SET name = ?, email = ?, login = ?, instagram = ?, telegram = ?, facebook = ?, tik_tok = ?, 
            vk = ?, youtube = ?
            WHERE id = ?""", (name, email, login, instagram, telegram, facebook, tik_tok, vk, youtube, user_id))
        self.__db.commit()
        return True

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

    def getUserByTextSearch(self, text):
        text = text.lower()
        self.__cur.execute("SELECT name, login, avatar FROM user WHERE LOWER(name) = ? OR LOWER(login) = ?", (text, text))

        res = self.__cur.fetchall()
        posts = []
        if res:
            for row in reversed(res):
                user = {
                    'name': row[0],
                    'login': row[1],
                    'avatar': row[2],
                }
                posts.append(user)
        return posts

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

    def addCardBeat(self, login, photo_path, music_path, text, genre, bpm, energy, joy, mood, tags):
        try:
            self.__cur.execute("""
        INSERT INTO users_card VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (login, photo_path,
                                                                         music_path, text,
                                                                         genre, bpm, energy,
                                                                         joy, mood, tags))
            self.__db.commit()
        except Exception as ex:
            print(ex)

    def getCardBeat(self, data, colum):
        # try:
        self.__cur.execute(f"""
            SELECT photo_path, music_path, text_beat, 
                   bpm, genre, tags, 
                   user.login, user.name, energy, joy, mood 
            FROM users_card
            LEFT JOIN user ON user.login = users_card.login
            WHERE users_card.{colum} = ?""", (data,))
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
                    'tags': json.loads(row[5]),
                    'login': row[6],
                    'name': row[7],
                    'energy': row[8],
                    'joy': row[9],
                    'mood': row[10]
                }
                posts.append(post)
        return posts
        # except Exception as ex:
        #     print(ex)
        #
        #     return []

    def getNameTagsBeat(self):
        self.__cur.execute("""
            SELECT login FROM user
        """)
        user_logins = self.__cur.fetchall()

        self.__cur.execute("""
            SELECT text_beat, genre, tags, user.login, user.name 
            FROM users_card
            LEFT JOIN user ON user.login = users_card.login
        """)
        rows = self.__cur.fetchall()

        search_data = set()

        for login in user_logins:
            search_data.add(login['login'])

        if rows:
            for row in rows:
                # tags_list = json.loads(row['tags'])
                # for tag in tags_list:
                #     search_data.add(tag['value'])
                search_data.add(row['name'])
                search_data.add(row['genre'])
                search_data.add(row['login'])
                search_data.add(row['text_beat'])
        else:
            print("Данных нету")

        search_data = list(search_data)
        print(search_data)
        return search_data

    def getNewUsers(self):
        self.__cur.execute(f"""
            SELECT photo_path, music_path, text_beat, 
                   bpm, genre, tags, 
                   user.login, user.name, user.avatar 
            FROM users_card
            LEFT JOIN user ON user.login = users_card.login
            GROUP BY user.login  
            ORDER BY MAX(user.id) DESC 
            LIMIT 10 
        """)
        rows = self.__cur.fetchall()
        posts = []
        for row in rows:
            post = {
                'photo_path': row[0],
                'music_path': row[1],
                'text': row[2],
                'bpm': row[3],
                'genre': row[4],
                'tags': json.loads(row[5]),
                'login': row[6],
                'name': row[7],
                'avatar': row[8]
            }
            posts.append(post)
        print(posts)
        return posts

    def getCardBeatOnMainPageAll(self):
        self.__cur.execute(f"""
            SELECT photo_path, music_path, text_beat, 
                   bpm, genre, tags, 
                   user.login, user.name 
            FROM users_card
            LEFT JOIN user ON user.login = users_card.login""")
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
                    'tags': json.loads(row[5]),
                    'login': row[6],
                    'name': row[7]
                }
                posts.append(post)
        return posts


